from odoo import models, fields

class RepairProblem(models.Model):
    _name = 'repair.problem'
    _description = 'Repair Problem'

    name = fields.Char(string='Problem Description', required=True)
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        help='Department this problem belongs to (e.g., DTLP, HHP, etc.)'
    )
    category = fields.Selection(
        [
            ('minor', 'Minor'),
            ('major', 'Major'),
            ('critical', 'Critical')
        ],
        string='Category',
        required=False,
    )
    estimated_cost = fields.Char(string='Estimated Cost', help='Estimated repair cost (optional)')
    product_id = fields.Many2one(
        'product.product',
        string='Related Product',
        domain="[('type', '=', 'service')]",
        help='The product/service that will be used in quotations for this problem'
    )