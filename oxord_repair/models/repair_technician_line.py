from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RepairTechnicianLine(models.Model):
    _name = "repair.technician.line"
    _description = "Repair Technician Line"

    repair_order_id = fields.Many2one(
        'repair.order', string='Repair Order', required=True, ondelete='cascade'
    )
    
    technician_id = fields.Many2one(
        'res.users', string='Technician', required=True,
        domain="[('share','=',False)]"
    )

    start_date = fields.Datetime(string='Start Date', readonly=True)
    end_date = fields.Datetime(string='End Date', readonly=True)
    
    # Aging fields
    aging_seconds = fields.Integer(string='Aging (seconds)', compute='_compute_aging', store=True)
    aging_days = fields.Integer(string='Days', compute='_compute_aging', store=True)
    aging_hours = fields.Integer(string='Hours', compute='_compute_aging', store=True)
    aging_minutes = fields.Integer(string='Minutes', compute='_compute_aging', store=True)
    aging_formatted = fields.Char(string='Aging', compute='_compute_aging')

    action_taken = fields.Text(string="Action Taken")
    remarks = fields.Text(string="Remarks")
        
    @api.constrains('technician_id')
    def _check_technician_readonly(self):
        """Prevent changing technician for existing line."""
        for rec in self:
            if rec.id and rec._origin.technician_id != rec.technician_id:
                raise UserError(_("You cannot change the technician for an existing line."))

    @api.constrains('repair_order_id')
    def _check_add_after_done(self):
        """Prevent creating or editing lines if repair is done."""
        for rec in self:
            if rec.repair_order_id.state == 'done':
                raise UserError(_("Cannot add or modify technician lines for a repair that is already Done."))

    @api.model_create_multi
    def create(self, vals_list):
        records = self.env['repair.technician.line']

        for vals in vals_list:
            repair_id = vals.get('repair_order_id')
            tech_id = vals.get('technician_id')

            if not repair_id or not tech_id:
                records |= super().create(vals)
                continue

            # ❌ Prevent duplicate active technician line
            existing_line = self.search([
                ('repair_order_id', '=', repair_id),
                ('technician_id', '=', tech_id),
                ('end_date', '=', False)
            ], limit=1)

            if existing_line:
                records |= existing_line
                continue

            now = fields.Datetime.now()

            # ✅ End previous active technician(s)
            previous_lines = self.search([
                ('repair_order_id', '=', repair_id),
                ('end_date', '=', False),
            ])
            previous_lines.write({'end_date': now})

            # ✅ Set start_date
            vals.setdefault('start_date', now)

            records |= super().create(vals)

        return records

    def write(self, vals):
        """Prevent changing technician or editing lines for done repairs."""
        for rec in self:
            if rec.repair_order_id.state == 'done':
                raise UserError(_("Cannot modify technician lines for a repair that is Done."))

            if 'technician_id' in vals:
                if rec.id and rec.technician_id != vals['technician_id']:
                    raise UserError(_("You cannot change the technician for an existing line."))

        return super().write(vals)

    @api.depends('start_date', 'end_date')
    def _compute_aging(self):
        """Compute aging dynamically; freeze when line ended or repair done."""
        now = fields.Datetime.now()
        for line in self:
            if not line.start_date:
                line.aging_seconds = 0
                line.aging_days = 0
                line.aging_hours = 0
                line.aging_minutes = 0
                line.aging_formatted = "0s"
                continue

            # Use end_date if exists, otherwise use current time
            end = line.end_date or now
            delta = end - line.start_date
            total_seconds = max(0, int(delta.total_seconds()))

            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            line.aging_seconds = total_seconds
            line.aging_days = days
            line.aging_hours = hours
            line.aging_minutes = minutes

            # Smart formatting
            if days > 0:
                line.aging_formatted = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                line.aging_formatted = f"{hours}h {minutes}m"
            elif minutes > 0:
                line.aging_formatted = f"{minutes}m {seconds}s"
            else:
                line.aging_formatted = f"{seconds}s"
