{
    'name': 'POS Sales Person',
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
    'assets': {
        'point_of_sale.assets': [
            'salesperson/static/src/js/salesperson_button.js',
            'salesperson/static/src/js/salesperson_popup.js',
            'salesperson/static/src/xml/salesperson_button.xml',
            'salesperson/static/src/xml/salesperson_popup.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
