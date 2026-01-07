from odoo import models, fields

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_company_type = fields.Boolean(string="Is Company Type")
    is_individual_type = fields.Boolean(string="Is Individual Type")

    type_name = fields.Selection([
        ('corporate', 'Corporate'),
        ('government', 'Government'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('other', 'Other')
    ], string="Type Name")
