from odoo import models, fields

class RepairLine(models.Model):
    _name = 'repair.line'
    _description = 'Repair Line'

    repair_order_id = fields.Many2one('repair.order', string='Repair Order', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Char(string='Description')
    product_uom_qty = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
