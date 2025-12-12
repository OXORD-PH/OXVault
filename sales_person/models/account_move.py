from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    pos_sales_person_id = fields.Many2one(
        "hr.employee",
        string="POS Sales Person"
    )
