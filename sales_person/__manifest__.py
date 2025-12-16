{
    'name': "POS Sales Person6",
    'summary': "Record sales person on POS order",
    'description': "Record sales person on POS order",
    'author': "OXORD DIS",
    'category': 'Point of Sale',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    'depends': [
        'hr',
        'point_of_sale',
        'pos_hr',
        'account',
    ],

    # Backend views (normal XML)
    'data': [
        'views/pos_config_view.xml',
        'views/res_config_settings.xml',
        'views/pos_order_view.xml',
        'views/account_move_view.xml',
    ],


'assets': {
    'point_of_sale._assets_pos': [
        'sales_person/static/src/screens/sales_person_button.js',
        'sales_person/static/src/overrides/control_buttons.js',
        'sales_person/static/src/overrides/pos_store.js',
        'sales_person/static/src/xml/sales_person_button.xml',
    ],
},


    'application': True,
    'installable': True,
    'auto_install': False,
}
