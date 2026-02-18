{
    "name": "OXORD Pos Salesperson",
    "version": "1.0",
    "depends": ["point_of_sale"],
    "data": [
        "views/pos_order_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_salesperson/static/src/js/payment_screen.js",
            "pos_salesperson/static/src/xml/pos_button.xml",
        ],
    },
    "installable": True,
}
