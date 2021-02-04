# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError

class WeIndice(models.Model):
    _name='we.indice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Erp extensions'
    _order='date_to desc'
    _sql_constraints = [
        ('indice_uniq', 'unique (major,minor)', "Indice Major,Minor already exist !"),
    ]
    active = fields.Boolean('Active', default=True,help="If the active field is set to False, it will allow you to hide the indice without removing it.")
    major=fields.Char('Major',required=True)
    minor=fields.Char('Minor')
    date_from=fields.Date('From',required=True,default=datetime.date.today())
    date_to=fields.Date('To')
    state = fields.Selection(
        [('draft','Draft'),('current','Current'),('closed','Closed')],
        string='Status', default='draft',store=True,readonly=True,required=True,tracking=True)
    note = fields.Text('Description', help="Text indice description")
    product = fields.Many2one('product.template', 'Product', auto_join=True,ondelete='restrict')
    bom = fields.Many2one('mrp.bom', 'Bom', auto_join=True,ondelete='restrict')
    is_enable=fields.Boolean(compute='_compute_is_enabled')
    
    def name_get(self):
        return [(indice.id, '%s - Indice %s' % ( indice.product.display_name,'%s.%s' % (indice.major,indice.minor ) if indice.minor else '%s'%(indice.major) )) for indice in self]

    @api.constrains('date_from','date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to and  record.date_from>record.date_to:
                raise ValidationError(_('Date from cannot be most recent than date to'))
            # self.env['we.indice'].search_count([('product.id','=',record.product.id),('date_from','>',record.date_from)])
    @api.depends("date_from", "date_to")
    def _compute_is_enabled(self):
        today = datetime.date.today()
        for record in self:
            record.is_enable = True
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
        self.ensure_one()
        # if self.create_date==False:
        #     return 
        if not self.product.id:
            return False
        indices = self.env['we.indice'].search([('product.id','=',self.product.id)],order="date_to desc")
        if indices.exists() and not indices[0].date_to:
            return indices[0]
        elif indices.exists() and indices[-1]:
            return indices[-1]
        return False

    @api.onchange('product')
    def _on_product_changed(self):
        for record in self:
       
            last=record._get_last_indice()
            if not last:
                continue
            today=datetime.date.today()
            if last.exists() and not last.date_to:
                record.date_from=datetime.date.today()
            elif last.exists() and not last.date_to>today:
                record.date_from = last.date_to + datetime.timedelta(days=1)
            else:
                record.date_from=today
    
    @api.onchange('date_from', 'date_to')
    def _on_date_changed(self):
        # control date range within indices
        pass
    def write(self,values):
        res = super(WeIndice, self).write(values) 
        self._update_last_indices()
        return res

