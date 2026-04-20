from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderApprovalWizard(models.TransientModel):
    _name = "sale.order.approval.wizard"
    _description = "Wizard for Chief Officer Approval"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)

    # Chief Officer Approval
    approved_by_id = fields.Many2one('hr.employee', string="Approved By", readonly=True)
    signature_approved_by = fields.Binary("Signature", widget="signature", required=True)
    approved_by_date = fields.Date("Approved By Date", default=fields.Date.context_today)

    def action_confirm_approval(self):
        for wizard in self:
            order = wizard.sale_order_id

            # 🚨 Ensure only assigned approver
            if order.approver_user_id and self.env.user != order.approver_user_id:
                raise UserError("You are not the assigned approver.")

            # 🔥 Get employee of logged-in user
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)

            if not employee:
                raise UserError("You are not linked to an employee.")

            # ✅ Write values
            order.write({
                'approved_by_id': employee.id,
                'signature_approved_by': wizard.signature_approved_by,
                'approved_by_date': wizard.approved_by_date,
                'state': 'customer_approval',
            })

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        if self._context.get('active_id'):
            order = self.env['sale.order'].browse(self._context['active_id'])

            # 🔥 Get employee of current user
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)

            res.update({
                'sale_order_id': order.id,
                'approved_by_id': employee.id if employee else False,
                'signature_approved_by': order.signature_approved_by,
            })

        return res