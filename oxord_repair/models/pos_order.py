# pos_order.py
from odoo import models, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    repair_order_id = fields.Many2one(
        'repair.order',
        string='Repair Order',
        index=True,
        help="Link this POS order to a repair order"
    )

    def action_pos_order_paid(self):
        """
        This method is called when the POS order is paid.
        It automatically updates the linked repair order's `is_pos_paid` field.
        """
        # Call the standard POS paid action first
        res = super().action_pos_order_paid()

        for order in self:
            if order.repair_order_id:
                # Mark the repair order as paid in POS
                repair = order.repair_order_id
                repair.is_pos_paid = True
                repair.invalidate_recordset()  # force recompute

        return res
