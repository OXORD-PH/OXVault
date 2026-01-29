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
    aging_seconds = fields.Integer(string='Aging (seconds)', compute='_compute_aging', store=True)
    aging_days = fields.Integer(string='Days', compute='_compute_aging', store=True)
    aging_hours = fields.Integer(string='Hours', compute='_compute_aging', store=True)
    aging_minutes = fields.Integer(string='Minutes', compute='_compute_aging', store=True)
    aging_formatted = fields.Char(string='Aging', compute='_compute_aging', store=True)

    action_taken = fields.Text(string="Action Taken")
    remarks = fields.Text(string="Remarks")
    
    @api.constrains('technician_id')
    def _check_technician_readonly(self):
        """Prevent changing the technician for an existing line."""
        for rec in self:
            if rec.id and rec._origin.technician_id != rec.technician_id:
                raise UserError(_("You cannot change the technician for an existing line."))

    @api.model
    def create(self, vals):
        """Automatically set start_date, end previous active lines, prevent duplicates."""
        
        # Check for existing active line for same technician and repair
        existing_line = self.env['repair.technician.line'].search([
            ('repair_order_id', '=', vals.get('repair_order_id')),
            ('technician_id', '=', vals.get('technician_id')),
            ('end_date', '=', False)
        ], limit=1)
        if existing_line:
            return existing_line  # do not create duplicate
    
        # Set start_date if not provided
        if not vals.get('start_date'):
            vals['start_date'] = fields.Datetime.now()
    
        # End previous active lines for other technicians
        previous_lines = self.env['repair.technician.line'].search([
            ('repair_order_id', '=', vals.get('repair_order_id')),
            ('end_date', '=', False),
            ('technician_id', '!=', vals.get('technician_id')),
        ])
        previous_lines.write({'end_date': fields.Datetime.now()})
    
        return super().create(vals)


    def write(self, vals):
        """Prevent technician change; allow updating other fields safely."""
        if 'technician_id' in vals:
            for rec in self:
                # Prevent changing technician
                if rec.id and rec.technician_id != vals['technician_id']:
                    raise UserError(_("You cannot change the technician for an existing line."))

        # Write other fields normally
        return super().write(vals)

    @api.depends('start_date', 'end_date')
    def _compute_aging(self):
        """Compute aging dynamically; refreshes automatically."""
        for line in self:
            if line.start_date and line.end_date:
                delta = line.end_date - line.start_date
                total_seconds = int(delta.total_seconds())
                line.aging_seconds = total_seconds
                line.aging_days = total_seconds // 86400
                line.aging_hours = (total_seconds % 86400) // 3600
                line.aging_minutes = (total_seconds % 3600) // 60
                line.aging_formatted = f"{line.aging_days}d {line.aging_hours}h {line.aging_minutes}m"
            else:
                line.aging_seconds = 0
                line.aging_days = 0
                line.aging_hours = 0
                line.aging_minutes = 0
                line.aging_formatted = "0d 0h 0m"
