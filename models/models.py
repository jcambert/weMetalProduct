from odoo import models, fields, api,_
from ast import literal_eval as _literal_eval
from . import models as _inner_models
from .we_settings import SHEETMETAL_CATEGORY, UOM_SURFACE,UOM_WEIGHT,UOM_LENGTH,UOM_VOLUMIC_MASS
from . import models as _inner_models
import logging
import re
import math
_logger = logging.getLogger(__name__)

def literal_eval(arg):
    if isinstance(arg,bool):
        return arg
    return _literal_eval(arg)

class Model(models.AbstractModel):
    """ Main super-class for regular database-persisted Odoo models.

    Odoo models are created by inheriting from this class::

        class user(Model):
            ...

    The system will later instantiate the class once per database (on
    which the class' module is installed).
    """
    _auto = True                # automatically create database backend
    _register = False           # not visible in ORM registry, meant to be python-inherited only
    _abstract = False           # not abstract
    _transient = False          # not transient

    _models= _inner_models
    # @classmethod
    # def _build_model(self, pool, cr):
    #     super(models.AbstractModel,self)._build_model(pool,cr)
    #     self._models.update(_inner_models)
    def get_param(self,key):
        return literal_eval( self.env['ir.config_parameter'].get_param(key) or False)

    def __getattr__(self,key):
        # print(key)
        if isinstance(key,str) and key in self._models:
            return self.env[self._models[key]]
        res =super().__getattr__(key)
        return res

    def map(self,fn):
        return map(fn,self)

class BaseCurrency(models.AbstractModel):
    _name='base.currency.mixin'
    _description='Currency Mixin'
    currency_id = fields.Many2one('res.currency', string='Currency',required=True,default=lambda self: self.env.company.currency_id.id)

class BaseArchive(models.AbstractModel):
    _name='base.archive.mixin'
    _description='Archive Mixin'
    active = fields.Boolean('Active',default=True)

    def do_archive(self):
        for rec in self:
            rec.active = True
class BaseSequence(models.AbstractModel):
    _name='base.sequence.mixin'
    _description='Sequence Mixin'
    sequence = fields.Integer(string='Sequence',default=1,help="Used to order line.")

class BaseUomConverter(models.AbstractModel):
    _name='base.uom.converter'
    _description='Base uom converter'
    
    base_surface_uom=fields.Many2one('uom.uom', string='Base Surface unit', required=True,readonly=True,default=lambda r:r.env['uom.uom'].search( [('category_id.id','=', literal_eval( r.env['ir.config_parameter'].get_param(UOM_SURFACE) or False) ),('uom_type','=','reference')],limit=1 ))
    base_length_uom=fields.Many2one('uom.uom', string='Base Length unit', required=True,readonly=True,default=lambda r:r.env['uom.uom'].search( [('category_id.id','=', literal_eval( r.env['ir.config_parameter'].get_param(UOM_LENGTH) or False) ),('uom_type','=','reference')],limit=1 ))
    base_weight_uom=fields.Many2one('uom.uom', string='Base weight unit', required=True,readonly=True,default=lambda r:r.env['uom.uom'].search( [('category_id.id','=', literal_eval( r.env['ir.config_parameter'].get_param(UOM_WEIGHT) or False) ),('uom_type','=','reference')],limit=1 ))

    @api.model
    def _get_base_uom(self, key):
        id=literal_eval( self.env['ir.config_parameter'].get_param(key) or False)
        return self.env['uom.uom'].search( [('category_id.id','=', id ),('uom_type','=','reference')],limit=1 )
    @api.model
    def get_base_surface(self):
        self.ensure_one()
        if self.base_surface_uom:
            return self.base_surface_uom
        self.base_surface_uom=self._get_base_uom(UOM_SURFACE)
        return self.base_surface_uom
    @api.model
    def get_base_length(self):
        self.ensure_one()
        if self.base_length_uom:
            return self.base_length_uom
        self.base_length_uom=self._get_base_uom(UOM_LENGTH)
        return self.base_length_uom
    @api.model
    def get_base_weight(self):
        self.ensure_one()
        if self.base_weight_uom:
            return self.base_weight_uom
        self.base_weight_uom=self._get_base_uom(UOM_WEIGHT)
        return self.base_weight_uom