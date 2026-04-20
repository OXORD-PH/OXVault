from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrderVerificationWizard(models.TransientModel):
    _name = "sale.order.verification.wizard"
    _description = "Wizard for Prepared and Checked By Signatures"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    
    # Checked By (Head)
    checked_by_id = fields.Many2one('hr.employee', string="Checked By", readonly=True)
    signature_checked_by = fields.Binary("Checked By Signature", widget="signature", required=True)
    checked_by_date = fields.Date("Checked By Date", default=fields.Date.context_today)


    def action_confirm_verification(self):
        for wizard in self:
            order = wizard.sale_order_id

            # 🚨 Ensure only assigned validator
            if order.validator_user_id and self.env.user != order.validator_user_id:
                raise UserError("You are not the assigned validator.")

            # 🔥 Always get employee from logged-in user
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)

            if not employee:
                raise UserError("You are not linked to an employee.")

            order.write({
                'checked_by_id': employee.id,  # 🔥 force correct user
                'signature_checked_by': wizard.signature_checked_by,
                'checked_by_date': wizard.checked_by_date,
                'state': 'approval',
            })

            return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        if self._context.get('active_id'):
            order = self.env['sale.order'].browse(self._context['active_id'])

            # 🔥 get employee of CURRENT USER (validator)
            employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)

            res.update({
                'sale_order_id': order.id,
                'checked_by_id': employee.id if employee else False,
                'signature_checked_by': order.signature_checked_by,
            })

        return res