from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_accessory = fields.Boolean(string="Is Accessory", default=False)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.product_variant_ids.write({'is_accessory': vals.get('is_accessory', False)})
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'is_accessory' in vals:
            self.mapped('product_variant_ids').write({'is_accessory': vals['is_accessory']})
        return res
