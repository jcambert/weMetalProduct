# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import logging
import re
import math
_logger = logging.getLogger(__name__)

class WeProfileType(models.Model):
    _name='we.profile.type'
    _description='Standard Profile Type' #UPN HEA ..
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Type',required=True)
    default_length=fields.Integer('Default length',default=0.0)
    convention=fields.Char('Convention',required=True,help="python regex string convention")
    calculate_surface_section=fields.Char('Surface section formula',default='')
    calculate_surface_meter=fields.Char('Surface meter formula',default='')

class WeProfile(models.Model):
    _name='we.profile'
    _description='Standard Profile Dimension'
    _sql_constraints = [
        ('we_profile_name_uniq','unique(type_id,name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True,index=True)
    type_id=fields.Many2one('we.profile.type','Type',required=True)
    surface_section=fields.Float('Surface',default=0.0)
    surface_meter=fields.Float('Surface meter',default=0.0)
    weight_meter=fields.Float('Weight meter',default=0.0)

class WeSheetmetal(models.Model):
    _name='we.sheetmetal'
    _description='Standard sheetmetal dimension'
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"The name of this sheetmetal must be unique"),
    ]
    name=fields.Char('Name',required=True)
    length=fields.Float('Length')
    width=fields.Float('Width')
    convention=fields.Char('Convention',required=True,help="python regex string convention")
    
    @api.constrains('width','length')
    def _check_material_values(self):
        for record in self:
            if record and record.width<=0:
                raise ValidationError(_('Sheetmetal width must be greater than 0'))
            if record and record.length<=0:
                raise ValidationError(_('Sheetmetal length must be greater than 0'))

class WeMaterial(models.Model):
    _name='we.material'
    _description='Generic Material'
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]
    name=fields.Char('Name',required=True)
    volmass=fields.Float('Volumic Mass',required=True,help="in m3/Kg")
    convention=fields.Char('Convention',help="python regex string convention")
    default=fields.Boolean('Default',default=False)
    @api.constrains('volmass')
    def _check_volmass(self):
        for record in self:
            if record.volmass<=0:
                raise ValidationError(_('The volumic mass must be greater than zero'))


class WeProduct(models.Model):
    _inherit = ['product.template']
    _description = 'Product Erp extensions'
    _sql_constraints = [
        ('we_product_name_uniq','unique(name)',"This name already exist !")
    ]
    indices=fields.One2many('we.indice','product',string="Indice")
    current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)
    # current_indice=fields.Char('Current indice')
    material = fields.Many2one('we.material','Material')
    
    # is_sheetmetal=fields.Boolean(readonly=True,store=True,compute='_compute_type')
    is_sheetmetal=fields.Boolean(readonly=True,store=True)
    sheet_length = fields.Float('Length', digits='Product Unit of Measure', default=0.0)
    sheet_width=fields.Float('Width',digits='Product Unit of Measure', default=0.0)
    sheet_thickness=fields.Float('Thickness',digits='Product Unit of Measure', default=0.0)

    # is_profile=fields.Boolean(readonly=True,store=True,compute='_compute_type')
    is_profile=fields.Boolean(readonly=True,store=True)
    profile_length = fields.Integer('Profile length')
    profile_surface_section = fields.Float('Surface Section', digits='Product Unit of Measure', default=0.0)
    profile_surface_meter = fields.Float('Surface per meter', digits='Product Unit of Measure', default=0.0)
    profile_weight_meter = fields.Float('Weight per meter', digits='Product Unit of Measure', default=0.0)
    profile_thickness = fields.Float('Thickness', digits='Product Unit of Measure', default=0.0,help="thickness for tubes")
    surface=fields.Float('Surface',store=True,readonly=True,compute='_compute_material_values')
    weight=fields.Float('Weight',store=True,readonly=True,compute='_compute_material_values')

    @api.depends('indices.is_enable')
    def _compute_current_indice(self):
        def get_last_indice(record):
            return record.indices.filtered(lambda i:i.is_enable)
            
        for record in self:
            indice = get_last_indice(record)
            record.current_indice= indice.name() if indice.exists() else ''

    def _filterByRe(self,*args):
        if len(args) not in [2,3]:
            return False
        convention,name,res=args[0],args[1],args[2] if len(args)==3 else None
        if(len(convention)==0 or len(name)==0):
            return False
        _logger.info(f"Filtering: Convention->{convention} , name->{name}")
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(name)
        if m:
            if isinstance(res,dict):
                res.update(m.groupdict())
            return True
        return False
    @api.model
    def compute_is_sheetmetal(self,sheetmetals,sheetmetal_id,materials,clear_cat=False,clear_name=False):
        self.ensure_one()
        if not self.categ_id.id:
            self.is_sheetmetal=False
            return
        self.is_sheetmetal = self.categ_id.id ==  literal_eval( sheetmetal_id) if isinstance(sheetmetal_id,str)  else sheetmetal_id
        if not self.is_sheetmetal:
            return
        
        
        groups={}
        sheetmetal=sheetmetals.filtered(lambda r:self._filterByRe(r.convention,self.name,groups))
        
        if sheetmetal.exists():
            if clear_name or clear_cat:
                self.sheet_length=0
                self.sheet_width=0
                self.sheet_thickness=0.0
            self.sheet_length= self.sheet_length if self.sheet_length>0 else sheetmetal[0].length
            self.sheet_width= self.sheet_width if self.sheet_width>0 else sheetmetal[0].width
            if 'name' in groups:
                material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['name']))
                if material.exists() :# material.ensure_one():
                    self.material=material[0]
            if 'value' in groups:
                self.sheet_thickness=float(groups['value'])

    @api.model
    def compute_is_profile(self,profiles,profile_ids,profile_types,materials,clear_cat=False,clear_name=False):
        self.ensure_one()
        if not self.categ_id.id:
            self.is_profile=False
            return
        self.is_profile = self.categ_id.id in literal_eval(profile_ids) if isinstance(profile_ids,str)  else profile_ids
        if self.is_profile:
            groups={}
            profile=profiles.filtered(lambda r:self._filterByRe(r.type_id.convention,self.name,groups))
            if profile.exists():
                try:
                    p = re.compile(profile[0].type_id.convention)
                    m = p.match(self.name)
                    value=m.groupdict()['value']
                    print('value: %s' %(value))
                    candidate=profile.filtered(lambda r:r.name==value)
                    if candidate.exists():
                        self.profile_length=self.profile_length if self.profile_length>0 else profile.type_id.default_length
                        self.profile_surface_section= self.profile_surface_section if self.profile_surface_section>0 else candidate[0].surface_section
                        self.profile_surface_meter= self.profile_surface_meter if self.profile_surface_meter>0 else candidate[0].surface_meter 
                        self.profile_weight_meter=self.profile_weight_meter if self.profile_weight_meter>0 else candidate[0].weight_meter
                        # record.material set to acier
                    if 'material' in groups:
                        material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['material']))
                        if material.exists() :
                            self.material=material[0]
                    else:
                        material=materials.filtered(lambda r:r.default)
                        if material.exists() :
                            self.material=material[0]

                    if 'thickness' in groups:
                        self.profile_thickness=float(groups['thickness'])
                except:
                    raise
                    # pass
            # non standard declined profile
            else:
                groups={}
                profile=profile_types.filtered(lambda r:self._filterByRe(r.convention,self.name,groups))
                if profile.exists() and profile.ensure_one():
                    thickness=0.0
                    if clear_name or clear_cat:
                        pass
                    self.profile_length=int(profile.default_length)
                    if 'thickness' in groups:
                        thickness=self.profile_thickness=float(groups['thickness'])
                    if 'material' in groups:
                        material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['material']))
                        if material.exists() :
                            self.material=material[0]
                    else:
                        material=materials.filtered(lambda r:r.default)
                        if material.exists() :
                            self.material=material[0]
                    if len(profile.calculate_surface_section)>0:
                        try:
                            code=compile(profile.calculate_surface_section, "<string>", "eval")
                            self.surface_section=float(eval(code))
                        except:
                            raise
                    if len(profile.calculate_surface_meter)>0:
                        try:
                            code=compile(profile.calculate_surface_meter, "<string>", "eval")
                            self.surface_meter=float(eval(code))
                        except:
                            raise
                    


    @api.onchange('categ_id','name')
    def _compute_type(self):
        sheetmetal_id = self.env['ir.config_parameter'].get_param('weOdooProduct.sheetmetal_category') or False
        profile_ids = self.env['ir.config_parameter'].get_param('weOdooProduct.profile_categories') or []
        sheetmetals=self.env['we.sheetmetal'].search([])
        profile_types=self.env['we.profile.type'].search([])
        profiles=self.env['we.profile'].search([])

        materials=self.env['we.material'].search([])
        clear_product_on_category_change=self.env['ir.config_parameter'].get_param('weOdooProduct.clear_product_on_category_change')
        clear_product_on_name_change=self.env['ir.config_parameter'].get_param('weOdooProduct.clear_product_on_name_change')

        for record in self:
            clear_cat=clear_product_on_category_change and record.categ_id.id!=record._origin.categ_id.id
            clear_name=clear_product_on_name_change and record.name!=record._origin.name
            record.compute_is_sheetmetal(sheetmetals,sheetmetal_id,materials,clear_cat,clear_name)
            record.compute_is_profile(profiles,profile_ids,profile_types,materials,clear_cat,clear_name)
            
    @api.depends('sheet_width','sheet_length','sheet_thickness','material','profile_surface_meter','profile_weight_meter','profile_length')
    def _compute_material_values(self):
        for record in self:
            if record.is_sheetmetal:
                record.surface=record.sheet_width*record.sheet_length
                if record.material:
                    record.weight=(record.surface*record.sheet_thickness*record.material.volmass)/1000000
                record.surface/=1000000
            elif record.is_profile:
                record.surface=record.profile_surface_meter*record.profile_length
                record.weight=record.profile_weight_meter*record.profile_length

    @api.constrains('sheet_width')
    def _check_sheetmetal_width(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.sheet_width<=0:
                raise ValidationError(_('Sheetmetal width must be greater than 0'))

    @api.constrains('sheet_length')
    def _check_sheetmetal_length(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.sheet_length<=0:
                raise ValidationError(_('Sheetmetal length must be greater than 0'))
            
    @api.constrains('sheet_thickness')
    def _check_sheetmetal_thickness(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.sheet_thickness<=0:
                raise ValidationError(_('Sheetmetal thickness must be greater than 0'))

    @api.constrains('profile_length')
    def _check_profile_length(self):
        if any( record.is_profile and record.profile<=0 for record in self):
            raise ValidationError(_('Profile length must be greater than 0'))
            


    def action_view_indice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("weOdooProduct.we_indice_action")
        action['domain'] = [ ('product', 'in', self.ids)]
        action['context'] = {}
        return action