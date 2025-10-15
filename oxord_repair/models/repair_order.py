from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class RepairOrder(models.Model):
    _inherit = 'repair.order'



    state_for_statusbar = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('under_repair', 'Under Repair'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ],
        string='Status for Statusbar',
        compute='_compute_state_for_statusbar',
        store=True
    )

    is_cancelled = fields.Boolean(string="Is Cancelled", compute="_compute_is_cancelled")


    model_id = fields.Many2one(
        'product.product', 
        string="Model")  


    unit_type_id = fields.Many2one(
        'repair.unit.type',
        string="Unit Type",
        required = True,

    )

    department_id = fields.Many2one(
        'hr.department',
        string="Department",
        domain="[('name','in',['DTLP','HHP','PCAV','PJT'])]",
        required = True,
        help="Select the actual department"
    )

    brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        domain="[('unit_type_id', '=', unit_type_id)]"
    )

    # ------------------------
    # Branch Field
    # ------------------------
    branch = fields.Selection(
        [
            ('la_hacienda', 'La Hacienda'),
            ('robinsons', 'Robinsons')
        ],
        string='Branch',
        default='la_hacienda',
        required=True,
        help="Select the branch for this repair order"
    )

    # ------------------------
    # Customer Type / Company Category
    # ------------------------
    customer_type = fields.Selection(
        [('individual', 'Individual'), ('company', 'Company')],
        string="Customer Type",
        compute='_compute_customer_type',
        inverse='_set_customer_type',
        store=True,
        help="Select if the customer is an Individual or a Company"
    )

    # ------------------------
    # Company Category (only if customer is a company)
    # ------------------------
    company_category = fields.Many2one(
        'res.partner.category',
        string="Company Type",
        required = True,
        help="Select the company type (Corporate, Government, etc.)"
    )




    # ------------------------
    # Company
    # ------------------------
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=False,
        index=True
    )

    # ------------------------
    # Coordinator / Technician Fields
    # ------------------------
    component_status = fields.Selection([
        ('ok', 'OK'),
        ('for_replacement', 'For Replacement'),
        ('defective', 'Defective')
    ], string="Component Status")
    initial_check_by = fields.Many2one('res.users', string="Initial Check By")
    encoded_by = fields.Many2one('res.users', string="Encoded By")
    endorse_to_tech = fields.Many2one('res.users', string="Endorsed to Tech")
    endorse_to_authorized_coordinator = fields.Many2one('res.users', string="Endorsed to Coordinator")

    # ------------------------
    # Aging fields (kept for internal logic)
    # ------------------------
    received_date = fields.Datetime(string="Received Date", default=fields.Datetime.now)
    initial_check_start_date = fields.Datetime(string="Initial Check Start Date")
    encoded_start_date = fields.Datetime(string="Encoded Start Date")
    endorse_to_tech_start_date = fields.Datetime(string="To Tech Start Date")
    endorse_to_coordinator_start_date = fields.Datetime(string="To Coordinator Start Date")

    received_aging = fields.Char(string="Received Aging", compute="_compute_received_aging", store=True)
    initial_check_aging = fields.Char(string="Initial Check Aging", compute="_compute_initial_check_aging", store=True)
    encoded_aging = fields.Char(string="Encoded Aging", compute="_compute_encoded_aging", store=True)
    endorse_to_tech_aging = fields.Char(string="Endorse to Tech Aging", compute="_compute_endorse_to_tech_aging", store=True)
    endorse_to_authorized_coordinator_aging = fields.Char(string="Coordinator Aging", compute="_compute_endorse_to_coordinator_aging", store=True)

    # ------------------------
    # Customer Information (related to partner)
    # ------------------------
    partner_street = fields.Char(
        related='partner_id.street',
        string="Street",
        readonly=False
    )
    partner_city = fields.Char(
        related='partner_id.city',
        string="City",
        readonly=False
    )
    partner_state_id = fields.Many2one(
        related='partner_id.state_id',
        string="State",
        readonly=False
    )
    partner_zip = fields.Char(
        related='partner_id.zip',
        string="ZIP",
        readonly=False
    )
    partner_country_id = fields.Many2one(
        related='partner_id.country_id',
        string="Country",
        readonly=False
    )
    phone = fields.Char(
        string="Telephone", 
        compute="_compute_partner_info", 
        inverse="_set_partner_info", 
        store=True
    )
    email = fields.Char(
        string="Email", 
        compute="_compute_partner_info", 
        inverse="_set_partner_info", 
        store=True
    )
    facebook = fields.Char(
        string="Facebook",
        related="partner_id.facebook",
        readonly=False   # editable here, saves to contact
    )
    # facebook = fields.Char(related='partner_id.facebook', string="Facebook", readonly=True)  # optional if partner has facebook field




    # Show Unit Info only if a department is selected
    show_unit_info = fields.Boolean(
        string="Show Unit Info",
        compute="_compute_show_unit_info",
        store=True
    )

    show_brand_info = fields.Boolean(
    string="Show Brand Info",
    compute="_compute_show_brand_info",
    store=True
    )

    # ------------------------
    serial = fields.Char(string="Serial")
    accessories = fields.Char(string="Accessories")
    pop_date = fields.Date(string="POP Date")
    warranty = fields.Char(string="Warranty")
    password = fields.Char(string="Password")
    ok_to_format = fields.Boolean(string="Ok to Format")
    problem = fields.Text(string="Problem")

    
    # Receiving Details
    # ------------------------
    received_time = fields.Float(string="Time")  # Can be float for hours/minutes
    received_by = fields.Many2one('res.users', string="Received By")
    remarks = fields.Text(string="Remarks")

    # ------------------------
    # Service Details
    # ------------------------
    action_taken = fields.Text(string="Action Taken")
    labor_amount = fields.Float(string="Labor Amount")
    total_charge = fields.Float(string="Total Charge")
    technician_remarks = fields.Text(string="Technician Remarks")


    # ---------------------------------------
    # Repair Workflow Actions
    # ---------------------------------------

    # def action_confirm(self):
    #     """Confirm the repair order."""
    #     for rec in self:
    #         rec.state = 'confirmed'

    def action_start_repair(self):
        """Mark repair as in progress (from draft)."""
        for rec in self:
            rec.state = 'under_repair'

    def action_end_repair(self):
        """Mark repair as completed."""
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        """Cancel the repair order."""
        for rec in self:
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        """Reset to draft state."""
        for rec in self:
            rec.state = 'draft'


    @api.depends('state')
    def _compute_state_for_statusbar(self):
        for rec in self:
            # If cancelled, include cancel in statusbar
            if rec.state == 'cancel':
                rec.state_for_statusbar = rec.state
            else:
                # Otherwise map state to same value, but "cancel" won't show in statusbar
                rec.state_for_statusbar = rec.state
            

    @api.depends('unit_type_id')
    def _compute_show_unit_info(self):
        for rec in self:
            rec.show_unit_info = bool(rec.unit_type_id)

    @api.depends('unit_type_id')
    def _compute_show_brand_info(self):
        for rec in self:
            rec.show_brand_info = bool(rec.unit_type_id)
       
    @api.onchange('customer_type')
    def _onchange_customer_type(self):
        if self.customer_type == 'company':
            self.company_category = False
            return {
                'domain': {
                    'company_category': [('is_company_type', '=', True)]
                }
            }
        else:
            self.company_category = None

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            self.brand_id = self.model_id.brand_id
            self.unit_type_id = self.model_id.unit_type_id


    @api.depends('state')
    def _compute_is_cancelled(self):
        for rec in self:
            rec.is_cancelled = rec.state == 'cancel'

    @api.depends('partner_id.is_company')
    def _compute_customer_type(self):
        for rec in self:
            rec.customer_type = 'company' if rec.partner_id and rec.partner_id.is_company else 'individual'

    def _set_customer_type(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.is_company = True if rec.customer_type == 'company' else False

    @api.onchange('company_category')
    def _onchange_company_category(self):
        """Assign selected company category to partner's tags"""
        if self.partner_id and self.customer_type == 'company' and self.company_category:
            self.partner_id.category_id = [(6, 0, [self.company_category.id])]


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-fill customer details, type, and company type."""
        if self.partner_id:
            self.phone = self.partner_id.phone or ''
            self.email = self.partner_id.email or ''
            self.customer_type = 'company' if self.partner_id.is_company else 'individual'

            if self.partner_id.is_company:
                company_tag = self.partner_id.category_id.filtered(lambda c: c.is_company_type)
                if company_tag:
                    self.company_category = company_tag[0]
                else:
                    self.company_category = False
            else:
                self.company_category = False
        else:
            self.phone = ''
            self.email = ''
            self.customer_type = False
            self.company_category = False


    @api.depends('partner_id')
    def _compute_partner_info(self):
        for rec in self:
            if rec.partner_id:
                rec.phone = rec.partner_id.phone or ''
                rec.email = rec.partner_id.email or ''
            else:
                rec.phone = ''
                rec.email = ''

            
    def _set_partner_info(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.phone = rec.phone
                rec.partner_id.email = rec.email

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            return {
                'domain': {
                    'model_id': [('brand_id', '=', self.brand_id.id)]
                }
            }
        else:
            return {'domain': {'model_id': []}}

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Dynamically filter Unit Types based on selected Department."""
        for rec in self:
            # Reset the field if changing department
            rec.unit_type_id = False  

            # Apply domain dynamically
            if rec.department_id:
                return {
                    'domain': {
                        'unit_type_id': [('department_id', '=', rec.department_id.id)]
                    }
                }
            else:
                return {
                    'domain': {'unit_type_id': []}
            }

    @api.onchange('unit_type_id')
    def _onchange_unit_type_id(self):
        """Reset brand and model when unit type changes, and filter allowed brands."""
        if self.unit_type_id:
            # Clear brand and model to prevent mismatched values
            self.brand_id = False
            self.model_id = False
            return {
                'domain': {
                    'brand_id': [('unit_type_id', '=', self.unit_type_id.id)]
                }
            }
        else:
            # If no unit type selected, clear both and show all
            self.brand_id = False
            self.model_id = False
            return {'domain': {'brand_id': []}}


    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        self.model_id = False
        return {
            'domain': {
                'model_id': [('brand_id', '=', self.brand_id.id)]
            }
        }
        
 


    # ------------------------
    # Helper: Format Duration
    # ------------------------
    def _format_duration(self, start_time):
        if not start_time:
            return ''
        now = datetime.now()
        diff = now - start_time
        seconds = int(diff.total_seconds())
        years, remainder = divmod(seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{years}y, {months}m, {days}d, {hours}h, {minutes}min, {seconds}s"

    # ------------------------
    # Create / Write Overrides
    # ------------------------
    @api.model
    def create(self, vals):
        branch = vals.get('branch', 'la_hacienda')

        if branch == 'hq':
            raise UserError("Repair orders cannot be created for HQ branch.")

        if branch == 'la_hacienda':
            vals['name'] = self.env['ir.sequence'].next_by_code('repair.order.lahacienda')
        elif branch == 'robinsons':
            vals['name'] = self.env['ir.sequence'].next_by_code('repair.order.robinsons')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('repair.order') or '/'

        return super().create(vals)

    def write(self, vals):
        for rec in self:
            if 'initial_check_by' in vals and not rec.initial_check_start_date:
                vals['initial_check_start_date'] = fields.Datetime.now()
            if 'encoded_by' in vals and not rec.encoded_start_date:
                vals['encoded_start_date'] = fields.Datetime.now()
            if 'endorse_to_tech' in vals and not rec.endorse_to_tech_start_date:
                vals['endorse_to_tech_start_date'] = fields.Datetime.now()
            if 'endorse_to_authorized_coordinator' in vals and not rec.endorse_to_coordinator_start_date:
                vals['endorse_to_coordinator_start_date'] = fields.Datetime.now()
        return super().write(vals)      


    # ------------------------
    # Aging Computation
    # ------------------------
    @api.depends('received_date', 'state')
    def _compute_received_aging(self):
        for rec in self:
            if rec.state not in ('done', 'cancel'):
                rec.received_aging = self._format_duration(rec.received_date)

    @api.depends('initial_check_start_date', 'state')
    def _compute_initial_check_aging(self):
        for rec in self:
            if rec.state not in ('done', 'cancel') and rec.initial_check_start_date:
                rec.initial_check_aging = self._format_duration(rec.initial_check_start_date)

    @api.depends('encoded_start_date', 'state')
    def _compute_encoded_aging(self):
        for rec in self:
            if rec.state not in ('done', 'cancel') and rec.encoded_start_date:
                rec.encoded_aging = self._format_duration(rec.encoded_start_date)

    @api.depends('endorse_to_tech_start_date', 'state')
    def _compute_endorse_to_tech_aging(self):
        for rec in self:
            if rec.state not in ('done', 'cancel') and rec.endorse_to_tech_start_date:
                rec.endorse_to_tech_aging = self._format_duration(rec.endorse_to_tech_start_date)

    @api.depends('endorse_to_coordinator_start_date', 'state')
    def _compute_endorse_to_coordinator_aging(self):
        for rec in self:
            if rec.state not in ('done', 'cancel') and rec.endorse_to_coordinator_start_date:
                rec.endorse_to_authorized_coordinator_aging = self._format_duration(rec.endorse_to_coordinator_start_date)

    # ------------------------
    # Parts Request Action
    # ------------------------
    def action_open_parts_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parts Request',
            'res_model': 'repair.parts.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_repair_id': self.id,
            }
        }
