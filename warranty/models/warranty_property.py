from odoo import fields, models, api
from datetime import datetime, timedelta


class Warranty(models.Model):
    _name = "warranty.property"
    _description = "Warranty Module"
    _rec_name = "sequence_number"

    sequence_number = fields.Char(readonly=True, required=True, copy=False,
                                  default='New')
    invoice_id = fields.Many2one('account.move', string="Invoice")
    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.lot', string='Lot/Sl.No')
    request_date = fields.Date()
    customer_id = fields.Many2one("res.partner", string="Partner")
    purchase_date = fields.Date(related='invoice_id.invoice_date',
                                string="Purchase Date")
    warranty_expire_date = fields.Date(string="Warranty Expire Date",
                                       compute="_compute_warranty_expire_date")
    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('to approve', 'To Approve'),
                                        ('approved', 'Approved'),
                                        ('cancel', 'Cancel')],
                             required="TRUE", default='draft')

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code(
                'self.service') or 'New'
            result = super(Warranty, self).create(vals)
        return result

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        # print(self)
        product_ids = self.invoice_id.invoice_line_ids.product_id.ids
        return {'domain': {'product_id': [('id', 'in', product_ids)]}}

    @api.depends('purchase_date', 'product_id', 'product_id.warranty_period')
    def _compute_warranty_expire_date(self):

        for rec in self:
            rec.warranty_expire_date = False

            if rec.purchase_date and rec.product_id.warranty_period:
                rec.warranty_expire_date = rec.purchase_date + timedelta(
                     days=int(rec.product_id.warranty_period))

    def action_submit(self):
        self.state = "to approve"

    def action_cancel(self):
        self.state = "cancel"

    def action_to_approve(self):
        self.state = "approved"

    def action_move_to_draft(self):
        self.state = "draft"


class InventoryInherit(models.Model):
    _inherit = "product.template"

    warranty_period = fields.Float()
    warranty_type = fields.Selection(string="Warranty Type",
                                     selection=[('type_1', '1.Service Warranty'),
                                                ('type_2', '2.Replacement '
                                                           'warranty')])
    has_warranty = fields.Boolean(string="Has Warranty")

