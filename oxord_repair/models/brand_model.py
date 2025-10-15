from odoo import models, fields

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(string="Brand Name", required=True)
    unit_type_id = fields.Many2one('repair.unit.type', string="Unit Type", required=True)
    product_ids = fields.One2many('product.product', 'brand_id', string="Products")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")
    unit_type_id = fields.Many2one(related='brand_id.unit_type_id', store=True, string="Unit Type")
