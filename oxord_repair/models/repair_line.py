from odoo import models, fields, api

class RepairLine(models.Model):
    _name = 'repair.line'
    _description = 'Repair Line'

    repair_order_id = fields.Many2one(
        'repair.order',
        string="Parent Repair Order",
        required=True
    )
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    estimated_cost = fields.Float(string='Estimated Cost', compute='_compute_estimated_cost')

    @api.depends('product_id')
    def _compute_estimated_cost(self):
        for line in self:
            line.estimated_cost = line.product_id.lst_price if line.product_id else 0.0
