from odoo import models, fields, api
from odoo.exceptions import ValidationError

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

    unit_type_id = fields.Many2one(
        'repair.unit.type',
        string="Unit Type",
        domain="[('department_id', '=', department_id)]",
        required=True,
        help="Type of unit (Desktop, Laptop, Phone, Printer, etc.)"
    )

    category = fields.Selection(
        [
            ('minor', 'Minor'),
            ('major', 'Major'),
            ('critical', 'Critical')
        ],
        string='Category'
    )

    estimated_cost = fields.Char(
        string='Estimated Cost',
        help='Estimated repair cost (optional)'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Related Product',
        domain="[('type', '=', 'service')]",
        help='The product/service that will be used in quotations for this problem'
    )

    @api.constrains('department_id', 'unit_type_id')
    def _check_unit_type_department(self):
        for rec in self:
            if rec.unit_type_id and rec.unit_type_id.department_id != rec.department_id:
                raise ValidationError(
                    "The selected Unit Type does not belong to the chosen Department."
                )
