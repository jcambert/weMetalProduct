# -*- coding: utf-8 -*-
from odoo import fields,api,tools
from .models import Model
from .we_settings import UOM_SURFACE,UOM_WEIGHT,UOM_LENGTH,UOM_VOLUMIC_MASS

class ProductAttribute(Model):
    _inherit = 'product.attribute'

    @tools.ormcache()
    def _get_default_length_category_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.uom_categ_length')

    @tools.ormcache()
    def _get_default_unit_category_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.product_uom_categ_unit')

    @api.depends('display_type')
    def _compute_uom_category(self):
        for record in self:
            if record.display_type in ('sheetmetalsize','profilelength','thickness'):
                record.uom_domain_id= record._get_default_length_category_id()
                # return [('category_id.id','=', self.env.ref('uom_categ_length').id  )]
            else:
                record.uom_domain_id= record._get_default_unit_category_id()
            
            
    display_type = fields.Selection( selection_add=[
        ('sheetmetalsize','Format tole'),
        ('profilelength','Profile Length'),
        ('thickness','Thickness'),
        ('material','Material')], 
        ondelete={'sheetmetalsize': 'cascade','profilelength':'cascade','thickness': 'cascade','material': 'cascade',})
    uom_domain_id=fields.Many2one('uom.category','Uom category',compute='_compute_uom_category')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    
    @api.depends('display_type')
    def _compute_uom_domain_id(self):
        for record in self:
            record.uom_domain_id=record.get_param(UOM_LENGTH) if record.display_type in ('sheetmetalsize','profilelength','thickness') else 0

class ProductAttributeValue(Model):
    _inherit = 'product.attribute.value'
    """ 3 Dimensionnal abilities """
    length = fields.Float('Length',default=0.0)
    width = fields.Float('Width',default=0.0)
    thickness = fields.Float('Thickness',default=0.0)
    material = fields.Many2one('we.material','Material')
    volmass = fields.Float('Volumic mass',related='material.volmass')
    code_suffixe=fields.Char('Code suffixe',default='')