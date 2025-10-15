from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    facebook = fields.Char(string="Facebook")
