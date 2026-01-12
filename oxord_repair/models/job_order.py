from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class JobOrder(models.Model):
    _name = 'job.order'
    _description = 'Job Order'
    _order = 'order_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(
        string='Job Order Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )


    # ===============================
    # Users & Servicer
    # ===============================
    user_id = fields.Many2one(
        'res.users',
        string='Order Taken By',
        default=lambda self: self.env.user
    )

    servicer_id = fields.Many2one(
        'res.users',
        string='Servicer'
    )

    # ===============================
    # Dates
    # ===============================
    order_date = fields.Datetime(
        string='Order Date',
        default=fields.Datetime.now
    )

    # ===============================
    # Customer Info
    # ===============================
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )
    contact_person_id = fields.Many2one(
        'res.partner',
        string='Contact Person'
    )
    company_name = fields.Char(
        string='Company'
    )
    phone = fields.Char(
        string='Phone'
    )
    job_phone = fields.Char(
        string='Job Phone'
    )

    # ===============================
    # Company & Branch
    # ===============================
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    branch = fields.Selection(
        [
            ('la_hacienda', 'La Hacienda'),
            ('robinsons', 'Robinsons'),
            ('hq', 'Headquarters'),
        ],
        string='Branch',
        required=True
    )

    # ===============================
    # Status / Workflow
    # ===============================
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft'
    )

    # ===============================
    # Notes
    # ===============================
    note = fields.Text(string='Notes')

    # ===============================
    # Readonly Logic (like Repair Order)
    # ===============================
    readonly_customer_info = fields.Boolean(
        compute='_compute_readonly_customer_info',
        store=False
    )

    description = fields.Text(
        string='Job Description',
        placeholder='Enter job description here...'
    )

    job_name = fields.Text(
        string='Job Name / Location',
        placeholder='Enter job name or location here...'
    )

    # Second container fields
    job_name = fields.Text(string='Job Name / Location')
    comments = fields.Text(string='Comments')
    not_home = fields.Boolean(string='Not Home')
    paid_upon_completion = fields.Boolean(string='Paid Upon Completion')
    bill_total_due = fields.Monetary(string='Bill Total Due', currency_field='company_currency_id')
    total_materials = fields.Monetary(string='Total Materials', currency_field='company_currency_id')
    total_labor = fields.Monetary(string='Total Labor', currency_field='company_currency_id')
    tax = fields.Monetary(string='TAX', currency_field='company_currency_id')
    total_due = fields.Monetary(string='Total Due', currency_field='company_currency_id')
    
    # Make sure you have currency field for Monetary fields
    company_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    # Replace the three booleans with a single selection field for the radio
    job_status = fields.Selection(
        [
            ('not_home', 'Not Home'),
            ('paid', 'Paid Upon Completion'),
            ('bill_due', 'Bill Total Due')
        ],
        string='Job Status',
        default='not_home'
    )

    date_completed = fields.Date()
    ordered_by = fields.Many2one('res.partner')

    job_type = fields.Selection([
        ('contract', 'Contract'),
        ('day_work', 'Day Work'),
        ('extra', 'Extra'),
        ('others', 'Others')
    ], string="Job Type", tracking=True)
    
    job_type_others = fields.Char(string="Other Job Type")
    
    def action_print_job_order(self):
        self.ensure_one()  # print only one Job Order
    
        report = self.env.ref(
            'oxord_repair.action_report_job_order',
            raise_if_not_found=False
        )
    
        if not report:
            raise UserError(
                "Report 'action_report_job_order' not found. "
                "Make sure the Job Order report XML is loaded."
            )
    
        return report.report_action(self)
        
    @api.depends('state')
    def _compute_readonly_customer_info(self):
        for record in self:
            record.readonly_customer_info = record.state != 'draft'

    # ===============================
    # CREATE: JO SEQUENCE (BRANCH-BASED)
    # ===============================
    @api.model_create_multi
    def create(self, vals_list):
        sequence_map = {
            'la_hacienda': 'repair.st4.jo',
            'robinsons': 'repair.st3.jo',
            'hq': 'repair.hq.jo',
        }

        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                branch = vals.get('branch')
                if not branch:
                    raise ValidationError(
                        _("Branch is required to generate Job Order reference.")
                    )
                seq_code = sequence_map.get(branch)
                if not seq_code:
                    raise ValidationError(
                        _("No Job Order sequence configured for this branch.")
                    )
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code)

        return super().create(vals_list)

    # ===============================
    # Workflow Methods for Buttons
    # ===============================
    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("Only Draft Job Orders can be confirmed."))
            rec.state = 'confirmed'

    def action_start(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise ValidationError(_("Only Confirmed Job Orders can be started."))
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise ValidationError(_("Only In Progress Job Orders can be marked Done."))
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            if rec.state in ['done', 'cancelled']:
                raise ValidationError(_("Cannot cancel a Done or Cancelled Job Order."))
            rec.state = 'cancelled'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'