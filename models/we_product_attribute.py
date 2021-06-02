# -*- coding: utf-8 -*-
from odoo import fields,api
from .models import Model
from .we_settings import UOM_SURFACE,UOM_WEIGHT,UOM_LENGTH,UOM_VOLUMIC_MASS

class ProductAttribute(Model):
    _inherit = 'product.attribute'

    
    # def get_default_uom_domain(self):
    #     if self.display_type in ('dimension','thickness'):
    #         return [('category_id.id','=', self.get_param(UOM_LENGTH) )]
    #     return []
            
            
    display_type = fields.Selection( selection_add=[
        ('dimension','Dimension'),
        ('thickness','Thickness'),
        ('material','Material')], 
        ondelete={'dimension': 'cascade','thickness': 'cascade','material': 'cascade',})
    uom_domain_id=fields.Integer('uom domain id',compute='_compute_uom_domain_id')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.depends('display_type')
    def _compute_uom_domain_id(self):
        for record in self:
            record.uom_domain_id=record.get_param(UOM_LENGTH) if record.display_type in ('dimension','thickness') else 0

class ProductAttributeValue(Model):
    _inherit = 'product.attribute.value'
    """ 3 Dimensionnal abilities """
    length = fields.Float('Length',default=0.0)
    width = fields.Float('Width',default=0.0)
    thickness = fields.Float('Thickness',default=0.0)
    material = fields.Many2one('we.material','Material')
    volmass = fields.Float('Volumic mass',related='material.volmass')