from odoo import models, fields

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_company_type = fields.Boolean(string="Is Company Type")
    type_name = fields.Selection([
        ('corporate', 'Corporate'),
        ('government', 'Government')
    ], string="Company Type Name")
