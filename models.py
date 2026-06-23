from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FundAllocation(models.Model):
    _name = 'fund.allocation'
    _description = 'Fund Allocation'

    name = fields.Char(string='Project Name', required=True)
    amount = fields.Float(string='Allocated Amount', required=True)
    spent_amount = fields.Float(string='Spent Amount', default=0.0)
    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_remaining', store=True)

    @api.depends('amount', 'spent_amount')
    def _compute_remaining(self):
        for record in self:
            record.remaining_amount = record.amount - record.spent_amount

    @api.constends('spent_amount', 'amount')
    def _check_double_spending(self):
        for record in self:
            if record.spent_amount > record.amount:
                raise ValidationError("Double Spending Alert! You cannot spend more than the allocated budget.")