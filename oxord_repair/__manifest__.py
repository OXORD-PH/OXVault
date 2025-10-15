{
    'name': 'OXORD Repair',
    'version': '1.0',
    'summary': 'Custom Repair Workflow for OXORD',
    'description': 'Customized repair order workflow and fields for OXORD process',
    'author': 'OXORD Computer Solutions',
    'depends': ['repair', 'base', 'stock'],
    'data': [
        'data/hr_department_data.xml',
        'data/repair_unit_type_data.xml',
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/repair_order_view.xml',
        'views/repair_order_tree_view.xml',
        'views/res_partner_views.xml',
        'views/res_partner_category.xml',
        'views/repair_action.xml',  
        'views/repair_menu.xml',
        'reports/repairorder_report.xml',
        'reports/repairorder_report_action.xml',
        'data/product_brand_data.xml',
        'data/product_model_data.xml',
        'data/repair_sequence.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'oxord_repair/static/src/css/repair_styles.css',
        ],
    },
    'installable': True,
    'application': True,
}
