from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    repair_order_id = fields.Many2one('repair.order', string="Related Repair Order")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if len(self) == 1 and self.repair_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Repair Order',
                'res_model': 'repair.order',
                'res_id': self.repair_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return res

