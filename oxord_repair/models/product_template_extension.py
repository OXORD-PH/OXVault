from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_accessory = fields.Boolean(string="Is Accessory", default=False)
    brand_id = fields.Many2one('product.brand', string="Brand")

    @api.model
    def create(self, vals_list):
        # Ensure vals_list is always a list
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        records = super().create(vals_list)

        # Set is_accessory for each record's variants
        for record, vals in zip(records, vals_list):
            is_accessory = vals.get('is_accessory', False)
            record.product_variant_ids.write({'is_accessory': is_accessory})

        return records

    def write(self, vals):
        res = super().write(vals)
        if 'is_accessory' in vals:
            self.mapped('product_variant_ids').write({'is_accessory': vals['is_accessory']})
        return res
