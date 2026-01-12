from odoo import models, fields

class RepairUnitType(models.Model):
    _name = 'repair.unit.type'
    _description = 'Repair Unit Type'
    _order = 'department_id, name'

    name = fields.Char(
        string="Unit Type",
        required=True
    )

    department_id = fields.Many2one(
        'hr.department',
        string="Department",
        required=True,
        ondelete='cascade'
    )
    
    code_prefix = fields.Char(
        string="Code Prefix",
        required=True,
        help="Prefix used for repair service codes (e.g. L for Laptop)"
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'repair_unit_type_unique',
            'unique(name, department_id)',
            'This Unit Type already exists in this Department.'
        )
    ]
