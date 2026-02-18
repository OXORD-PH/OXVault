from odoo import models, fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson"
    )


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_users(self):
        return {
            "search_params": {
                "domain": [("share", "=", False)],  # internal users only
                "fields": ["id", "name"],
            },
        }

    def _get_pos_ui_res_users(self, params):
        return self.env["res.users"].search_read(**params["search_params"])