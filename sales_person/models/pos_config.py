from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

    sales_person_ids = fields.Many2many(
        "hr.employee",
        "config_allowed_salesperson_rel",
        "pos_config_id",
        "employee_id",
        string="Allowed Sales Persons",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sales_person_ids = fields.Many2many(
        related="pos_config_id.sales_person_ids",
        readonly=False,
    )
