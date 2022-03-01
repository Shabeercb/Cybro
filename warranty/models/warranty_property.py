from odoo import fields, models, api
from datetime import timedelta, datetime


class Warranty(models.Model):
    _name = "warranty.property"
    _description = "Warranty Module"
    _rec_name = "sequence_number"

    sequence_number = fields.Char(readonly=True, required=True, copy=False,
                                  default='New')
    invoice_id = fields.Many2one('account.move', string="Invoice",
                                 required=True)
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
                                        (
                                        'product received', 'Product Received'),
                                        ('done', 'Done'),
                                        ('cancel', 'Canceled'),
                                        ],
                             required="TRUE", default='draft')
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    warranty_info_id = fields.Many2one('account.move',
                                       string='Warranty Info Id')

    # sequence_number

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code(
                'self.service') or 'New'
        return super(Warranty, self).create(vals)

    # invoice_id

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        # print(self)
        product_ids = self.invoice_id.invoice_line_ids.product_id.ids
        return {'domain': {'product_id': [('id', 'in', product_ids)]}}

    # warranty_expire_date

    @api.depends('purchase_date', 'product_id', 'product_id.warranty_period')
    def _compute_warranty_expire_date(self):

        for rec in self:
            rec.warranty_expire_date = False

            if rec.purchase_date and rec.product_id.warranty_period:
                rec.warranty_expire_date = rec.purchase_date + timedelta(
                    days=int(rec.product_id.warranty_period))

    # button submit

    def action_submit(self):
        self.state = "to approve"

    # button_cancel

    def action_cancel(self):
        self.state = "cancel"

    # button_to_approve, stock_move

    def action_to_approve(self):
        self.state = 'product received'
        # # print(self.product_id.warranty_type)
        # print(self.product_id.uom_id.id)
        if self.product_id.warranty_type == "type_2":
            stock_move = self.env['stock.move'].create({
                'origin': self.sequence_number,
                'name': 'Warranty Replacement',
                'date': self.request_date,
                'product_id': self.product_id.id,
                'location_id':
                    self.env.ref('stock.stock_location_customers').id,
                'location_dest_id':
                    self.env.ref('warranty.warranty_storage_location').id,
                'company_id': self.env.user.company_id.id,
                'product_uom_qty': '1',
                'product_uom': self.product_id.uom_id.id,
                'procure_method': 'make_to_order',
            })
            result = stock_move
            self.stock_move_id = stock_move.id
            return result

        elif self.product_id.warranty_type == "type_1":
            return self.env['stock.move'].create({
                'origin': self.sequence_number,
                'name': 'Warranty Service',
                'date': self.request_date,
                'product_id': self.product_id.id,
                'location_id':
                    self.env.ref('warranty.warranty_storage_location').id,
                'location_dest_id':
                    self.env.ref('stock.stock_location_customers').id,
                'company_id': self.env.user.company_id.id,
                'product_uom_qty': '1',
                'product_uom': self.product_id.uom_id.id,
                'procure_method': 'make_to_order',
            })

    # button_return_product

    def action_to_return_product(self):
        self.state = 'done'
        if self.product_id.warranty_type == "type_2":
            return self.env['stock.move'].create({
                'origin': self.sequence_number,
                'name': 'Warranty Replacement Return',
                'date': self.request_date,
                'product_id': self.product_id.id,
                'location_id':
                    self.env.ref('warranty.warranty_storage_location').id,
                'location_dest_id':
                    self.env.ref('stock.stock_location_customers').id,
                'company_id': self.env.user.company_id.id,
                'product_uom_qty': '1',
                'product_uom': self.product_id.uom_id.id,
                'procure_method': 'make_to_order',
            })

        elif self.product_id.warranty_type == "type_1":
            return self.env['stock.move'].create({
                'origin': self.sequence_number,
                'name': 'Warranty Service Return',
                'date': self.request_date,
                'product_id': self.product_id.id,
                'location_id':
                    self.env.ref('stock.stock_location_customers').id,
                'location_dest_id':
                    self.env.ref('warranty.warranty_storage_location').id,
                'company_id': self.env.user.company_id.id,
                'product_uom_qty': '1',
                'product_uom': self.product_id.uom_id.id,
                'procure_method': 'make_to_order',
            })

    # button_move_to_draft

    def action_move_to_draft(self):
        self.state = "draft"

    def action_create_invoice(self):
        for rec in self:
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': rec.customer_id.id,
                'payment_reference': rec.sequence_number,
                'invoice_date': (datetime.now()).date(),
                'invoice_line_ids': [(0, 0, {
                    'product_id': rec.product_id,
                    'quantity': 1.0,
                    'name': rec.sequence_number,
                    'product_uom_id': rec.product_id.uom_id.id,
                })]
            })
            rec.invoice_id = invoice.id
            print(invoice.id)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoices',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'domain': [('payment_reference', '=', self.sequence_number)],
                'context': "{'create': False}"
            }

    # smart_button

    def action_stock_move(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Move',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'stock.move',
            'res_id': self.stock_move_id.id,
            'domain': [('origin', '=', self.sequence_number)],
            'context': "{'create': False}"
        }

    # Invoice smart button

    def action_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'domain': [('payment_reference', '=', self.sequence_number)],
            'context': "{'create': False ,}"
        }


class InventoryInherit(models.Model):
    _inherit = "product.template"

    warranty_period = fields.Float()
    warranty_type = fields.Selection(
        string="Warranty Type",
        selection=[('type_1', '1.Service Warranty'),
                   ('type_2', '2.Replacement ' 'warranty')])
    has_warranty = fields.Boolean(string="Has Warranty")


class InvoiceInherit(models.Model):
    _inherit = "account.move"

    warranty_info_lines_ids = fields.One2many('warranty.property',
                                              'invoice_id',
                                              string='Warranty Info')


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    stock_move = fields.Char(string="Stock Move")


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.onchange('product_id')
    def onchange_product_id(self):

        if self.product_id:
            print(self.product_id)
            for rec in self:
                location = self.env['stock.putaway.rule'].search(
                    [('product_id', '=', self.product_id.id)])
                print(location)
                rec.location_id = location.location_out_id
