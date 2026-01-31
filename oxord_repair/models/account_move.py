from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    repair_order_id = fields.Many2one('repair.order', string="Repair Order")
