# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

from itertools import groupby


class WeBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = ['mrp.bom']

    indices=fields.One2many('we.indice','bom',string="Bom")