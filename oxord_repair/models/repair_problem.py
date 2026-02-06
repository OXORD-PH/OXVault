from odoo import models, fields, api
from odoo.exceptions import ValidationError

class RepairProblem(models.Model):
    _name = 'repair.problem'
    _description = 'Repair Service Price List'

    name = fields.Char(string='Repair Service Name', required=True)
    code = fields.Char(
        string="Service Code",
        readonly=True,
        copy=False,
        index=True
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        help='Department this problem belongs to (e.g., DTLP, HHP, etc.)'
    )

    unit_type_id = fields.Many2one(
        'repair.unit.type',
        string="Unit Type",
        domain="[('department_id', '=', department_id)]",
        required=True,
        help="Type of unit (Desktop, Laptop, Phone, Printer, etc.)"
    )

    category = fields.Selection(
        [
            ('minor', 'Minor'),
            ('major', 'Major'),
            ('critical', 'Critical')
        ],
        string='Category'
    )

    estimated_cost = fields.Float(
        string='Estimated Cost',
        digits=(12, 2),
        help='Estimated repair cost'
    )


    product_id = fields.Many2one(
        'product.product',
        string='Related Product',
        domain="[('type', '=', 'service')]",
        help='The product/service that will be used in quotations for this problem'
    )

    active = fields.Boolean(string='Active', default=True)  # <-- add this
    
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else rec.name

    @api.constrains('department_id', 'unit_type_id')
    def _check_unit_type_department(self):
        for rec in self:
            if rec.unit_type_id and rec.unit_type_id.department_id != rec.department_id:
                raise ValidationError(
                    "The selected Unit Type does not belong to the chosen Department."
                )
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
    
        for rec in records:
            if not rec.code and rec.unit_type_id:
                prefix = rec.unit_type_id.code_prefix
    
                count = self.search_count([
                    ('unit_type_id', '=', rec.unit_type_id.id),
                    ('id', '<=', rec.id),
                ])
    
                rec.code = f"{prefix}{str(count).zfill(3)}"
    
        return records

    # -------------------------
    # Enable searching by code
    # -------------------------
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
    
        # Search by name normally
        recs = self.search([('name', operator, name)] + args, limit=limit)
        # Also search by code if input matches
        recs_code = self.search([('code', operator, name)] + args, limit=limit)
    
        # Combine results, removing duplicates
        recs = (recs | recs_code).sorted(key=lambda r: r.id)
        
        # Return list of (id, display_name) tuples using your custom display_name
        return [(r.id, r.display_name) for r in recs]
