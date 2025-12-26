from odoo import models, fields, api

class RepairOrderPart(models.Model):
    _name = 'repair.order.part'
    _description = 'Repair Order Parts'

    repair_order_id = fields.Many2one('repair.order', string='Repair Order')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Monetary(string='Unit Price', currency_field='currency_id')
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit
