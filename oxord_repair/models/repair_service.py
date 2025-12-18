from odoo import models, fields

class RepairService(models.Model):
    _name = "repair.service"
    _description = "Repair Service"

    name = fields.Char(string="Service Name", required=True)
    description = fields.Text(string="Description")
    price = fields.Float(string="Price")
    active = fields.Boolean(default=True)
