from odoo import models, fields, api
from odoo.exceptions import UserError


class TechnicalReport(models.Model):
    _name = 'technical.report'
    _description = 'Technical Report'

    name = fields.Char(
        string='Technical Report Ref',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
    ], default='draft', tracking=True)

    repair_order_id = fields.Many2one(
        'repair.order',
        string='Repair Order',
        required=True,
    )

    # Related customer fields
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='repair_order_id.partner_id',
        readonly=True
    )
    partner_street = fields.Char(
        string='Address',
        related='repair_order_id.partner_id.street',
        readonly=True
    )
    partner_email = fields.Char(
        string='Email',
        related='repair_order_id.partner_id.email',
        readonly=True
    )
    partner_phone = fields.Char(
        string='Phone',
        related='repair_order_id.partner_id.phone',
        readonly=True
    )

    created_by = fields.Many2one(
        'res.users',
        string='Checked & Prepared by',
        default=lambda self: self.env.user,
        tracking=True
    )


    report_date = fields.Datetime(
        default=fields.Datetime.now,
        readonly=True
    )

    details = fields.Text(string='Action Taken')

    status = fields.Selection([
        ('fixed', 'Unit Fixed'),
        ('not_fixed', 'Unit Not Fixed'),
    ], default='not_fixed', required=True)

    recommendation = fields.Text()
    
    brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        related='repair_order_id.brand_id',
        readonly=True,
        store=True
    )
    
    model_id = fields.Many2one(
        'product.product',
        string='Model',
        related='repair_order_id.model_id',
        readonly=True,
        store=True
    )
    
    accessory_ids = fields.Many2many(
        'product.template',
        string='Accessories',
        related='repair_order_id.accessory_ids',
        readonly=True
    )

    
    serial = fields.Char(
        string='Serial Number',
        related='repair_order_id.serial',
        readonly=True
    )

    
    # pop_date = fields.Datetime(
    #     string='Isolation Date',
    #     related='repair_order_id.pop_date',
    #     readonly=True
    # )

    noted_by_id = fields.Many2one(
        'res.users',
        string="Noted By (Technical Head)",
        readonly=True,
        tracking=True
    )


    # Existing fields...
    problem_ids = fields.Many2many(
        'repair.problem',
        string='Problems',
        related='repair_order_id.problem_ids',
        readonly=True
    )

    problem_note = fields.Text(string="Additional Notes on Problems")


    def action_validate(self):
        if not self.env.user.has_group('oxord_repair.group_technical_head'):
            raise UserError(
                "Only the Technical Head can validate this Technical Report."
            )
    
        for report in self:
            if report.state == 'validated':
                continue
    
            report.write({
                'noted_by_id': self.env.user.id,
                'state': 'validated',
            })

    
    
    @api.model
    def create(self, vals):
        # Handle list of dicts (bulk create)
        if isinstance(vals, list):
            res = []
            for v in vals:
                if v.get('name', 'New') == 'New':
                    v['name'] = self.env['ir.sequence'].next_by_code('technical.report') or 'New'
                res.append(super(TechnicalReport, self).create(v))
            return self.browse([r.id for r in res])
        else:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('technical.report') or 'New'
            return super(TechnicalReport, self).create(vals)
