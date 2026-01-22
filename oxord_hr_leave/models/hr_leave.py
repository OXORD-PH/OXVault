from odoo import models, fields, api

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    flow_state = fields.Selection([
        ('request', 'Requesting'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Leave Flow Status', default='request', tracking=True)

    # Letter fields
    request_date = fields.Date(string='Date', default=fields.Date.today)
    hr_officer_name = fields.Char(string='To', default='ROLAND BERIA')
    hr_officer_position = fields.Char(string='Position', default='Human Resource Officer')
    hr_company = fields.Char(string='Company', default='OXORD Computer Solutions and Repair Center')
    hr_office_address = fields.Char(string='Address', default='Arnaldo Blvd. Roxas City, Capiz')
    letter_from = fields.Char(string='From', compute='_compute_letter_from')
    letter_body = fields.Html()

    @api.depends('employee_id')
    def _compute_letter_from(self):
        for rec in self:
            rec.letter_from = rec.employee_id.name if rec.employee_id else ''

    def action_send_request(self):
        """Employee submits request. Only updates flow_state."""
        for rec in self:
            rec.flow_state = 'request'
            rec.message_post(body="Leave request submitted.")  # optional notification