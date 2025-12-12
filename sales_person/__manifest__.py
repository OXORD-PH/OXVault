{
    'name': "POS Sales Person",
    'summary': "Record sales person on POS order",
    'description': "Record sales person on POS order",
    'author': "OXORD DIS",
    'category': 'Point of Sale',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['hr', 'point_of_sale', 'pos_hr', 'account'],

    'data': [
        'views/account_move_view.xml',
        'views/pos_order_view.xml',
        'views/res_config_settings.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'pos_sales_person/static/src/**/*',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}
