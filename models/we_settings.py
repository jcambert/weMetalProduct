from odoo import api, fields, models
import sys
from ast import literal_eval

SETTINGS='weSettings.'
SHEETMETAL_CATEGORY=SETTINGS+'sheetmetal_category'
PRODUCT_NAME_FORCE_UPPERCASE=SETTINGS+'product_name_force_uppercase'
MATERIAL_ATTRIBUTE=SETTINGS+'material_attribute'
THICKNESS_ATTRIBUTE=SETTINGS+'thickness_attribute'
DIMENSION_ATTRIBUTE=SETTINGS+'dimension_attribute'
UOM_UNITE=SETTINGS+'uom_unite'
UOM_WEIGHT=SETTINGS+'uom_weight'
UOM_TIME=SETTINGS+'uom_time'
UOM_LENGTH=SETTINGS+'uom_length'
UOM_VOLUME=SETTINGS+'uom_volume'
UOM_VOLUMIC_MASS=SETTINGS+'uom_volumic_mass'
UOM_SURFACE=SETTINGS+'uom_surface'
class WeSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    # sheetmetal_category=fields.Many2one('product.category',default=False,config_parameter=SHEETMETAL_CATEGORY, string='Sheetmetal category')
    # profile_categories=fields.Many2many('product.category',string='Profiles categories')
    # component_category=fields.Many2one('product.category',default=False,config_parameter='component_category',string='Product category')
    product_name_force_uppercase = fields.Boolean('Force name uppercase',default=False,config_parameter=PRODUCT_NAME_FORCE_UPPERCASE, help='Clear product material on name change')
    # material_attribute = fields.Many2one('product.attribute',default=False,config_parameter=MATERIAL_ATTRIBUTE,string='Material attribute')
    # thickness_attribute = fields.Many2one('product.attribute',default=False,config_parameter=THICKNESS_ATTRIBUTE,string='Thickness attribute')
    # dimension_attribute = fields.Many2one('product.attribute',default=False,config_parameter=DIMENSION_ATTRIBUTE,string='Dimension attribute')

    """ Needs for domain uom filtering """
    # uom_unite = fields.Many2one('uom.category',string='Unite Category',config_parameter=UOM_UNITE)
    # uom_weight = fields.Many2one('uom.category',string='Weight Category',config_parameter=UOM_WEIGHT)
    # uom_time =  fields.Many2one('uom.category',string='Time Category',config_parameter=UOM_TIME)
    # uom_length= fields.Many2one('uom.category',string='Length/Distance Category',config_parameter=UOM_LENGTH)
    # uom_volume = fields.Many2one('uom.category',string='Volume Category',config_parameter=UOM_VOLUME)
    # uom_volumic_mass= fields.Many2one('uom.category',string='Volumic Mass Category',config_parameter=UOM_VOLUMIC_MASS)
    # uom_surface= fields.Many2one('uom.category',string='Surface Category',config_parameter=UOM_SURFACE)