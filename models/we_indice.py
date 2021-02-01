# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError
class WeIndice(models.Model):
    _name='we.indice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Erp extensions'
    _order='date_to desc'
    major=fields.Char('Major',required=True)
    minor=fields.Char('Minor')
    date_from=fields.Date('From',required=True,default=datetime.date.today())
    date_to=fields.Date('To')
    is_enabled = fields.Boolean("Enabled", compute="_compute_is_enabled")
    note = fields.Text('Description', help="Text indice description")
    product = fields.Many2one('product.template', 'Product', auto_join=True,ondelete='restrict')
    bom = fields.Many2one('mrp.bom', 'Bom', auto_join=True,ondelete='restrict')

    

    @api.depends("date_from", "date_to")
    def _compute_is_enabled(self):
        today = datetime.date.today()
        for record in self:
            if record.date_to and  record.date_from>record.date_to:
                raise UserError(_('Date from cannot be most recent than date to'))
            record.is_enabled = True
            if record.date_from:
                date_from = record.date_from
                if date_from > today:
                    record.is_enabled = False
            if record.date_to:
                date_to = record.date_to
                if today > date_to:
                    record.is_enabled = False

    @api.model
    def _update_last_indices(self):
        last = self._get_last_indice()
        today=datetime.date.today()
        yesterday=today - datetime.timedelta(days=1)
        update={'date_to':yesterday}
        if last.exists() and not last.date_to:
            last.update(update)
        elif last.exists() and last.date_to>today:
            last.update(update)
    
    @api.model
    def _get_last_indice(self):
        indices = self.env['we.indice'].search(['product.id','=',self.product.id],order="date_to desc")
        if indices.exists() and not indices[0].date_to:
            return indices[0]
        elif indices.exists() and indices[-1]:
            return indices[-1]
        return self.env['we.indice'].browse(-1)

    @api.onchange('product')
    def _on_product_changed(self):
        if not self.product.exists():
            return
        last=self._get_last_indice()
        today=datetime.date.today()
        if last.exists() and not last.date_to:
            self.date_from=datetime.date.today()
        elif last.exists() and not last.date_to>today:
            self.date_from = last.date_to + datetime.timedelta(days=1)
        else:
            self.date_from=today
    
    @api.onchange('date_from', 'date_to')
    def _on_date_changed(self):
        # control date range within indices
        pass
    def write(self,values):
        res = super(WeIndice, self).write(values) 
        self._update_last_indices()
        return res

