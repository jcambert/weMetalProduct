from odoo import api, fields, models
import sys
from ast import literal_eval
class WeSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sheetmetal_category=fields.Many2one('product.category',string='Sheetmetal category')
    profile_categories=fields.Many2many('product.category',string='Profiles categories')
    material_convention
    def set_values(self):
        res=super(WeSettings, self).set_values()
        fn=self.env['ir.config_parameter'].set_param
        fn('weOdooProduct.sheetmetal_category',self.sheetmetal_category.id or False)
        fn('weOdooProduct.profile_categories',self.profile_categories.ids or [])
        return res
    @api.model
    def get_values(self):
        res = super(WeSettings, self).get_values()
        try:
            fn = self.env['ir.config_parameter'].sudo().get_param
            sheetmetal_category=fn('weOdooProduct.sheetmetal_category')
            profile_categories=fn('weOdooProduct.profile_categories')
            res.update(sheetmetal_category=literal_eval( sheetmetal_category),profile_categories=literal_eval(profile_categories))
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