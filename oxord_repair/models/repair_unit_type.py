from odoo import models, fields

class RepairUnitType(models.Model):
    _name = 'repair.unit.type'
    _description = 'Repair Unit Type'

    name = fields.Char(string="Unit Type", required=True)
    department_id = fields.Many2one(
        'hr.department',
        string="Department",
        required=True,
        domain="[('name','in',['DTLP','HHP','PCAV','PJT'])]",
        help="Select the department for this unit type"
    )
    active = fields.Boolean(string="Active", default=True)
