from odoo import models, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    selected_employee_id = fields.Many2one('hr.employee', string="Selected Employee")
    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        vals['pos_employee_id'] = self.selected_employee_id.id
        return vals

