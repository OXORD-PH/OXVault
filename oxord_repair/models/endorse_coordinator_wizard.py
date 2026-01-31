from odoo import models, fields, api

class EndorseCoordinatorWizard(models.TransientModel):
    _name = 'endorse.coordinator.wizard'
    _description = 'Endorse Repair Order to Coordinator'

    repair_id = fields.Many2one('repair.order', string="Repair Order", required=True)
    coordinator_id = fields.Many2one('res.users', string="Coordinator", required=True)
    remarks = fields.Text(string="Remarks")

    def action_endorse(self):
        for wizard in self:
            repair = wizard.repair_id
            now = fields.Datetime.now()
    
            # Assign coordinator
            repair.coordinator_id = wizard.coordinator_id
            if not repair.coordinator_assigned_date:
                repair.coordinator_assigned_date = now
    
            # ✅ STOP TECHNICIAN AGING FIRST
            active_lines = repair.technician_line_ids.filtered(lambda l: not l.end_date)
            active_lines.write({'end_date': now})
    
            # ✅ NOW mark repair as done
            repair.repair_end_date = now
            repair.state = 'done'
    
            # Chatter
            repair.message_post(
                body=f"Repair endorsed and marked as <b>Done</b> by {self.env.user.name}."
            )
    
        return {'type': 'ir.actions.act_window_close'}
