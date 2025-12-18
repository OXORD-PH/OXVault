from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    background_image = fields.Binary("PDF Background Image")
    code = fields.Char(string="Branch Code")


