from odoo import models, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        readonly=True
    )
