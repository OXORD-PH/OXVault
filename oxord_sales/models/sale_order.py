from odoo import models, fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Add new stages for signature workflow
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Sent'),
        ('for_approval', 'Verification'),
        ('approval', 'For Approval'),
        ('customer_approval', 'Customer Approval'),
        ('sale', 'Sales Order'),
    ], string='Status', readonly=True, copy=False, tracking=True)

    # Prepared By
    prepared_by_id = fields.Many2one('res.users', string="Prepared By")
    signature_prepared_by = fields.Binary("Prepared By Signature")
    prepared_by_date = fields.Date("Prepared By Date")

    # Checked By (Head)
    checked_by_id = fields.Many2one('hr.employee', string="Checked By (Head)")
    signature_checked_by = fields.Binary("Checked By Signature")
    checked_by_date = fields.Date("Checked By Date")

    # Approved By (Chief Officer)
    approved_by_id = fields.Many2one('hr.employee', string="Approved By (Chief Officer)")
    signature_approved_by = fields.Binary("Approved By Signature")
    approved_by_date = fields.Date("Approved By Date")

    # Customer
    customer_id = fields.Many2one('res.partner', string="Customer")
    signature_customer = fields.Binary("Customer Signature")
    customer_date = fields.Date("Customer Date")

    notify_validator_sent = fields.Boolean(string="Validator Notified", default=False, readonly=True,
    tracking=True)

    notify_approver_sent = fields.Boolean(
        string="Approver Notified",
        default=False
    )

    validator_user_id = fields.Many2one('res.users', string="Validator User", tracking=True)
    approver_user_id = fields.Many2one('res.users', string="Approver User", tracking=True)

    def log_progress(self, title, message):
        self.ensure_one()
        return self.message_post(
            body=f"""
            🔹 <b>{title}</b><br/>
            👤 User: {self.env.user.name}<br/>
            📌 {message}
            """
        )
    
    def action_set_for_approval(self):
        for rec in self:
            if not self.env.user.has_group('oxord_sales.group_sale_cgs'):
                raise UserError("Only CGS can move to Verification stage.")

            rec.state = 'for_approval'

            rec.log_progress(
                "Stage Update",
                "Moved to Verification stage"
            )

    def action_preview_quotation(self):
        self.ensure_one()
        return self.env.ref('oxord_sales.action_report_oxord_quotation').report_action(self)
            
    def action_set_for_verification(self):
        for order in self:
            order.state = 'for_approval'

            order.log_progress(
                "Stage Update",
                "Moved to Verification stage"
            )


    def action_approve(self):
        for order in self:
            order.state = 'approval'

            order.log_progress(
                "Stage Update",
                "Moved to Approval stage"
            )

    def action_customer_approve(self):
        for order in self:
            order.state = 'customer_approval'

            order.log_progress(
                "Stage Update",
                "Customer approved the quotation"
            )

    def action_confirm(self):
        res = super().action_confirm()

        for order in self:
            order.log_progress(
                "Final Stage",
                "Sales Order confirmed"
            )

        return res

    def action_quotation_send(self):
        res = super().action_quotation_send()
        return res