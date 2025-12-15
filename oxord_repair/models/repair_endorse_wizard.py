from odoo import models, fields, api

class RepairEndorseWizard(models.TransientModel):
    _name = "repair.endorse.wizard"
    _description = "Technician Endorse Wizard"

    repair_id = fields.Many2one("repair.order", required=True)
    new_technician_id = fields.Many2one("res.users", string="New Technician", required=True)

    def action_apply(self):
        self.repair_id.set_new_technician(self.new_technician_id)
        return {"type": "ir.actions.act_window_close"}
