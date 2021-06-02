# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import logging
import re
import math
_logger = logging.getLogger(__name__)
   
class WeProduct(models.Model):
    _inherit = ['product.template']
    _description = 'Product Erp extensions'
    _sql_constraints = [
        ('we_product_name_uniq','unique(name)',"This name already exist !")
    ]
    indices=fields.One2many('we.indice','product',string="Indice")
    current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)
    state = fields.Selection(
        [('draft','Draft'),('running','running'),('closed','Closed')],
        string='State',
        default='draft',
        copy=False,required=True,help="Statut",tracking=True,store=True)
    material = fields.Many2one('we.material','Material')
    finition = fields.Char('Finition',default='')
    is_sheetmetal=fields.Boolean()

    profile_type=fields.Many2one('we.profile.type')
    is_profile=fields.Boolean('Is profile')
    is_predefined_profile=fields.Boolean('Is predefined profile')
    profile_length = fields.Integer('Profile length')
    surface_section = fields.Float('Surface Section', digits='Product Unit of Measure', default=0.0)
    surface_meter = fields.Float('Surface per meter', digits='Product Unit of Measure', default=0.0)
    weight_meter = fields.Float('Weight per meter', digits='Product Unit of Measure', default=0.0)

    surface=fields.Float('Surface',store=True,compute='_compute_material_values', digits='Product Unit of Measure',default=0.0)
    weight=fields.Float('Weight',store=True,compute='_compute_material_values', digits='Product Unit of Measure',default=0.0)

    dim1=fields.Float('dim1',digits='Product Unit of Measure',default=0.0)#length, external diameter
    dim2=fields.Float('dim2',digits='Product Unit of Measure',default=0.0)#Width, external diameter
    dim3=fields.Float('dim3',digits='Product Unit of Measure',default=0.0)#Length, internal diameter
    dim4=fields.Float('dim4',digits='Product Unit of Measure',default=0.0)#Width, internal diameter
    dim5=fields.Float('dim5',digits='Product Unit of Measure',default=0.0)#thickness

    @api.onchange('name')
    def set_upper(self):    
        if isinstance(self.name,str):
            force=self.env['ir.config_parameter'].get_param('weMetalProduct.product_name_force_uppercase')
            self.name = str(self.name).upper() if force else str(self.name)
        return


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
        if(not convention or not name or len(convention)==0 or len(name)==0):
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
    def compute_is_profile(self,profiles,profile_ids,sheetmetal_id,profile_types,materials,clear_cat=False,clear_name=False):
        self.ensure_one()
        if not self.categ_id.id:
            self.is_profile=False
            return
        self.is_profile = self.categ_id.id in literal_eval(profile_ids) if isinstance(profile_ids,str)  else profile_ids
        self.is_sheetmetal = self.categ_id.id ==  literal_eval( sheetmetal_id) if isinstance(sheetmetal_id,str)  else sheetmetal_id

        if not self.is_profile and not self.is_sheetmetal:
            return
        groups={}
        profile=profiles.filtered(lambda r:self._filterByRe(r.type_id.convention,self.name,groups))
        if profile.exists() and profile.ensure_one():
            self.is_predefined_profile=True
            self.profile_type=profile
            try:
                p = re.compile(profile.type_id.convention)
                m = p.match(self.name)
                value=m.groupdict()['value']
                print('value: %s' %(value))
                candidate=profile.filtered(lambda r:r.name==value)
                if candidate.exists():
                    self.profile_length=self.profile_length if self.profile_length>0 else profile.type_id.default_length
                    self.surface_section= self.surface_section if self.surface_section>0 else candidate[0].surface_section
                    self.surface_meter= self.surface_meter if self.surface_meter>0 else candidate[0].surface_meter 
                    self.weight_meter=self.weight_meter if self.weight_meter>0 else candidate[0].weight_meter
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
                    self.dim5=float(groups['thickness'])
            except:
                raise
                # pass
        # non standard declined profile
        else:
            self.is_predefined_profile=False
            groups={}
            profile=profile_types.filtered(lambda r:self._filterByRe(r.convention,self.name,groups))
            if profile.exists() and profile.ensure_one():
                self.profile_type=profile
                if clear_name or clear_cat:
                    self.profile_length=0
                    self.dim1=self.dim2=self.dim3=self.dim4=self.dim5=0.0
                thickness=0.0
                value=value_one=value_two=0
                self.profile_length= self.profile_length if self.profile_length>0 else int(profile.default_length)
                if self.is_sheetmetal:
                    value=value_one=self.dim1= self.dim1 if self.dim1>0 else profile.length
                    value_two=self.dim2= self.dim2 if self.dim2>0 else profile.width
                elif 'value' in groups:
                    value=self.dim1=int(groups['value'])
                if 'value_one' in groups:
                    value_one=self.dim1=int(groups['value_one'])
                if 'value_two' in groups:
                    value_two=self.dim2=int(groups['value_two'])
                if 'thickness' in groups:
                    thickness=self.dim5=self.dim5 if self.dim5>0 else float(groups['thickness'])
                    # self.dim2=self.dim1-2*self.dim5
                if 'material' in groups:
                    material=materials.filtered(lambda r:self._filterByRe(r.convention,groups['material']))
                    if material.exists() :
                        self.material=material[0]
                else:
                    material=materials.filtered(lambda r:r.default)
                    if material.exists()  :
                        self.material=material[0]
                if 'finition' in groups:
                    self.finition=groups['finition']
                self._update_non_standard_profile_values()
                    # self.update({'dim1':self.dim1,'dim2':self.dim2,'dim5':self.dim5})

    @api.onchange('dim5')
    def _on_dim5_changed(self):
        # profile_types=self.env['we.profile.type'].search([])
        for record in self.filtered(lambda r:not r.is_predefined_profile and r.profile_type):
            # profile=profile_types.filtered(lambda r:record._filterByRe(r.convention,record.name))
            # if profile.exists() and profile.ensure_one():
            record._update_non_standard_profile_values()
    @api.model
    def _update_non_standard_profile_values(self):
        record=self
        value=value_one=record.dim1
        thickness=record.dim5
        profile=record.profile_type
        if len(profile.calculate_dim2)>0:
            try:
                code=compile(profile.calculate_dim2, "<string>", "eval")
                value_two=record.dim2=float(eval(code))
            except:
                value_two=0
                raise
        else:
            value_two=record.dim2
        if len(profile.calculate_dim3)>0:
            try:
                code=compile(profile.calculate_dim3, "<string>", "eval")
                record.dim3=float(eval(code))
            except:
                raise
        if len(profile.calculate_dim4)>0:
            try:
                code=compile(profile.calculate_dim4, "<string>", "eval")
                record.dim4=float(eval(code))
            except:
                raise
        if len(profile.calculate_surface_section)>0:
            try:
                code=compile(profile.calculate_surface_section, "<string>", "eval")
                record.surface_section=float(eval(code))
            except:
                raise
        if len(profile.calculate_surface_meter)>0:
            try:
                code=compile(profile.calculate_surface_meter, "<string>", "eval")
                record.surface_meter=float(eval(code))
            except:
                raise
        record.weight_meter=record.surface_section*record.material.volmass

    @api.onchange('categ_id','name')
    def _compute_type(self):
        sheetmetal_id = self.env['ir.config_parameter'].get_param('weMetalProduct.sheetmetal_category') or False
        profile_ids = self.env['ir.config_parameter'].get_param('weMetalProduct.profile_categories') or []
        # sheetmetals=self.env['we.sheetmetal'].search([])
        profile_types=self.env['we.profile.type'].search([])
        profiles=self.env['we.profile'].search([])

        materials=self.env['we.material'].search([])
        clear_product_on_category_change=self.env['ir.config_parameter'].get_param('weMetalProduct.clear_product_on_category_change')
        clear_product_on_name_change=self.env['ir.config_parameter'].get_param('weMetalProduct.clear_product_on_name_change')

        for record in self:
            clear_cat=clear_product_on_category_change and record.categ_id.id!=record._origin.categ_id.id
            clear_name=clear_product_on_name_change and record.name!=record._origin.name
            # record.compute_is_sheetmetal(profiles,sheetmetal_id,materials,clear_cat,clear_name)
            record.compute_is_profile(profiles,profile_ids,sheetmetal_id,profile_types,materials,clear_cat,clear_name)
            
    @api.depends('dim2','dim1','dim5','material','surface_meter','weight_meter','profile_length')
    def _compute_material_values(self):
        for record in self.filtered(lambda r:r.is_sheetmetal):
            record.surface=record.dim2*record.dim1
            if record.material:
                record.weight=(record.surface*record.dim5*record.material.volmass)/1000000
            record.surface/=1000000
        for record in self.filtered(lambda r:r.is_profile):
                record.surface=record.surface_meter*record.profile_length
                record.weight=record.weight_meter*record.profile_length
        
            # record.surface=0.0
            # record.weight=0.0
    @api.constrains('dim2')
    def _check_sheetmetal_width(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim2<=0:
                raise ValidationError(_('Sheetmetal width must be greater than 0'))

    @api.constrains('dim1')
    def _check_sheetmetal_length(self):
        for record in self:
            if not record.is_sheetmetal:
                continue
            if record and record.dim1<=0:
                raise ValidationError(_('Sheetmetal length must be greater than 0'))
            
    @api.constrains('dim5')
    def _check_sheetmetal_thickness(self):
        if any( record.is_sheetmetal and record.dim5<=0 for record in self):
            raise ValidationError(_('Sheetmetal thickness must be greater than 0'))
        #thickness profile can be 0 

    @api.constrains('profile_length')
    def _check_profile_length(self):
        if any( record.is_profile and record.profile_length<=0 for record in self):
            raise ValidationError(_('Profile length must be greater than 0'))
            


    def action_view_indice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("weMetalProduct.we_indice_action")
        action['domain'] = [ ('product', 'in', self.ids)]
        action['context'] = {}
        return action