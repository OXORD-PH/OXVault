from odoo import models, fields, api

class ARFreeService(models.Model):
    _name = "ar.free.service"
    _description = "Acknowledgment Receipt for Free Service"

    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company
    )

    name = fields.Char(
        string="Acknowledgment Reference",
        required=True,
        copy=False,
        default="New",
        readonly=True,
    )

    employee_id = fields.Many2one('hr.employee', string="Prepared By", required=True)
    recipient_name = fields.Char(string="Received By")
    wo_number = fields.Char(string="WO Number")
    brand_model = fields.Char(string="Brand / Model")
    serial_number = fields.Char(string="Serial Number")
    department_id = fields.Many2one('hr.department', string="Department")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('saved', 'Saved')
    ], default='draft', string="Status")

    customer_name = fields.Char(string="Customer Name")
    customer_company = fields.Char(string="Customer Company")
    unit_type = fields.Char(string="Unit Type")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ar.free.service'
                ) or 'New'
        return super().create(vals_list)


    def action_generate_reference(self):
        for record in self:
            if record.state == 'draft':
                if record.name == 'New':
                    record.name = self.env['ir.sequence'].next_by_code('ar.free.service') or 'ARFS/0001'
                record.state = 'saved'
        return True
