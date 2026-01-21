from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_quotation_send(self):
        res = super().action_quotation_send()

        # Replace default quotation PDF with custom Oxord quotation
        if isinstance(res, dict) and res.get('context'):
            res['context'].update({
                'default_report_template': 'oxord_sales.quotation_template',
                'default_report_name': 'Oxord Quotation',
            })

        return res
