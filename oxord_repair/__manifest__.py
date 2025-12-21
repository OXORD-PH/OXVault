{
    'name': 'OXORD Repair',
    'version': '1.0',
    'summary': 'Custom Repair Workflow for OXORD',
    'description': 'Customized repair order workflow and fields for OXORD process',
    'author': 'OXORD Computer Solutions',
    'license': 'LGPL-3',  # <-- added license key
    'depends': ['base', 'repair', 'hr', 'sale', 'stock'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'report/repair_order_template.xml',
        'report/repair_order_report.xml',
        'report/technical_report_template.xml', 
        # 'data/repair_sequence_data.xml',
        'data/technical_report_sequence.xml',
        'views/repair_endorse_wizard_view.xml',
        'views/endorse_coordinator_wizard.xml',
        'views/technical_report_views.xml',
        'views/repair_order_view.xml',
        'views/product_accessory_view.xml',
        'views/product_brand_views.xml',
        'views/repair_problem_views.xml',
        'views/unit_type_views.xml',
        'views/repair_services_menu.xml',
        'views/repair_order_reporting_view.xml',
        'views/repair_order_tree_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_views.xml',
        'views/res_partner_category.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'oxord_repair/static/src/css/repair_styles.css',
        ],
    },
    'installable': True,
    'application': True,
}
