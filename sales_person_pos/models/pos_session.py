from odoo import models, api
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)
class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        # config = self.env['pos.config'].browse(config_id)
        # Only load if your module is needed — or always if you want it unconditional
        data.append('hr.employee')
        return data

    @api.model
    def _pos_data_model_hr_employee(self, config, domain=None):
        return self.env['hr.employee'].search_read(
            domain=[('job_title', '=', 'Sales')],  # Load only salespeople
            fields=['id', 'name', 'job_title']
        )

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info("🚀 Mohamed Moghazy - Report called for sessions: %s", docids)

        report_values = super()._get_report_values(docids, data)

        sessions = self.env['pos.session'].browse(docids)
        pos_payments = self.env['pos.payment'].search([('session_id', 'in', docids)])

        from collections import defaultdict
        session_payment_summary = defaultdict(lambda: defaultdict(float))

        for payment in pos_payments:
            session_id = payment.session_id.id
            method_name = payment.payment_method_id.name
            session_payment_summary[session_id][method_name] += payment.amount

        report_values.update({
            'session_payment_summary': session_payment_summary,
            'docs': sessions,
        })

        return report_values
