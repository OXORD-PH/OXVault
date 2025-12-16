{
    'name': 'POS Custom Features',
    'version': '19.0.1.0.0',
    'summary': 'Adds a feature to select the employee responsible for each sales line in Point of Sale.',
    'description': """
POS Custom Features
===================

This module introduces a custom feature in the Point of Sale interface, specifically a button or mechanism to:
* Select and assign the employee who handled or assisted with a specific order line.
* Pass this employee information to the backend for reporting, commission calculation, or tracking purposes.

This helps in accurately tracking employee performance and sales attribution within the PoS environment.
    """,
    'author': 'Jimmy Llano',
    'website': 'https://portfolio-omega-nine-75.vercel.app/',
    'category': 'Sales/Point of Sale',
    'depends': [
        'point_of_sale',
        'hr',
    ],
    'data': [
        'views/invoice_document_view.xml',
        'views/pos_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sales_person_pos/static/src/overrides/models/*.js',
            'sales_person_pos/static/src/js/**/*.js',
            'sales_person_pos/static/src/xml/**/*.xml',
            'sales_person_pos/static/src/css/**/*.css',
        ],
    },
    'images': ['static/description/screen.JPG'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
