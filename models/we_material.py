# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import logging
import re
import math

class WeMaterial(models.Model):
    _name='we.material'
    _description='Generic Material'
    _inherit=['we.convention']
    _order='name'
    _sql_constraints = [
        ('name_uniq','unique(name)',"This name already exist !")
    ]
    name=fields.Char('Name',required=True)
    volmass=fields.Float('Volumic Mass',required=True,help="in m3/Kg")
    default=fields.Boolean('Default',default=False)

    @api.constrains('volmass')
    def _check_volmass(self):
        if any( record.volmass<=0 for record in self):
            raise ValidationError(_('The volumic mass must be greater than zero'))