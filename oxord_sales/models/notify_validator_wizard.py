from odoo import models, fields
from datetime import timedelta

class NotifyValidatorWizard(models.TransientModel):
    _name = 'sale.order.notify.wizard'
    _description = 'Notify Validator Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    user_id = fields.Many2one(
        'res.users',
        string="Notify User",
        required=True,
        default=lambda self: self.env.user
    )

    def action_notify_validator(self):
        self.ensure_one()
        order = self.sale_order_id
        partner = self.user_id.partner_id

        # ==============================
        # 1. FORCE FOLLOWER (IMPORTANT)
        # ==============================
        if partner.id not in order.message_partner_ids.ids:
            order.message_subscribe(partner_ids=[partner.id])

        # ==============================
        # 2. CHATTER MESSAGE (VISIBLE + NOTIFICATION)
        # ==============================
        message = order.message_post(
            body=f"""
                You have been assigned to validate Sales Order: {order.name}
                Requested by: {self.env.user.name}
            """,
            partner_ids=[partner.id], 
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
        )

        # ==============================
        # 3. FORCE INBOX NOTIFICATION (💬 CLOUD ICON)
        # ==============================
        # self.env['mail.notification'].sudo().create({
        #     'res_partner_id': partner.id,
        #     'mail_message_id': message.id,
        #     'notification_type': 'inbox',
        # })

        # ==============================
        # 4. ACTIVITY (TO DO)
        # ==============================
        order.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.user_id.id,
            note=f"Please validate Sales Order: {order.name}",
            date_deadline=fields.Date.today() + timedelta(days=1),
        )

        # ==============================
        # 5. FLAG
        # ==============================
        order.notify_validator_sent = True
        order.validator_user_id = self.user_id.id

        # ==============================
        # 6. CHATTY LOG (OPTIONAL)
        # ==============================
        order.log_progress(
            "Notification Sent",
            f"Validator notified: {self.user_id.name}"
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }