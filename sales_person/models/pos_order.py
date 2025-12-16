from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    sales_person_id = fields.Many2one(
        "hr.employee",
        string="POS Sales Person"
    )

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        if 'sales_person_id' in ui_order:
            res['sales_person_id'] = ui_order.get('sales_person_id')
        return res

    def action_pos_order_invoice(self):
        self.ensure_one()
        res = super().action_pos_order_invoice()

        if res.get('res_id'):
            invoice = self.env['account.move'].browse(res['res_id'])
            if invoice:
                invoice.write({
                    'sales_person_id': self.sales_person_id.id,
                })

        return res