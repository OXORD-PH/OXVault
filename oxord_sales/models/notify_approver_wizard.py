from odoo import models, fields
from datetime import timedelta
from odoo.exceptions import UserError

class NotifyApproverWizard(models.TransientModel):
    _name = 'sale.order.notify.approver.wizard'
    _description = 'Notify Approver Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    user_id = fields.Many2one(
        'res.users',
        string="Approver",
        required=True,
        default=lambda self: self.env.user
    )

    def action_notify_approver(self):
        self.ensure_one()
        order = self.sale_order_id
        partner = self.user_id.partner_id

        # =========================
        # 1. VALIDATION
        # =========================
        if not self.user_id.has_group('oxord_sales.group_sale_approver'):
            raise UserError("Selected user is not allowed to approve.")

        # =========================
        # 2. FORCE FOLLOWER
        # =========================
        if partner.id not in order.message_partner_ids.ids:
            order.message_subscribe(partner_ids=[partner.id])

        # =========================
        # 3. CHATTER MESSAGE (CLEAN)
        # =========================
        order.message_post(
            body=f"""
                <b>Approval Request</b><br/>
                You have been assigned to APPROVE Sales Order: <b>{order.name}</b><br/>
                Requested by: {self.env.user.name}
            """,
            partner_ids=[partner.id],
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )

        # =========================
        # 4. ACTIVITY (TO DO)
        # =========================
        order.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.user_id.id,
            note=f"Please approve Sales Order: {order.name}",
            date_deadline=fields.Date.today() + timedelta(days=1),
        )

        # =========================
        # 5. FLAG
        # =========================
        order.notify_approver_sent = True
        order.approver_user_id = self.user_id.id

        # =========================
        # 6. LOG PROGRESS
        # =========================
        order.log_progress(
            "Approval Notification Sent",
            f"Approver notified: {self.user_id.name}"
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }