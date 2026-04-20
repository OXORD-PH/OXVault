from odoo import models, fields, api

class SaleOrderCustomerWizard(models.TransientModel):
    _name = "sale.order.customer.wizard"
    _description = "Wizard for Customer Approval"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)

    # Customer Approval Fields
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    signature_customer = fields.Binary("Customer Signature", widget="signature", required=True)
    customer_date = fields.Date("Customer Approval Date", default=fields.Date.context_today)

    def action_confirm_customer(self):
        for wizard in self:
            order = wizard.sale_order_id
            order.customer_id = wizard.customer_id
            order.signature_customer = wizard.signature_customer
            order.customer_date = wizard.customer_date
            # Final stage
            order.state = 'sale'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self._context.get('active_id'):
            order = self.env['sale.order'].browse(self._context['active_id'])
            res.update({
                'sale_order_id': order.id,
                'customer_id': order.customer_id,
                'signature_customer': order.signature_customer,
            })
        return res