{
    'name': 'OXORD Pos',
    'version': '1.0.0',
    'summary': 'POS Salesperson selection',
    'description': """
Adds a selectable Salesperson field in POS UI
to track who catered the customer.
""",
    'author': 'Oxord',
    'depends': [
        'point_of_sale',
    ],

    # Backend views (POS Order form)
    'data': [
        'views/pos_order_view.xml',
    ],

    # POS frontend assets
    'assets': {
        'point_of_sale.assets': [
            'oxord_pos/static/src/js/pos_salesperson.js',
            'oxord_pos/static/src/js/pos_salesperson_db.js',
            'oxord_pos/static/src/js/pos_salesperson_action.js',
        ],
    },



    'installable': True,
    'application': False,
}
