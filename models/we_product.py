# -*- coding: utf-8 -*-

from odoo import models, fields, api
class WeProduct(models.Model):
    _inherit = ['product.template']
    _description = 'Product Erp extensions'
     
    indices=fields.One2many('we.indice','product',string="Indice")
    current_indice = fields.Char('Current indice',compute='_compute_current_indice',readonly=True)


    def _compute_current_indice(self):
        def get_last_indice(record):
            # indices=self.env['we.indice'].search([('product.id','=',record.id)],order='date_to desc')
            indices=self.indices.sorted(lambda i:i.date_to,reverse=True)
            if indices.exists() and not indices[0].date_to:
                return indices[0]
            elif indices.exists() and indices[-1]:
                return indices[-1]
            else:
                return None

        for record in self:
            indice = get_last_indice(record)
            if indice:
                record.current_indice=f'{indice.major}.{indice.minor}'
            else:
                record.current_indice=''
    def action_view_indice(self):
        action = self.env["ir.actions.actions"]._for_xml_id("weOdooProduct.we_indice_action")
        action['domain'] = [ ('product', 'in', self.ids)]
        action['context'] = {}
        return action