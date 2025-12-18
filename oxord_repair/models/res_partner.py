from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    facebook = fields.Char(string="Facebook")

    @api.constrains('name')
    def _check_duplicate_name(self):
        for rec in self:
            if rec.name and not rec.is_company:
                duplicates = self.env['res.partner'].search([
                    ('name', '=', rec.name),
                    ('id', '!=', rec.id),
                    ('is_company', '=', False)
                ])
                if duplicates:
                    raise UserError(
                        f"A contact named '{rec.name}' already exists. "
                        "Please check before creating a duplicate."
                    )
