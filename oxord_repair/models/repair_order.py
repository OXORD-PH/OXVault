from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class RepairOrder(models.Model):
    _inherit = 'repair.order'


    state_for_statusbar = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('under_repair', 'Under Repair'),
            ('done', 'Done'),
            ('released', 'Released'),
            ('cancel', 'Cancelled')
        ],
        string='Status for Statusbar',
        compute='_compute_state_for_statusbar',
        store=True
    )

    # Extend the original state field to include 'released'
    state = fields.Selection(
        selection_add=[('released', 'Released')],
        string='Status',
        readonly=True,
        copy=False,
        tracking=True,
        default='draft'
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
        required=False,
        help="Select the branch for this repair order"
    )

    # ------------------------
    # Customer Type / Company Category
    # ------------------------
    customer_category = fields.Selection(
        [('individual', 'Individual'), ('company', 'Company')],
        string="Customer Type",
        compute='_compute_customer_category',
        inverse='_set_customer_category',
        store=True,
        help="Select if the customer is an Individual or a Company"
    )

    individual_type = fields.Many2one(
        'res.partner.category',
        string="Individual Type",
        domain="[('is_individual_type', '=', True)]"
    )


    company_category = fields.Many2one(
        'res.partner.category',
        string="Company Type",
        domain="[('is_company_type', '=', True)]"
    )

    show_company_type = fields.Boolean(compute="_compute_show_fields", store=False)
    show_individual_type = fields.Boolean(compute="_compute_show_fields", store=False)


    contact_person_id = fields.Many2one(
        'res.partner',
        string='Contact Person',
        help="Person who represents the company for this transaction."
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
    # Service Type
    # ------------------------
    service_type = fields.Selection([
        ('carry_in', 'Carry-In'),
        ('onsite', 'Onsite')
    ], string='Service Type', required=True, default='carry_in')


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


    # ---------- Computed / Visibility Fields ----------
    show_unit_info = fields.Boolean(compute='_compute_show_unit_info')



    show_brand_info = fields.Boolean(
    string="Show Brand Info",
    compute="_compute_show_brand_info",
    store=True
    )

    # ------------------------
    serial = fields.Char(string="Serial")
    
    problem_ids = fields.Many2many(
    'repair.problem',
    string="Problems",
    domain="[('department_id', '=', department_id)]",
    help="Select one or more problems related to this department"
    )

    estimated_cost = fields.Float(
        string="Total Estimated Cost",
        compute="_compute_problem_details",
        store=True,
    )

    category = fields.Selection(
        related='problem_ids.category',
        string="Category",
        store=True
    )

 

    accessory_ids = fields.Many2many(
        'product.template',
        string='Accessories',
        domain="[('is_accessory', '=', True)]",
        help="Select accessories related to this repair unit"
    )

    password = fields.Char(string="Password")

    
    # Receiving Details
    # ------------------------
    received_date = fields.Datetime(string="Received Date", default=fields.Datetime.now)
    received_by = fields.Many2one('res.users', string="Received By", required=True)
    remarks = fields.Text(string="Remarks")

    # ------------------------
    # Service Details
    # ------------------------
    endorse_to_tech = fields.Many2one(
        'res.users',
        string="Technician/Engineer Assigned",
        help="The technician or engineer responsible for the repair.",
        required=True
    )
    action_taken = fields.Text(string="Action Taken")
    labor_amount = fields.Float(string="Labor Amount")
    technician_remarks = fields.Text(string="Technician Remarks")






    # ------------------------
    # Aging fields (timestamps + computed)
    # ------------------------
    repair_start_date = fields.Datetime(string="Start Repair Date", readonly=True)
    repair_end_date = fields.Datetime(string="End Repair Date", readonly=True)
    parts_requested_date = fields.Datetime(string="Parts Requested Date", readonly=True)
    parts_received_date = fields.Datetime(string="Parts Received Date", readonly=True)
    released_date = fields.Datetime(string="Released Date", readonly=True)

    # Stored numeric fields (reportable)
    total_aging_days = fields.Float(
        string="Total Aging (Received → Released, days)",
        compute="_compute_aging_durations",
        store=True
    )
    repair_duration_days = fields.Float(
        string="Repair Duration (Start → End, days)",
        compute="_compute_aging_durations",
        store=True
    )
    parts_wait_days = fields.Float(
        string="Parts Aging (Requested → Received, days)",
        compute="_compute_aging_durations",
        store=True
    )


    total_aging_formatted = fields.Char(string="Total Aging (Detailed)", compute="_compute_aging_durations", store=False)
    repair_duration_formatted = fields.Char(string="Repair Duration (Detailed)", compute="_compute_aging_durations", store=False)
    parts_wait_formatted = fields.Char(string="Parts Wait (Detailed)", compute="_compute_aging_durations", store=False)


    pop_date = fields.Date(string="POP Date")
    warranty_status = fields.Selection(
        [
            ('in_warranty', 'In Warranty'),
            ('out_warranty', 'Out of Warranty'),
        ],
        string="Warranty Status",
        compute="_compute_warranty_status",
        store=True
    )

    warranty_expiry_date = fields.Date(string="Warranty Expiry Date", compute="_compute_warranty_status", store=True)


    readonly_customer_info = fields.Boolean(
        string="Readonly Customer Info",
        compute="_compute_readonly_customer_info",
        store=False
    )



    show_contact_person = fields.Boolean(
        string="Show Contact Person",
        compute="_compute_show_contact_person",
        store=False
    )


    # --- New field for coordinator (Releasing Info)
    coordinator_id = fields.Many2one('res.users', string="Coordinator")



    show_releasing = fields.Boolean(
        string="Show Releasing",
        compute="_compute_show_releasing"
    )


    # Timestamp when coordinator is assigned
    coordinator_assigned_date = fields.Datetime(
        string="Coordinator Assigned Date",
        readonly=True,
    )

    # Computed duration from coordinator assigned → released
    coordinator_to_release_days = fields.Float(
        string="Coordinator → Release (days)",
        compute="_compute_aging_durations",
        store=True
    )

    coordinator_to_release_formatted = fields.Char(
        string="Coordinator → Release (Detailed)",
        compute="_compute_aging_durations",
        store=False
    )

    previous_tech_duration_days = fields.Float(
        string="Previous Technician Duration (days)",
        compute="_compute_aging_durations",
        store=True
    )

    current_tech_duration_days = fields.Float(
        string="Current Technician Duration (days)",
        compute="_compute_aging_durations",
        store=True
    )

    # Technician fields
    previous_technician_id = fields.Many2one("res.users", string="Previous Technician")

    # Timing fields
    previous_tech_start = fields.Datetime(string="Previous Tech Start")
    previous_tech_end = fields.Datetime(string="Previous Tech End")

    current_tech_start = fields.Datetime(string="Current Tech Start")
    current_tech_end = fields.Datetime(string="Current Tech End")

    # Computed aging
    previous_tech_aging = fields.Float(string="Previous Technician Aging (Hours)", compute="_compute_aging_durations")
    current_tech_aging = fields.Float(string="Current Technician Aging (Hours)", compute="_compute_aging_durations")


    # --- New formatted fields ---
    previous_tech_duration_formatted = fields.Char(
        string="Previous Technician Duration (formatted)",
        compute="_compute_aging_durations",
        store=True,
        default="0s"
    )
    current_tech_duration_formatted = fields.Char(
        string="Current Technician Duration (formatted)",
        compute="_compute_aging_durations",
        store=True,
        default="0s"

    )

    quotation_id = fields.Many2one(
        'sale.order',
        string="Quotation",
        readonly=True,
    )


    invoice_ids = fields.One2many('account.move', 'repair_order_id', string="Invoices")  # optional

    is_rerepair = fields.Boolean(string="Is Re-Repair", default=False)
    original_repair_id = fields.Many2one(
        'repair.order', 
        string="Original Repair", 
        readonly=True
    )


    show_repair_info = fields.Boolean(
        string='Show Repair Info',
        compute='_compute_show_repair_info',
        store=False
    )



    # Count of invoices (for smart button)
    invoice_count = fields.Integer(
        string="Invoices",
        compute='_compute_invoice_count'
    )

    # Count of stock moves (for smart button)
    move_count = fields.Integer(
        string="Stock Moves",
        compute='_compute_move_count'
    )
    
    # One2many to show linked reports
    technical_report_ids = fields.One2many(
        'technical.report',
        'repair_order_id',
        string='Technical Reports'
    )
   
    def action_create_technical_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Technical Report',
            'res_model': 'technical.report',
            'view_mode': 'form',
            'context': {
                'default_repair_order_id': self.id,
            }
        }

    
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)

    @api.depends('move_ids')
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(rec.move_ids)

    # Action for smart button to view invoices
    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'default_repair_id': self.id},
        }

    # Action for smart button to view stock moves
    def action_view_moves(self):
        self.ensure_one()
        return {
            'name': 'Stock Moves',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.move_ids.ids)],
        }
        
    @api.depends('is_rerepair')
    def _compute_show_repair_info(self):
        for order in self:
            order.show_repair_info = order.is_rerepair
            

    def action_rereturn(self):
        self.ensure_one()

        if not self.received_by:
            raise ValidationError(_("Received By is required before Re-Repair."))

        vals = {
            # Flags
            'is_rerepair': True,
            'original_repair_id': self.id,

            # Selection fields
            'customer_category': self.customer_category,
            'service_type': self.service_type,
            'company_category': self.company_category,
            'individual_type': self.individual_type,

            # MANY2ONE → ALWAYS .id
            'partner_id': self.partner_id.id,
            'contact_person_id': self.contact_person_id.id or False,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'unit_type_id': self.unit_type_id.id,
            'brand_id': self.brand_id.id,
            'model_id': self.model_id.id,
            'endorse_to_tech': self.endorse_to_tech.id or False,
            'received_by': self.received_by.id,

            # Unit info
            'serial': self.serial,
            'password': self.password,
            'pop_date': self.pop_date,

            # MANY2MANY → (6, 0, ids)
            'accessory_ids': [(6, 0, self.accessory_ids.ids)],
            'problem_ids': [(6, 0, self.problem_ids.ids)],

            # Reset workflow
            'received_date': fields.Datetime.now(),
            'state': 'draft',
        }

        new_order = self.env['repair.order'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Re-Repair Order'),
            'res_model': 'repair.order',
            'view_mode': 'form',
            'res_id': new_order.id,
            'target': 'current',
        }

    
    def action_create_payment_invoice(self):
        self.ensure_one()
    
        if self.invoice_ids:
            raise UserError("Invoice already exists for this repair order.")
    
        # Create invoice
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'repair_order_id': self.id,
        })
    
        # Add PROBLEMS HEADER
        self.env['account.move.line'].create({
            'move_id': invoice.id,
            'product_id': False,
            'quantity': 0,
            'price_unit': 0,
            'name': "=== PROBLEMS ===",
            'display_type': 'line_section',
        })
    
        # Add Problem Lines
        for problem in self.problem_ids:
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': False,
                'quantity': 1,
                'price_unit': problem.estimated_cost or 0.0,
                'name': problem.name,
            })

        # === PARTS (from standard repair order moves) ===
        if self.move_ids:
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'display_type': 'line_section',
                'name': '=== PARTS ===',
            })
        
            for move in self.move_ids:
                if not move.product_id or move.product_uom_qty <= 0:
                    continue
        
                product = move.product_id
                account = (
                    product.property_account_income_id
                    or product.categ_id.property_account_income_categ_id
                )
                if not account:
                    raise UserError(
                        f"No income account defined for product {product.display_name}"
                    )
        
                self.env['account.move.line'].create({
                    'move_id': invoice.id,
                    'product_id': product.id,
                    'name': product.display_name,
                    'quantity': move.product_uom_qty,
                    'price_unit': product.lst_price,
                    'account_id': account.id,
                    'tax_ids': [(6, 0, product.taxes_id.ids)],
                })


    
        # Add Labor Line if exists
        if self.labor_amount and self.labor_amount > 0:
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': False,
                'quantity': 0,
                'price_unit': 0,
                'name': "=== OTHER ===",
                'display_type': 'line_section',
            })
    
            self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': False,
                'quantity': 1,
                'price_unit': self.labor_amount,
                'name': "Labor Charge",
            })
    
        # Refresh page so button disappears
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



    def action_print_claim_form(self):
        self.ensure_one()  # Make sure only one record is printed
        report = self.env.ref('oxord_repair.action_report_repair_order', raise_if_not_found=False)
        if not report:
            raise UserError("Report 'action_report_repair_order' not found. Make sure the XML is loaded.")
        return report.report_action(self)
    



    @api.depends('problem_ids')
    def _compute_problem_details(self):
        for rec in self:
            # Sum all estimated costs (convert to float safely)
            total_cost = 0.0
            for p in rec.problem_ids:
                try:
                    total_cost += float(p.estimated_cost or 0)
                except ValueError:
                    continue  # ignore non-numeric entries
            rec.estimated_cost = total_cost

            # Combine all categories as string
            rec.category = ', '.join([p.category for p in rec.problem_ids if p.category])



    # -----------------------------------------------------------
    # WHEN FIRST TECHNICIAN IS ASSIGNED
    # -----------------------------------------------------------
    @api.onchange("endorse_to_tech")
    def _onchange_endorse_to_tech(self):
        """Just store the assigned tech as previous technician placeholder; do NOT start timing yet."""
        if self.endorse_to_tech and not self.previous_technician_id:
            self.previous_technician_id = self.endorse_to_tech



    # -----------------------------------------------------------
    # CALL FROM WIZARD
    # -----------------------------------------------------------
    def set_new_technician(self, new_tech):
        self.endorse_to_tech = new_tech.id









    def action_endorse_to_tech(self):
        return {
            'name': 'Endorse Technician',
            'type': 'ir.actions.act_window',
            'res_model': 'repair.endorse.tech.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_repair_id': self.id},
        }



    @api.depends('coordinator_id')
    def _compute_show_releasing(self):
        for rec in self:
            rec.show_releasing = bool(rec.coordinator_id)


    # --- Button to open the wizard
    def action_open_endorse_wizard(self):
        """Open popup wizard for endorsing to coordinator"""
        return {
            'name': 'Endorse to Coordinator',
            'type': 'ir.actions.act_window',
            'res_model': 'endorse.coordinator.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_repair_id': self.id},
        }

    @api.onchange('unit_type_id')
    def _onchange_unit_type_for_accessories(self):
        for rec in self:
            if rec.unit_type_id:
                accessory_domain = [
                    ('is_accessory', '=', True),
                    ('unit_type_id', '=', rec.unit_type_id.id)
                ]
                rec.accessory_ids = [(6, 0, self.env['product.product'].search(accessory_domain).ids)]
            else:
                rec.accessory_ids = [(6, 0, [])]
    


    @api.depends('customer_category')
    def _compute_show_contact_person(self):
        for rec in self:
            rec.show_contact_person = rec.customer_category == 'company'
            # Reset contact_person_id if switching to individual
            if rec.customer_category != 'company':
                rec.contact_person_id = False



    def _format_datetime(self, dt):
        """Helper: nicely format datetime for PDF reports."""
        if not dt:
            return "-"
        return dt.strftime("%b %d, %Y %I:%M %p")  # Example: Oct 25, 2025 03:45 PM



    @api.depends(
        'received_date', 'released_date',
        'repair_start_date', 'repair_end_date',
        'parts_requested_date', 'parts_received_date'
    )
    def _compute_readable_durations(self):
        for rec in self:
            rec.total_aging_readable = rec._format_duration(
                rec.received_date, rec.released_date or fields.Datetime.now()
            ) if rec.received_date else ''

            rec.repair_duration_readable = rec._format_duration(
                rec.repair_start_date, rec.repair_end_date or fields.Datetime.now()
            ) if rec.repair_start_date else ''

            rec.parts_wait_readable = rec._format_duration(
                rec.parts_requested_date, rec.parts_received_date or fields.Datetime.now()
            ) if rec.parts_requested_date else ''


    @api.depends('state')
    def _compute_readonly_customer_info(self):
        for rec in self:
            # Once repair starts or beyond, make fields read-only
            rec.readonly_customer_info = rec.state in ('under_repair', 'done', 'released')

    @api.depends('pop_date')
    def _compute_warranty_status(self):
        """Automatically determine warranty status based on POP Date."""
        today = fields.Date.today()
        for rec in self:
            if rec.pop_date:
                expiry_date = rec.pop_date + timedelta(days=365)  # 1-year warranty
                rec.warranty_expiry_date = expiry_date
                rec.warranty_status = 'in_warranty' if today <= expiry_date else 'out_warranty'
            else:
                rec.warranty_status = False
                rec.warranty_expiry_date = False


    @api.depends('customer_category')
    def _compute_show_fields(self):
        for record in self:
            record.show_company_type = record.customer_category == 'company'
            record.show_individual_type = record.customer_category == 'individual'

    @api.depends(
        'state',
        'received_date', 'repair_start_date', 'repair_end_date',
        'parts_requested_date', 'parts_received_date', 'released_date',
        'coordinator_id', 'coordinator_assigned_date',
        'previous_tech_start', 'previous_tech_end',
        'current_tech_start', 'current_tech_end'
    )


    def _compute_aging_durations(self):
        """Compute Total Aging, Repair Duration, Parts Wait, and Coordinator-to-Release durations in days and detailed format.
        Freeze durations if state is 'cancel' or 'released'.
        """
        def format_duration(seconds):
            """Convert seconds to Xd Yh Zm Ws"""
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            parts = []
            if days: parts.append(f"{days}d")
            if hours: parts.append(f"{hours}h")
            if minutes: parts.append(f"{minutes}m")
            if secs or not parts: parts.append(f"{secs}s")
            return " ".join(parts)

        for rec in self:
            now = fields.Datetime.now()
            freeze = rec.state in ('cancel', 'released')

            # --- Total Aging ---
            if rec.received_date:
                end_total = rec.released_date if rec.released_date else (rec.received_date if freeze else now)
                delta_total = (end_total - rec.received_date).total_seconds() if end_total else 0
                rec.total_aging_days = round(delta_total / 86400, 4)
                rec.total_aging_formatted = format_duration(delta_total)
            else:
                rec.total_aging_days = 0.0
                rec.total_aging_formatted = "0s"

            # --- Repair Duration ---
            if rec.repair_start_date:
                end_repair = rec.repair_end_date if rec.repair_end_date else (rec.repair_start_date if freeze else now)
                delta_repair = (end_repair - rec.repair_start_date).total_seconds() if end_repair else 0
                rec.repair_duration_days = round(delta_repair / 86400, 4)
                rec.repair_duration_formatted = format_duration(delta_repair)
            else:
                rec.repair_duration_days = 0.0
                rec.repair_duration_formatted = "0s"
            
            # --- Previous Technician ---
            if rec.previous_tech_start:
                # Previous tech ends when a new tech is assigned
                end_prev = rec.previous_tech_end or rec.current_tech_start or now
                delta_prev = (end_prev - rec.previous_tech_start).total_seconds()
                rec.previous_tech_duration_days = round(delta_prev / 86400, 2)
                rec.previous_tech_duration_formatted = format_duration(delta_prev)
            else:
                rec.previous_tech_duration_days = 0.0
                rec.previous_tech_duration_formatted = "0s"

            # --- Current Technician ---
            if rec.current_tech_start:
                # Current tech ends when repair is done
                if rec.state == 'done':
                    end_curr = rec.repair_end_date or now
                else:
                    end_curr = rec.current_tech_end or now
                delta_curr = (end_curr - rec.current_tech_start).total_seconds()
                rec.current_tech_duration_days = round(delta_curr / 86400, 2)
                rec.current_tech_duration_formatted = format_duration(delta_curr)
            else:
                rec.current_tech_duration_days = 0.0
                rec.current_tech_duration_formatted = "0s"


            
            # Assign the aging in hours
            rec.previous_tech_aging = rec.previous_tech_duration_days * 24
            rec.current_tech_aging = rec.current_tech_duration_days * 24


            # --- Parts Wait ---
            if rec.parts_requested_date:
                end_parts = rec.parts_received_date if rec.parts_received_date else (rec.parts_requested_date if freeze else now)
                delta_parts = (end_parts - rec.parts_requested_date).total_seconds() if end_parts else 0
                rec.parts_wait_days = round(delta_parts / 86400, 4)
                rec.parts_wait_formatted = format_duration(delta_parts)
            else:
                rec.parts_wait_days = 0.0
                rec.parts_wait_formatted = "0s"

            # --- Coordinator to Release Duration ---
            if rec.coordinator_assigned_date:
                end_coord = rec.released_date if rec.released_date else (now if not freeze else rec.coordinator_assigned_date)
                delta_coord = (end_coord - rec.coordinator_assigned_date).total_seconds()
                rec.coordinator_to_release_days = round(delta_coord / 86400, 4)
                rec.coordinator_to_release_formatted = rec._format_duration(
                    rec.coordinator_assigned_date, end_coord
                )
            else:
                rec.coordinator_to_release_days = 0.0
                rec.coordinator_to_release_formatted = "0s"




    @api.onchange('partner_id')
    def _onchange_partner_for_contact(self):
        """
        Set the domain of contact_person_id so only individual contacts are selectable.
        """
        if not self.partner_id or not self.partner_id.is_company:
            return {'domain': {'contact_person_id': [('id', '=', False)]}}

        return {
            'domain': {'contact_person_id': [
                ('parent_id', '=', self.partner_id.id),
                ('is_company', '=', False)
            ]}
        }





    def action_start_repair(self):
        """Mark repair as in progress and start first technician aging."""
        for rec in self:

            # Set repair start date if not already set
            if not rec.repair_start_date:
                rec.repair_start_date = fields.Datetime.now()

            # Change state
            rec.state = 'under_repair'

            # Ensure previous technician is set
            if not rec.previous_technician_id and rec.endorse_to_tech:
                rec.previous_technician_id = rec.endorse_to_tech

            # Start first technician aging
            if rec.previous_technician_id and not rec.previous_tech_start:
                rec.previous_tech_start = fields.Datetime.now()


    def action_done(self):
        for rec in self:
            if rec.state != 'under_repair':
                raise UserError("Only repairs in progress can be marked as done.")
    
            now = fields.Datetime.now()
            rec.repair_end_date = now
    
            # Stop previous technician aging
            if rec.previous_tech_start and not rec.previous_tech_end:
                rec.previous_tech_end = now
    
            # Stop current technician aging
            if rec.current_tech_start and not rec.current_tech_end:
                rec.current_tech_end = now
            elif not rec.current_tech_start:
                rec.current_tech_start = now
                rec.current_tech_end = now
    
            rec.state = 'done'
            rec.message_post(body=f"Repair marked as <b>Done</b> by {self.env.user.name}.")
    
            # Create invoice in draft automatically (manual payment)
            rec.action_create_invoice()



    
    def action_request_parts(self):
        """Stamp the parts requested datetime (call when requesting parts)."""
        for rec in self:
            if not rec.parts_requested_date:
                rec.parts_requested_date = fields.Datetime.now()
            # optionally set a state like waiting_parts if you have that

    def action_parts_received(self):
        """Stamp the parts received datetime (call when parts arrive)."""
        for rec in self:
            rec.parts_received_date = fields.Datetime.now()
    
    def action_release(self):
        """Mark as released (final stage) and stamp released_date."""
        for rec in self:
            # Only completed orders can be released
            if rec.state != 'done':
                raise UserError("Only completed repair orders can be released.")
    
            # Check if already released
            if rec.released_date:
                raise UserError("This repair order is already released.")
    
            # Check invoices
            if not rec.invoice_ids:
                raise UserError("Cannot release this repair order: no invoice exists.")
    
            # Filter invoices: must be posted AND paid
            unpaid_invoices = rec.invoice_ids.filtered(lambda inv: inv.state != 'posted' or inv.payment_state != 'paid')
            if unpaid_invoices:
                raise UserError(
                    "Cannot release this repair order because the related invoice(s) are not posted or not fully paid."
                )
    
            # Release the order
            rec.released_date = fields.Datetime.now()
            rec.state = 'released'


    def action_cancel(self):
        """Allow cancel on all states except released."""
        for rec in self:
            # if rec.state == 'released':
            #     raise UserError("You cannot cancel a Repair Order that's already released.")
            rec.state = 'cancel'
            # Freeze timestamps
            rec.repair_end_date = rec.repair_end_date or fields.Datetime.now()
            rec.released_date = rec.released_date or fields.Datetime.now()

    def unlink(self):
        """Allow deletion only if not released."""
        # for rec in self:
        #     if rec.state == 'released':
        #         raise UserError("You cannot delete a Repair Order that's already released.")
        return super().unlink()

    @api.model
    def _check_can_cancel(self, states):
        """
        Override base check: consider only 'released' as final.
        This prevents the 'done' state from blocking cancel.
        """
        # No need to call super; we handle logic here
        return states

    @api.model
    def _check_can_delete(self, states):
        """
        Override base check: consider only 'released' as final.
        """
        return states


    def action_reset_to_draft(self):
        """Reset to draft state."""
        for rec in self:
            rec.state = 'draft'


    @api.depends('state')
    def _compute_state_for_statusbar(self):
        """Map repair states for the statusbar. Only 'released' or 'cancel' are final."""
        for rec in self:
            if rec.state in ('cancel', 'released'):
                rec.state_for_statusbar = rec.state
            elif rec.state == 'done':
                # Treat done as intermediate (repair completed but not released)
                rec.state_for_statusbar = 'under_repair'
            else:
                rec.state_for_statusbar = rec.state


    @api.depends('unit_type_id')
    def _compute_show_unit_info(self):
        """Show unit info section only if unit type is selected."""
        for record in self:
            record.show_unit_info = bool(record.unit_type_id)



    @api.depends('unit_type_id')
    def _compute_show_brand_info(self):
        for rec in self:
            rec.show_brand_info = bool(rec.unit_type_id)
       
    @api.onchange('customer_category')
    def _onchange_customer_category(self):
        """Filter customers by category and clear irrelevant tag fields."""
        if not self:
            return

        # Clear opposite type tags
        if self.customer_category == 'company':
            self.individual_type = False
            domain = [('is_company', '=', True)]
        elif self.customer_category == 'individual':
            self.company_category = False
            domain = [('is_company', '=', False)]
        else:
            self.company_category = False
            self.individual_type = False
            domain = []

        return {'domain': {'partner_id': domain}}




    @api.onchange('individual_type')
    def _onchange_individual_type(self):
        """Assign selected individual type tag to partner"""
        if self.partner_id and self.customer_category == 'individual' and self.individual_type:
            self.partner_id.category_id = [(6, 0, [self.individual_type.id])]
        else:
            self.partner_id.category_id = [(6, 0, [])] 

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id and self.model_id.brand_id:
            self.brand_id = self.model_id.brand_id
    


    @api.depends('state')
    def _compute_is_cancelled(self):
        for rec in self:
            rec.is_cancelled = rec.state == 'cancel'

    @api.depends('partner_id.is_company')
    def _compute_customer_category(self):
        for rec in self:
            rec.customer_category = 'company' if rec.partner_id and rec.partner_id.is_company else 'individual'
            

    def _set_customer_category(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_id.is_company = True if rec.customer_category == 'company' else False

    @api.onchange('company_category')
    def _onchange_company_category(self):
        """Assign selected company category to partner's tags"""
        if self.partner_id and self.customer_category == 'company' and self.company_category:
            self.partner_id.category_id = [(6, 0, [self.company_category.id])]
        else:
            self.partner_id.category_id = [(6, 0, [])]


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-detect and set category (company/individual) correctly."""
        for record in self:
            partner = record.partner_id

            # If no partner selected → clear everything
            if not partner:
                record.customer_category = False
                record.company_category = False
                record.individual_type = False
                record.contact_person_id = False
                return

            # CASE 1: Partner is a company
            if partner.is_company:
                record.customer_category = 'company'
                company_tag = partner.category_id.filtered(lambda c: c.is_company_type)
                record.company_category = company_tag[:1] or False
                record.individual_type = False
                record.contact_person_id = False
                return

            # CASE 2: Partner is a contact under a company
            if partner.parent_id:
                record.customer_category = 'company'
                company = partner.parent_id

                company_tag = company.category_id.filtered(lambda c: c.is_company_type)
                record.company_category = company_tag[:1] or False
                record.individual_type = False

                record.contact_person_id = partner
                record.partner_id = company  # set parent company as customer
                return

            # CASE 3: Pure individual (no parent, not a company)
            record.customer_category = 'individual'
            individual_tag = partner.category_id.filtered(lambda c: c.is_individual_type)
            record.individual_type = individual_tag[:1] or False
            record.company_category = False
            record.contact_person_id = False


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
    def _onchange_brand_for_model(self):
        for rec in self:
            rec.model_id = False
            domain = [('brand_id', '=', rec.brand_id.id)] if rec.brand_id else []
            return {'domain': {'model_id': domain}}


                
    @api.onchange('department_id', 'brand_id')
    def _onchange_department_brand(self):
        """Filter unit types, problems, and accessories based on department and brand."""
        for rec in self:
            domain = {}

            # Reset dependent fields (but NOT unit_type_id itself)
            rec.problem_ids = False
            rec.accessory_ids = [(6, 0, [])]

            # ----- Department logic -----
            if rec.department_id:
                domain['unit_type_id'] = [('department_id', '=', rec.department_id.id)]
                domain['problem_ids'] = [('department_id', '=', rec.department_id.id)]


            else:
                domain['unit_type_id'] = []
                domain['problem_ids'] = []

            # ----- Brand logic for accessories -----
            if rec.brand_id and rec.unit_type_id:
                accessory_domain = [
                    ('is_accessory', '=', True),
                    ('unit_type_id', '=', rec.unit_type_id.id),
                    ('brand_id', '=', rec.brand_id.id)
                ]
                rec.accessory_ids = [(6, 0, self.env['product.product'].search(accessory_domain).ids)]

            return {'domain': domain}

    @api.onchange('department_id', 'unit_type_id')
    def _onchange_department_or_unit_type(self):
        """Reset dependent fields and filter problems only by department."""
        for rec in self:
            domain = {}

            # Reset brand and model if department or unit type changes
            rec.brand_id = False
            rec.model_id = False

            # Reset problem and accessories
            rec.problem_ids = False
            rec.accessory_ids = [(6, 0, [])]

            # Filter unit types by department
            if rec.department_id:
                domain['unit_type_id'] = [('department_id', '=', rec.department_id.id)]
            else:
                domain['unit_type_id'] = []

            # Filter problems ONLY by department
            if rec.department_id:
                domain['problem_ids'] = [('department_id', '=', rec.department_id.id)]
            else:
                domain['problem_ids'] = []

            return {'domain': domain}

    @api.onchange('brand_id')
    def _onchange_brand_id_for_model(self):
        if self.brand_id:
            return {
                'domain': {
                    'model_id': [('id', 'in', self.brand_id.product_ids.ids)]
                }
            }
        else:
            return {
                'domain': {
                    'model_id': []
                }
            }

    @api.onchange('brand_id', 'unit_type_id')
    def _onchange_brand_or_unit_type_for_accessories(self):
        """Filter accessories based on brand and unit type."""
        for rec in self:
            domain = [('is_accessory', '=', True)]
            if rec.brand_id:
                domain.append(('brand_id', '=', rec.brand_id.id))
            if rec.unit_type_id:
                domain.append(('unit_type_id', '=', rec.unit_type_id.id))
            return {'domain': {'accessory_ids': domain}}


    # ------------------------
    # Helper: Format Duration
    # ------------------------
    def _format_duration(self, start_time, end_time=None):
        """Format duration between start_time and end_time into Y,M,D,H,M,S"""
        if not start_time:
            return ''
        if not end_time:
            end_time = datetime.now()
        delta = end_time - start_time
        seconds = int(delta.total_seconds())
        years, remainder = divmod(seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if years:
            parts.append(f"{years}y")
        if months:
            parts.append(f"{months}m")
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}min")
        if seconds:
            parts.append(f"{seconds}s")
        return ', '.join(parts) if parts else '0s'
        
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Determine company
            if 'company_id' in vals:
                company = self.env['res.company'].browse(vals['company_id'])
            else:
                company = self.env.company
    
            # Default service type
            service_type = vals.get('service_type', 'carry_in')
    
            # HQ always uses JO sequence
            if company == self.env.ref('base.main_company'):
                seq_code = 'repair.order.HQ'
            else:
                if service_type == 'carry_in':
                    seq_code = f'repair.order.{company.code}.carryin'
                else:
                    seq_code = f'repair.order.{company.code}.onsite'
    
            # Assign sequence
            vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')
    
            # ✅ Ensure unit_type_id exists (avoid NotNullViolation)
            if 'unit_type_id' not in vals or not vals['unit_type_id']:
                # Pick a default unit type if any exists
                default_unit = self.env['repair.unit.type'].search([], limit=1)
                if default_unit:
                    vals['unit_type_id'] = default_unit.id
                else:
                    # Optional: raise a warning in dev if no unit types exist
                    _logger.warning("No default repair.unit.type found. Repair Order created without unit_type_id.")
    
        return super(RepairOrder, self).create(vals_list)
    
        




     

    def write(self, vals):
        """Track changes to Received By and Technician and log in chatter. 
        Also record when a coordinator is first assigned.
        """
        for rec in self:
            changes = []

            # Track when coordinator is first assigned
            if 'coordinator_id' in vals and vals['coordinator_id']:
                if not rec.coordinator_assigned_date:
                    rec.coordinator_assigned_date = fields.Datetime.now()

            # Compare and log Received By changes
            if 'received_by' in vals:
                old = rec.received_by.name or "None"
                new = self.env['res.users'].browse(vals['received_by']).name if vals['received_by'] else "None"
                if old != new:
                    changes.append(f"Coordinator changed from {old} to {new}.")

            if 'endorse_to_tech' in vals:
                new_tech = self.env['res.users'].browse(vals['endorse_to_tech'])

                # If technician is changing WHILE under repair
                if rec.endorse_to_tech and rec.endorse_to_tech != new_tech and rec.state == 'under_repair':

                    # END previous technician aging
                    if rec.current_tech_start and not rec.current_tech_end:
                        rec.current_tech_end = fields.Datetime.now()

                    # Move current → previous
                    rec.previous_technician_id = rec.endorse_to_tech
                    rec.previous_tech_start = rec.previous_tech_start or rec.repair_start_date
                    rec.previous_tech_end = rec.current_tech_end  # stamping same end time

                    # Start new technician aging
                    rec.current_tech_start = fields.Datetime.now()
                    rec.current_tech_end = False  # running





            # Post to chatter if there are any changes
            if changes:
                body = "<br/>".join(changes)
                rec.message_post(body=body)

        return super(RepairOrder, self).write(vals)




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


    @api.constrains('partner_id', 'contact_person_id', 'customer_category', 'company_category', 'individual_type')
    def _check_customer_locked(self):
        for rec in self:
            # Skip new records (no previous data yet)
            if not rec._origin or not rec._origin.id:
                continue

            # Get the previous state from the database, not just from memory
            prev_state = self.env['repair.order'].browse(rec.id).state

            # Only enforce lock if record is already under repair or beyond
            if prev_state in ('under_repair', 'done', 'released'):
                if rec.has_customer_info_changed():
                    raise ValidationError("You cannot modify Customer Info once the repair has started.")


    def has_customer_info_changed(self):
        """Check if customer-related fields have been modified."""
        self.ensure_one()

        old = self.env['repair.order'].browse(self.id)

        return (
            old.partner_id.id != self.partner_id.id or
            old.contact_person_id.id != self.contact_person_id.id or
            old.customer_category != self.customer_category or
            old.company_category.id != getattr(self.company_category, 'id', False) or
            old.individual_type.id != getattr(self.individual_type, 'id', False)
        )
