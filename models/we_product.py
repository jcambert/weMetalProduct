# -*- coding: utf-8 -*-

from odoo import models, fields, api
class WeProduct(models.Model):
    _inherit = ['product.template']
    _description = 'Product Erp extensions'
     
    indices=fields.One2many('we.indice','product',string="Indice")
    current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)

    @api.depends('indices.is_enable')
    def _compute_current_indice(self):
        def get_last_indice(record):
            return self.indices.filtered(lambda i:i.is_enable)
            

        for record in self:
            indice = get_last_indice(record)
            record.current_indice= indice.name() if indice.exists() else ''
            
    def action_view_indice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("weOdooProduct.we_indice_action")
        action['domain'] = [ ('product', 'in', self.ids)]
        action['context'] = {}
        return action