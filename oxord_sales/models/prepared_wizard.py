from odoo import models, fields
from datetime import date

class SaleOrderPreparedWizard(models.TransientModel):
    _name = 'sale.order.prepared.wizard'
    _description = 'Prepared By Signature Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)

    prepared_by_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user
    )

    signature_prepared_by = fields.Binary(required=True)

    def action_sign_prepared(self):
        self.ensure_one()

        self.sale_order_id.write({
            'prepared_by_id': self.prepared_by_id.id,
            'prepared_by_date': date.today(),
            'signature_prepared_by': self.signature_prepared_by,
            'state': 'for_approval',
        })

        return {'type': 'ir.actions.act_window_close'}