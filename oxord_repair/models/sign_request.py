from odoo import models, api

class SignRequest(models.Model):
    _inherit = 'sign.request'

    def _post_fill_request_item(self):
        """
        This is called after a signature is confirmed.
        Update related repair.order receiving_signature_state and attach signed documents.
        """
        res = super()._post_fill_request_item()
        for item in self.item_ids:
            if item.res_model == 'repair.order' and item.res_id:
                repair = self.env['repair.order'].browse(item.res_id)
                repair.receiving_signature_state = 'signed'

                # Attach the signed documents from this sign request to repair order
                if self.signed_attachment_ids:
                    repair.signed_attachment_ids = [(6, 0, self.signed_attachment_ids.ids)]
        return res
