from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(string="Brand Name", required=True)
    product_ids = fields.Many2many(
        'product.product',
        'brand_id',
        string="Products"
    )

    # Link to unit types with labor & service type per unit type
    unit_type_ids = fields.One2many(
        'product.brand.unit.type', 'brand_id',
        string="Unit Types"
    )

    @api.model
    def create(self, vals):
        brand = super().create(vals)
        brand._create_brand_attribute_value()
        return brand

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals:
            self._create_brand_attribute_value()
        return res

    def _create_brand_attribute_value(self):
        """Ensure the Brand attribute has a value matching this brand"""
        brand_attribute = self.env['product.attribute'].search(
            [('name', '=', 'Brand')], limit=1
        )
        if not brand_attribute:
            brand_attribute = self.env['product.attribute'].create({
                'name': 'Brand',
                'create_variant': 'always',
            })

        for brand in self:
            attr_value = self.env['product.attribute.value'].search([
                ('attribute_id', '=', brand_attribute.id),
                ('name', '=', brand.name)
            ], limit=1)

            if not attr_value:
                self.env['product.attribute.value'].create({
                    'name': brand.name,
                    'attribute_id': brand_attribute.id
                })


class ProductBrandUnitType(models.Model):
    _name = 'product.brand.unit.type'
    _description = 'Brand Unit Type Mapping'

    brand_id = fields.Many2one('product.brand', string="Brand", required=True)
    unit_type_id = fields.Many2one('repair.unit.type', string="Unit Type", required=True)
    labor_amount = fields.Float(string="Labor Amount", required=True)
    service_type = fields.Selection(
        [
            ('carry_in', 'Carry In'),
            ('onsite', 'Onsite'),
            ('both', 'Carry In / Onsite'),
        ],
        string="Service Type",
        default='carry_in',
        required=True
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one(
        related='product_tmpl_id.brand_id',
        store=True,
        string="Brand"
    )

    unit_type_id = fields.Many2one(
        'repair.unit.type',
        string="Unit Type"
    )

    labor_amount = fields.Float(
        string="Labor Amount",
        help="Labor amount based on brand & unit type"
    )

    service_type = fields.Selection(
        [
            ('carry_in', 'Carry In'),
            ('onsite', 'Onsite'),
            ('both', 'Carry In / Onsite'),
        ],
        string="Service Type"
    )

    is_accessory = fields.Boolean(string="Is Accessory", default=False)

    @api.model
    def create(self, vals):
        product = super().create(vals)
        product._assign_brand_attributes()
        return product

    def write(self, vals):
        res = super().write(vals)
        if 'brand_id' in vals or 'unit_type_id' in vals:
            self._assign_brand_attributes()
        return res

    def _assign_brand_attributes(self):
        """Assign labor and service type based on brand and unit type"""
        for product in self:
            if product.brand_id and product.unit_type_id:
                mapping = self.env['product.brand.unit.type'].search([
                    ('brand_id', '=', product.brand_id.id),
                    ('unit_type_id', '=', product.unit_type_id.id)
                ], limit=1)
                if mapping:
                    product.labor_amount = mapping.labor_amount
                    product.service_type = mapping.service_type

            # Assign Brand attribute value for variants
            if product.brand_id:
                brand_attribute = self.env['product.attribute'].search(
                    [('name', '=', 'Brand')], limit=1
                )
                if not brand_attribute:
                    brand_attribute = self.env['product.attribute'].create({
                        'name': 'Brand',
                        'create_variant': 'always',
                    })

                attr_value = self.env['product.attribute.value'].search([
                    ('attribute_id', '=', brand_attribute.id),
                    ('name', '=', product.brand_id.name)
                ], limit=1)
                if not attr_value:
                    attr_value = self.env['product.attribute.value'].create({
                        'name': product.brand_id.name,
                        'attribute_id': brand_attribute.id
                    })

                existing_ids = product.product_tmpl_id.product_template_attribute_value_ids \
                    .mapped('product_attribute_value_id').ids

                if attr_value.id not in existing_ids:
                    self.env['product.template.attribute.value'].create({
                        'product_tmpl_id': product.product_tmpl_id.id,
                        'product_attribute_value_id': attr_value.id,
                    })
