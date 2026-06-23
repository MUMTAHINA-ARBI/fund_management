from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FundAllocation(models.Model):
    _name = 'fund.allocation'
    _description = 'Project Fund Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Gives us the Audit History automatically!

    name = fields.Char(string='Project Name', required=True)
    allocated_amount = fields.Float(string='Total Allocated Amount', required=True, tracking=True)
    
    # Mathematical tracking fields
    assigned_amount = fields.Float(string='Held / Assigned Balance', compute='_compute_balances', store=True)
    spent_amount = fields.Float(string='Spent Balance', compute='_compute_balances', store=True)
    available_amount = fields.Float(string='Available Balance', compute='_compute_balances', store=True)
    
    requisition_ids = fields.One2many('fund.requisition', 'allocation_id', string='Requisitions')

    @api.depends('allocated_amount', 'requisition_ids.amount', 'requisition_ids.state')
    def _compute_balances(self):
        for record in self:
            held = 0.0
            spent = 0.0
            for req in record.requisition_ids:
                if req.state in ['gm_approved', 'md_approved']:
                    held += req.amount
                elif req.state == 'posted':
                    spent += req.amount
            
            record.assigned_amount = held
            record.spent_amount = spent
            record.available_amount = record.allocated_amount - (held + spent)

    # ANTI-DOUBLE-SPENDING CONSTRAINT
    @api.constrains('allocated_amount', 'requisition_ids')
    def _check_over_spending(self):
        for record in self:
            if record.available_amount < 0:
                raise ValidationError(
                    "Double Spending Blocked! The requested requisitions exceed the total allocated budget for this project."
                )


class FundRequisition(models.Model):
    _name = 'fund.requisition'
    _description = 'Fund Requisition'
    _inherit = ['mail.thread']

    allocation_id = fields.Many2one('fund.allocation', string='Project Allocation', ondelete='cascade')
    description = fields.Char(string='Purpose / Expense Head', required=True)
    amount = fields.Float(string='Requested Amount', required=True, tracking=True)
    
    # GM and MD Approval State Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approved', 'GM Approved'),
        ('md_approved', 'MD Approved'),
        ('posted', 'Bills Posted / Spent')
    ], default='draft', string='Status', tracking=True)

    def action_gm_approve(self):
        self.state = 'gm_approved'

    def action_md_approve(self):
        self.state = 'md_approved'

    def action_post_bill(self):
        self.state = 'posted'