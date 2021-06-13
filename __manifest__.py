# -*- coding: utf-8 -*-
{
    'name': "Metal Product Extension",

    'summary': """
        Extension Addon that evolve product""",

    'description': """
        Addon Product
    """,

    'author': "AMBERT Jean-Christophe",
    'website': "http://jc.ambert.free.fr",

    #For Orm goto https://www.odoo.com/documentation/14.0/fr/developer/reference/orm.html
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base','mrp','product',  'uom'],

    # always loaded
    'data': [
        'security/we_security.xml',
        'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
        # 'data/ir_module_category.xml',
        # 'data/mrp_plm_data.xml',
        # 'views/indice_views.xml',
        'views/product_views.xml',
        'views/material_views.xml',
        'views/profile_views.xml',
        'views/profile_type_views.xml',
        # 'views/res_config_settings_view.xml',
        'views/product_attribute_views.xml',
        'views/product_category_views.xml',
        'views/menus_views.xml',
        'data/uom.xml',
        'data/product_categories.xml',
        'data/materials.xml',
        'data/profiles.xml',
        'data/settings.xml',
        'data/product_attribute.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': False
}
