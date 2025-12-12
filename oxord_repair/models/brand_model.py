from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(string="Brand Name", required=True)
    unit_type_id = fields.Many2one('repair.unit.type', string="Unit Type", required=True)
    product_ids = fields.One2many('product.product', 'brand_id', string="Products")

    @api.model
    def create(self, vals):
        brand = super().create(vals)
        brand._create_brand_attribute_value()
        return brand

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals or 'unit_type_id' in vals:
            self._create_brand_attribute_value()
        return res

    def _create_brand_attribute_value(self):
        """Ensure the Brand attribute has a value matching this brand"""
        brand_attribute = self.env['product.attribute'].search([('name', '=', 'Brand')], limit=1)
        if not brand_attribute:
            brand_attribute = self.env['product.attribute'].create({
                'name': 'Brand',
                'create_variant': 'always',
            })

        for brand in self:
            # Create the attribute value if not exists
            attr_value = self.env['product.attribute.value'].search([
                ('attribute_id', '=', brand_attribute.id),
                ('name', '=', brand.name)
            ], limit=1)
            if not attr_value:
                self.env['product.attribute.value'].create({
                    'name': brand.name,
                    'attribute_id': brand_attribute.id
                })


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string="Brand")
    unit_type_id = fields.Many2one(related='brand_id.unit_type_id', store=True, string="Unit Type")
    is_accessory = fields.Boolean(string="Is Accessory", default=False)

    @api.model
    def create(self, vals):
        product = super().create(vals)
        product._assign_brand_attribute()
        return product

    def write(self, vals):
        res = super().write(vals)
        if 'brand_id' in vals:
            self._assign_brand_attribute()
        return res

    def _assign_brand_attribute(self):
        """Assigns the Brand attribute value based on brand_id"""
        for product in self:
            if product.brand_id:
                brand_attribute = self.env['product.attribute'].search([('name', '=', 'Brand')], limit=1)
                if brand_attribute:
                    attr_value = self.env['product.attribute.value'].search([
                        ('attribute_id', '=', brand_attribute.id),
                        ('name', '=', product.brand_id.name)
                    ], limit=1)
                    if not attr_value:
                        attr_value = self.env['product.attribute.value'].create({
                            'name': product.brand_id.name,
                            'attribute_id': brand_attribute.id
                        })
                    # Assign to product
                    product.attribute_value_ids = [(4, attr_value.id)]
