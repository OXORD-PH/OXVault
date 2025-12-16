
{
    'name': 'Sales Person On POS Order Line',
    'Version': '19.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'This module is used to set sales persons on pos order line',
    'description': 'This module allows you to assign salespersons to order'
                   'lines in the Point of Sale (POS)',
    'author': 'OXORD Computer solutions',
    'company': 'OXORD Computer solutions',
    'maintainer': 'OXORD Computer solutions',
    'website': "https://www.oxord.com.ph",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_orderline_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
                'salesperson_pos_order_line/static/src/js/pos_screen.js',
                'salesperson_pos_order_line/static/src/js/orderline.js',
                'salesperson_pos_order_line/static/src/js/pos_orderline.js',
                'salesperson_pos_order_line/static/src/xml/pos_screen_templates.xml',
                'salesperson_pos_order_line/static/src/xml/orderline_templates.xml',
            ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
