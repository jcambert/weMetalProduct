# -*- coding: utf-8 -*-
{
    'name': "We Addon Product",

    'summary': """
        Extension Addon that evolve product""",

    'description': """
        Addon Product
    """,

    'author': "We",
    'website': "http://jc.ambert.free.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['base','mrp','product', 'mail', 'uom'],

    # always loaded
    'data': [
        'security/we_security.xml',
        'security/ir.model.access.csv',
        # 'data/ir_cron.xml',
        # 'data/ir_module_category.xml',
        # 'data/mrp_plm_data.xml',
        'data/product_category.xml',
        'data/material.xml',
        'data/sheetmetal.xml',
        'data/settings.xml',
        'views/indice_views.xml',
        'views/product_views.xml',
        'views/menus_views.xml',
        'views/res_config_settings_view.xml',
        
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    # 'demo': ['data/mrp_plm_demo.xml'],
    
    #Module Installation
    'installable': True,
    'application': True,
    'auto_install': False
}
