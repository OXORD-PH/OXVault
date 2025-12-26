from odoo import models, fields, api

class EndorseCoordinatorWizard(models.TransientModel):
    _name = 'endorse.coordinator.wizard'
    _description = 'Endorse Repair Order to Coordinator'

    repair_id = fields.Many2one('repair.order', string="Repair Order", required=True)
    coordinator_id = fields.Many2one('res.users', string="Coordinator", required=True)
    remarks = fields.Text(string="Remarks")

    def action_endorse(self):
        """Assign coordinator, post remarks, update coordinator aging, and set state to done."""
        for wizard in self:
            repair = wizard.repair_id

            # Store old coordinator for message
            old_coordinator = repair.coordinator_id.name if repair.coordinator_id else "None"

            # Assign new coordinator
            repair.coordinator_id = wizard.coordinator_id

            # Stamp coordinator assigned date if not already set
            if not repair.coordinator_assigned_date:
                repair.coordinator_assigned_date = fields.Datetime.now()

            # Recompute aging durations immediately
            repair._compute_aging_durations()
            repair.invalidate_recordset(['coordinator_to_release_days', 'coordinator_to_release_formatted'])

            # Post message to chatter
            body = f"Coordinator changed from <b>{old_coordinator}</b> to <b>{wizard.coordinator_id.name}</b>."
            if wizard.remarks:
                body += f"<br/><b>Remarks:</b> {wizard.remarks}"
            repair.message_post(body=body)

            # Move repair order state to 'done' after coordinator is assigned
            if repair.state != 'done':
                repair.repair_end_date = fields.Datetime.now()
                repair.state = 'done'

        # Close the wizard window
        return {'type': 'ir.actions.act_window_close'}
