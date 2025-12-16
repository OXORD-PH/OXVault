from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    # REQUIRED for POS to load your module
    module_sales_person = fields.Boolean(
        string="Enable POS Sales Person",
        help="Enable the Sales Person feature in POS."
    )

    # Your existing field
    sales_person_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="config_allowed_salesperson_rel",
        column1="pos_config_id",
        column2="employee_id",
        string="Allowed Sales Persons",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_config_id = fields.Many2one(
        comodel_name='pos.config',
        string="POS Configuration",
        default=lambda self: self.env['pos.config'].search([], limit=1),
    )

    sales_person_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Allowed Sales Persons",
    )

    def set_values(self):
        super().set_values()
        if self.pos_config_id:
            self.pos_config_id.write({
                'sales_person_ids': [(6, 0, self.sales_person_ids.ids)]
            })

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update({
            'sales_person_ids': self.pos_config_id.sales_person_ids.ids if self.pos_config_id else [],
        })
        return res
