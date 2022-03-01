from odoo import fields, models, api


class EmployeeTransfer(models.Model):
    _name = "employee.transfer"
    _rec_name = "sequence_number"

    sequence_number = fields.Char(readonly=True, required=True, copy=False,
                                  default='New')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    current_company = fields.Char(related="employee_id.company_id.name",
                                  string="Current Company")
    transfer_to_id = fields.Many2one('res.company', string='Transfer To')
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('to approve', 'To Approve'),
                                        ('approved', 'Approved'),
                                        ('canceled', 'Canceled')
                                        ],
                             required="TRUE", default='draft')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code(
                'self.service') or 'New'
        return super(EmployeeTransfer, self).create(vals)

    def action_confirm(self):
        self.state = "to approve"

    def action_approve(self):
        self.state = "approved"
        print(self.employee_id.company_id)
        print(self.transfer_to_id)
        print(self.employee_id)
        if self.transfer_to_id:
            employee_ids = self.env['hr.employee']\
                .search([('company_id', '!=',
                          self.transfer_to_id.id)])
            print(employee_ids)
            for self.employee_id in employee_ids:
                self.employee_id.active = False
                print(self.employee_id.active)
                return

    def action_move_to_draft(self):
        self.state = "draft"

    def action_cancel(self):
        self.state = "canceled"
