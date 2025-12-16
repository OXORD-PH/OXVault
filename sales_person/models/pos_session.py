from odoo import models

class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        """Tell POS to also load hr.employee records."""
        res = super()._pos_ui_models_to_load()
        if "hr.employee" not in res:
            res.append("hr.employee")
        return res

    def _loader_params_hr_employee(self):
        """Restrict employees to those allowed in the POS Config."""
        config = self.config_id
        return {
            "search_params": {
                "domain": [("id", "in", config.sales_person_ids.ids)] if config else [],
                "fields": ["id", "name"],
            }
        }

    def _get_pos_ui_hr_employee(self, params):
        """Return employees for POS frontend based on loader params."""
        return self.env["hr.employee"].search_read(**params.get("search_params", {}))
