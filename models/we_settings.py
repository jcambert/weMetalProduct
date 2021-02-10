from odoo import api, fields, models
import sys
from ast import literal_eval

class WeTag(models.Model):
    _name='we.setting.tag'
    _description='Setting tag'
    name = fields.Char('Tag Name', required=True, translate=True)
    
    _sql_constraints = [
        ('setting_tag_name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class WeSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sheetmetal_category=fields.Many2one('product.category',string='Sheetmetal category')
    profile_categories=fields.Many2many('product.category',string='Profiles categories')
    material_convention_names=fields.Many2many('we.setting.tag', 'we_setting_material_tag_rel', 'setting_id', 'material_tag_id', string='Material convention name')
    sheetmetal_convention_names=fields.Many2many('we.setting.tag', 'we_setting_sheetmetal_tag_rel', 'setting_id', 'sheetmetal_tag_id', string='Sheetmetal convention name')
    profile_convention_names=fields.Many2many('we.setting.tag', 'we_setting_profile_tag_rel', 'setting_id', 'profile_tag_id', string='Profile convention name')
    
    clear_product_on_category_change = fields.Boolean('Clear on category change', help='Clear product material on category change',default=False)
    clear_product_on_name_change = fields.Boolean('Clear on name Change', help='Clear product material on name change',default=False)

    def set_values(self):
        res=super(WeSettings, self).set_values()
        fn=self.env['ir.config_parameter'].set_param
        fn('weOdooProduct.sheetmetal_category',self.sheetmetal_category.id or False)
        fn('weOdooProduct.profile_categories',self.profile_categories.ids or [])
        fn('weOdooProduct.material_convention_names',self.material_convention_names.ids or [])
        fn('weOdooProduct.sheetmetal_convention_names',self.sheetmetal_convention_names.ids or [])
        fn('weOdooProduct.profile_convention_names',self.profile_convention_names.ids or [])

        fn('weOdooProduct.clear_product_on_category_change',self.clear_product_on_category_change)
        fn('weOdooProduct.clear_product_on_name_change',self.clear_product_on_name_change)


        return res
    
    @api.model
    def get_values(self):
        res = super(WeSettings, self).get_values()
        try:
            fn = self.env['ir.config_parameter'].sudo().get_param
            sheetmetal_category=fn('weOdooProduct.sheetmetal_category')
            profile_categories=fn('weOdooProduct.profile_categories')
            material_convention_names=fn('weOdooProduct.material_convention_names')
            sheetmetal_convention_names=fn('weOdooProduct.sheetmetal_convention_names')
            profile_convention_names=fn('weOdooProduct.profile_convention_names')

            clear_product_on_category_change=fn('weOdooProduct.clear_product_on_category_change') or False
            clear_product_on_name_change=fn('weOdooProduct.clear_product_on_name_change') or False


            res.update(
                sheetmetal_category=literal_eval( sheetmetal_category),
                profile_categories=literal_eval(profile_categories),
                material_convention_names=literal_eval(material_convention_names),
                sheetmetal_convention_names=literal_eval(sheetmetal_convention_names),
                profile_convention_names=literal_eval(profile_convention_names),
                clear_product_on_category_change=clear_product_on_category_change,
                clear_product_on_name_change=clear_product_on_name_change
                )
        except :
            print("Unexpected error:", sys.exc_info()[0])
        return res

    # @api.model
    # def _params(self,param):
    #     return 'weOdooProduct.%s' % (param)
    # @api.model
    # def __write(self,fn,param):
    #     fn(self._params(param),getattr(self,param))

    # @api.model
    # def __read(self,fn,param,values):
    #     result=fn(self._params(param))
    #     values[param]=result
    #     setattr(self,param,result)
    
    # def set_values(self):
    #     res=super(WeSettings, self).set_values()
    #     fn=self.env['ir.config_parameter'].sudo().set_param
    #     for field in ['sheetmetal_category']:
    #         self.__write(fn,field)
    #     return res
    # @api.model
    # def get_values(self):
    #     res = super(WeSettings, self).get_values()
    #     fn = self.env['ir.config_parameter'].sudo().get_param
    #     values={}
    #     for field in ['sheetmetal_category']:
    #         self.__read(fn,field,values)
    #     res.update(values)
    #     return res