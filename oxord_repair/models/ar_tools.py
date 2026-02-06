from odoo import models, fields, api

class ARTools(models.Model):
    _name = "ar.tools"
    _description = "AR for Tools - Acknowledgment Form"

    name = fields.Char(
        string="Acknowledgment Reference",
        required=True,
        copy=False,
        default="New",
        readonly=True,
    )
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', string="Prepared By", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    department_id = fields.Many2one('hr.department', string="Department")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('saved', 'Saved')
    ], default='draft', string="Status")
    tool_line_ids = fields.One2many('ar.tools.line', 'ar_tools_id', string="Tools / Equipment")

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        new_records = []
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ar.tools.sequence') or 'New'
            new_records.append(super(ARTools, self).create(vals))
        return new_records if len(new_records) > 1 else new_records[0]

    def action_generate_reference(self):
        for record in self:
            if record.state == 'draft':
                if record.name == 'New':
                    record.name = self.env['ir.sequence'].next_by_code('ar.tools.sequence') or 'AR_TLS/0001'
                record.state = 'saved'
        return True


class ARToolsLine(models.Model):
    _name = "ar.tools.line"
    _description = "Tools / Equipment Line"

    ar_tools_id = fields.Many2one('ar.tools', string="Acknowledgment Form", required=True)
    product_name = fields.Char(string="Item Name", required=True)
    quantity = fields.Integer(string="Quantity", default=1)
    notes = fields.Char(string="Notes")


