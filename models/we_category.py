# -*- coding: utf-8 -*-
from odoo import models, fields, api,_,tools
from .models import Model
import re
class WeProductCategory(Model):
    
    _inherit='product.category'
    _models={'pdt':'product.product','pdttpl':'product.template'}
    @tools.ormcache()
    def _get_default_length_uom_categ(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.uom_categ_length')
    @tools.ormcache()
    def _get_default_surface_uom_categ(self):
        # Deletion forbidden (at least through unlink)
        result= self.env.ref('weMetalProduct.uom_categ_surface')
        return result
    @tools.ormcache()
    def _get_default_weight_uom_categ(self):
        # Deletion forbidden (at least through unlink)
        result= self.env.ref('uom.product_uom_categ_kgm')
        return result
    surface_formula=fields.Char('Surface Formula',default='')
    volume_formula=fields.Char('Volume Formula',default='')
    weight_formula=fields.Char('Weight Formula',default='')
    
    convention=fields.Char('Convention',help="python regex string convention",default='')
    cattype=fields.Selection([('none','None'),('sheetmetal','Sheetmetal'),('profile','Profile')],default='none',string='Type')
    protype=fields.Selection([('none','None'),('standard','Standard'),('calculated','Calculated')],default='none',string="Profile",domain="[('cattype','=','profile')]")
    
    surface_uom=fields.Many2one('uom.uom','Surface Unit',required=True,domain="[('category_id','=',surface_uom_categ)]")
    surface_uom_categ=fields.Many2one('uom.category',default=_get_default_surface_uom_categ,store=False,readonly=True)

    length_uom=fields.Many2one('uom.uom','Length Unit',required=True,domain="[('category_id','=',length_uom_categ)]")
    length_uom_categ=fields.Many2one('uom.category',default=_get_default_length_uom_categ,store=False,readonly=True)


    weight_uom =fields.Many2one('uom.uom','Weight Unit',required=True,domain="[('category_id','=',weight_uom_categ)]")
    weight_uom_categ=fields.Many2one('uom.category',default=_get_default_weight_uom_categ,store=False,readonly=True)

    def update_product_weight(self):
        self.ensure_one()
        products = self.env['product.template'].search([('categ_id', 'child_of', self.ids)])
        for product in products:
            product.calculate_weight()
        title = _("Update product's weight!")
        message = _("Everything seems properly fine!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            }
        }
    @api.model
    def parse(self,convention,value,results):
        p = re.compile(convention,re.IGNORECASE)
        m = p.match(value)
        if m:
            if isinstance(results,dict):
                results.update(m.groupdict())
            return True
        return False