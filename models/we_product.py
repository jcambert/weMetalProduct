# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import re
# from weOdooProduct.helpers import inlist
class WeProfileType(models.Model):
    _name='we.profile.type'
    _description='Standard Profile Type' #UPN HEA ..
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Type',required=True)
    convention=fields.Char('Convention',required=True,help="python regex string convention")

class WeProfile(models.Model):
    _name='we.profile'
    _description='Standard Profile Dimension'
    _sql_constraints = [
        ('we_profile_name_uniq','unique(type_id,name)',"The name of this profile type must be unique"),
    ]
    name=fields.Char('Name',required=True,index=True)
    type_id=fields.Many2one('we.profile.type','Type',required=True)
    surface_section=fields.Float('Surface')
    surface_meter=fields.Float('Surface meter')
    weight_meter=fields.Float('Weight meter')

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

    @api.constrains('volmass')
    def _check_volmass(self):
        for record in self:
            if record.volmass<=0:
                raise ValidationError(_('The volumic mass must be greater than zero'))


class WeProduct(models.Model):
    _inherit = ['product.template']
    _description = 'Product Erp extensions'
     
    indices=fields.One2many('we.indice','product',string="Indice")
    current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)
    # current_indice=fields.Char('Current indice')
    material = fields.Many2one('we.material','Material')
    
    is_sheetmetal=fields.Boolean(readonly=True,store=True,compute='_compute_type')
    sheet_length = fields.Float('Length', digits='Product Unit of Measure', default=0.0)
    sheet_width=fields.Float('Width',digits='Product Unit of Measure', default=0.0)
    sheet_thickness=fields.Float('Thickness',digits='Product Unit of Measure', default=0.0)

    is_profile=fields.Boolean(readonly=True,store=True,compute='_compute_type')
    profile_length = fields.Integer('Profile length')
    profile_surface_section = fields.Float('Surface Section', digits='Product Unit of Measure', default=0.0)
    profile_surface_meter = fields.Float('Surface per meter', digits='Product Unit of Measure', default=0.0)
    profile_weight_meter = fields.Float('Weight per meter', digits='Product Unit of Measure', default=0.0)

    surface=fields.Float('Surface',store=True,readonly=True,compute='_compute_material_values')
    weight=fields.Float('Weight',store=True,readonly=True,compute='_compute_material_values')

    @api.depends('indices.is_enable')
    def _compute_current_indice(self):
        def get_last_indice(record):
            return record.indices.filtered(lambda i:i.is_enable)
            
        for record in self:
            indice = get_last_indice(record)
            record.current_indice= indice.name() if indice.exists() else ''

    @api.depends('categ_id','name')
    def _compute_type(self):
        sheetmetal_id = self.env['ir.config_parameter'].get_param('weOdooProduct.sheetmetal_category') or False
        profile_ids = self.env['ir.config_parameter'].get_param('weOdooProduct.profile_categories') or []
        sheetmetals=self.env['we.sheetmetal'].search([])
        profiles=self.env['we.profile'].search([])

        def _compute_sheetmetal(record):
            if not record.is_sheetmetal:
                return
            sheetmetal=sheetmetals.filtered(lambda r:re.search(r.convention, record.name, re.IGNORECASE))
            if sheetmetal.exists():
                record.sheet_length= record.sheet_length if record.sheet_length>0 else sheetmetal[0].length
                record.sheet_width= record.sheet_width if record.sheet_width>0 else sheetmetal[0].width

        def _compute_profile(record):
            if not record.is_profile:
                return
            profile=profiles.filtered(lambda r:re.search(r.type_id.convention,record.name,re.IGNORECASE))
            if profile.exists():
                try:
                    p = re.compile(profile[0].type_id.convention)
                    m = p.match(record.name)
                    value=m.groupdict()['value']
                    # name=m.groupdict['name']
                    print('value: %s' %(value))
                    candidate=profile.filtered(lambda r:r.name==value)
                    if candidate.exists():
                        record.profile_surface_section= record.profile_surface_section if record.profile_surface_section>0 else candidate[0].surface_section
                        record.profile_surface_meter= record.profile_surface_meter if record.profile_surface_meter>0 else candidate[0].surface_meter 
                        record.profile_weight_meter=record.profile_weight_meter if record.profile_weight_meter>0 else candidate[0].weight_meter
                        # record.material set to acier
                except:
                    pass

        for record in self:
            record.is_sheetmetal = record.categ_id.id ==  literal_eval( sheetmetal_id) if isinstance(sheetmetal_id,str)  else sheetmetal_id
            _compute_sheetmetal(record)
            if not record.is_sheetmetal:
                record.is_profile = record.categ_id.id in literal_eval(profile_ids) if isinstance(sheetmetal_id,str)  else sheetmetal_id
                _compute_profile(record)

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
        for record in self:
            if not record.is_profile:
                continue
            if record and record.profile_length<=0:
                raise ValidationError(_('Profile length must be greater than 0'))
            


    def action_view_indice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("weOdooProduct.we_indice_action")
        action['domain'] = [ ('product', 'in', self.ids)]
        action['context'] = {}
        return action