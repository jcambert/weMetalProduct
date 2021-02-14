# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import AccessError, UserError,ValidationError
from ast import literal_eval
import logging
import re
import math
class WeConvention(models.Model):
    _name='we.convention'
    _description='Convention RegEx searching'
    convention=fields.Char('Convention',help="python regex string convention")
    @api.onchange('convention')
    def on_convention_changed(self):
        if isinstance(self.convention,str):
            self.convention = str(self.name).strip()
        return