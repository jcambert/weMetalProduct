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
    product_name_force_uppercase = fields.Boolean('Force name uppercase', help='Clear product material on name change',default=False)
  
    indice_for_purchased = fields.Boolean('Indice for purchased product', help='Indice for purchased product',default=False)
    
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
        fn('weOdooProduct.indice_for_purchased',self.indice_for_purchased)
        fn('weOdooProduct.product_name_force_uppercase',self.product_name_force_uppercase)


        return res
    
    @api.model
    def get_values(self):
        res = super(WeSettings, self).get_values()
        try:
            fn = self.env['ir.config_parameter'].sudo().get_param
            sheetmetal_category=fn('weOdooProduct.sheetmetal_category') or False
            profile_categories=fn('weOdooProduct.profile_categories') or False
            material_convention_names=fn('weOdooProduct.material_convention_names') or False
            sheetmetal_convention_names=fn('weOdooProduct.sheetmetal_convention_names') or False
            profile_convention_names=fn('weOdooProduct.profile_convention_names') or False

            clear_product_on_category_change=fn('weOdooProduct.clear_product_on_category_change') or False
            clear_product_on_name_change=fn('weOdooProduct.clear_product_on_name_change') or False
            product_name_force_uppercase=fn('weOdooProduct.product_name_force_uppercase') or False
            indice_for_purchased=fn('weOdooProduct.indice_for_purchased') or False

            

            updates={}
            if isinstance(sheetmetal_category,str) :
                updates['sheetmetal_category']=literal_eval(sheetmetal_category)
            if isinstance(profile_categories,str):
                updates['profile_categories']=literal_eval(profile_categories)
            if isinstance(material_convention_names,str):
                updates['material_convention_names']=literal_eval(material_convention_names)
            if isinstance(sheetmetal_convention_names,str):
                updates['sheetmetal_convention_names']=literal_eval(sheetmetal_convention_names)
            if isinstance(profile_convention_names,str):
                updates['profile_convention_names']=literal_eval(profile_convention_names)
            
            updates['clear_product_on_category_change']=clear_product_on_category_change
            updates['clear_product_on_name_change']=clear_product_on_name_change
            updates['product_name_force_uppercase']=product_name_force_uppercase
            updates['indice_for_purchased']=indice_for_purchased

            res.update(updates)
            # res.update(
            #     sheetmetal_category=literal_eval( sheetmetal_category),
            #     profile_categories=literal_eval(profile_categories),
            #     material_convention_names=literal_eval(material_convention_names),
            #     sheetmetal_convention_names=literal_eval(sheetmetal_convention_names),
            #     profile_convention_names=literal_eval(profile_convention_names),
            #     clear_product_on_category_change=clear_product_on_category_change,
            #     clear_product_on_name_change=clear_product_on_name_change
            #     )
        except :
            print("Unexpected error:", sys.exc_info()[0])
            raise
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