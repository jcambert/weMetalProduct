# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError

class WeIndice(models.Model):
    _name='we.indice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product Erp extensions'
    _order='date_from desc'
    _sql_constraints = [
        ('date_uniq','unique(product_id,date_from)',"There is another indice with this date !"),
        ('indice_uniq', 'unique (product_id,major,minor)', "Indice Major,Minor already exist !"),
    ]
    active = fields.Boolean('Active', default=True,help="If the active field is set to False, it will allow you to hide the indice without removing it.")
    major=fields.Char('Major',required=True)
    minor=fields.Char('Minor')
    date_from=fields.Date('From',required=True,default=datetime.date.today())
    # date_to=fields.Date('To')
    state = fields.Selection(
        [('draft','Draft'),('current','Current'),('closed','Closed')],
        string='State',
        default='draft',
        copy=False,required=True,help="Statut",tracking=True,store=True
        )
    note = fields.Text('Description', help="Text indice description")
    product = fields.Many2one('product.template', 'Product', auto_join=True,ondelete='restrict',required=True)
    bom = fields.Many2one('mrp.bom', 'Bom', auto_join=True,ondelete='restrict')
    is_enable=fields.Boolean(compute='_compute_is_enabled',default=False, store=True,tracking=True)
    # can_start_indice=fields.Boolean("can start indice",default=True,compute="_compute_can_start_indice")
    
    def name_get(self):
        # return [(indice.id, '%s / %s' % (self.product.display_name, '%s.%s' % (indice.major,indice.minor ) if indice.minor else '%s'%(indice.major) )) for indice in self]
        return [(indice.id, '%s / %s' % (self.product.display_name, indice.name() ) ) for indice in self]

    @api.model
    def name(self):
        self.ensure_one()
        return '%s' % ( '%s.%s' % (self.major,self.minor ) if self.minor else '%s'%(self.major) )
    # @api.constrains('date_from')
    # def _check_dates(self):
    #     for record in self:
    #         if record.date_to and  record.date_from>record.date_to:
    #             raise ValidationError(_('Date from cannot be most recent than date to'))
            
    # @api.depends("date_from", "date_to")
    # def _compute_is_enabled(self):
    #     today = datetime.date.today()
    #     for record in self:
    #         record.is_enable = True
    #         if record.date_from:
    #             date_from = record.date_from
    #             if date_from > today:
    #                 record.is_enabled = False
    #         if record.date_to:
    #             date_to = record.date_to
    #             if today > date_to:
    #                 record.is_enabled = False
    # @api.depends('state')
    # def _compute_can_start_indice(self):
    #     for record in self:
    #         # record.allow_start_revision=
    #         record.can_start_indice = (record.state=='draft' and record.create_date!=False)

    @api.depends('date_from')
    def _compute_is_enabled(self):
        records=self.env['we.indice'].search([('product.id','=',self.product.id)]).sorted(lambda r:r.date_from,reverse=True)
        if not records.exists():
            return 
        today=datetime.date.today()
        candidates=records.filtered(lambda r:r.date_from<=today)
        futures=records.filtered(lambda r:r.date_from>today)

        for record in futures:
            record.is_enable=False
            record.state='draft'
        for index,record in enumerate(candidates):
            if index==0:
                record.is_enable=True
                record.state='current'
            else:
                record.is_enable=False
                record.state='closed'
            # record.is_enable=record.state in ['current'] and record.date_from<=today
    
    # @api.onchange('is_enable')
    # def _on_state_change(self):
    #     self.ensure_one()
    #     if not self.product.exists():
    #         return
    #     if self.state=='draft':
    #         return
    #     if self.state == 'current':
    #         others=self.env['we.indice'].search([('product.id','=',self.product.id),('id','!=',self.id),('state','=','current')],order="date_from desc")
    #         for other in others:
    #             other.state='closed'

    # @api.model
    # def _update_last_indices(self):
    #     last = self._get_last_indice()
    #     today=datetime.date.today()
    #     yesterday=today - datetime.timedelta(days=1)
    #     update={'date_to':yesterday}
    #     if last.exists() and not last.date_to:
    #         last.update(update)
    #     elif last.exists() and last.date_to>today:
    #         last.update(update)
    
    @api.model
    def get_last_indice(self,is_enable=True):
        result= self.env['we.indice'].search([('product.id','=',self.product.id),('is_enable','=',is_enable)])
        return result[0] if result.exists() else None
    

    # @api.onchange('product')
    # def _on_product_changed(self):
    #     for record in self:
       
    #         last=record._get_last_indice()
    #         if not last.exists():
    #             continue
    #         today=datetime.date.today()
    #         if last.exists() and not last.date_to:
    #             record.date_from=datetime.date.today()
    #         elif last.exists() and not last.date_to>today:
    #             record.date_from = last.date_to + datetime.timedelta(days=1)
    #         else:
    #             record.date_from=today
    
    # def unlink(self):
        
    # def write(self,values):
    #     res = super(WeIndice, self).write(values) 
    #     self._update_last_indices()
    #     return res

    def _action_follow(self,record):
        action = self.env["ir.actions.actions"]._for_xml_id("weOdooProduct.we_indice_action_none")

        # action['context'] = {'id':record.id}
        action['res_id'] =record.id
        # action['view_mode']='form'
        action['views'] = [(self.env.ref('weOdooProduct.we_indice_form_view').id, 'form')]
        return action
    def _increment_int_value(self,value,step):
        return int(value)+step
    def _increment_char_value(self,value,step):
        lower=range(97,121)
        upper=range(65,89)

        c=ord(value[-1])
        if c in lower or c in upper:
            c+=1
        
        return '%s%s' %(value[:-1],chr(c))

    def action_start_indice(self):
        self.ensure_one()
        self.state='current'

    def action_add_major(self):
        return self._action_add()
        
        
    def action_add_minor(self):
        return self._action_add('minor')
        

    def _action_add(self,gender='major',step=1):
        def _copy(record,value,date=None):
            # if not date:
            #     last=record.get_last_indice()
            #     date = last.date_from+datetime.timedelta(days=1) if last  else None
            datas={gender:value,'date_from':date or datetime.date.today()}
            if gender=='major':
                datas['minor']=''
            copy=super(WeIndice,self).copy(datas)
            
            return copy
        self.ensure_one()
        value=None
        target=getattr(self,gender)
        try:
            value=self._increment_int_value(target if len(target)>0 else 0,step)
        except:
            value=None
        if not value:
            try:
                value=self._increment_char_value(target,step)
            except:
                value=None
        
        if value:
            return self._action_follow( _copy(self,value))