from odoo import models

class PosSession(models.Model):
    _inherit = "pos.session"
    # No overrides needed for Odoo 19 POS OWL v2
    pass
