from odoo import fields, models, api


class Warranty(models.Model):
    _name = "warranty.property"
    _description = "Warranty Module"
    _rec_name = "sequence_number"

    sequence_number = fields.Char(readonly=True, required=True, copy=False,
                                  default='New')

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code\
                                          ('self.service') or 'New'
            result = super(Warranty, self).create(vals)
        return result

    invoice_id = fields.Many2one('account.move', string="Invoice")

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        # print(self)
        product_ids = self.invoice_id.invoice_line_ids.product_id.ids
        print(self)
        return {'domain': {'product_id': [('id', 'in', product_ids)]}}

    product_id = fields.Many2one('product.product', string="product")

    lot_id = fields.Many2one('stock.lot', string='Lot/Sl.No')

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     print(self)
    #     self.lot_id= self.invoice_id.name


    request_date = fields.Date()
    customer_id = fields.Many2one("res.partner", string="Partner")
    purchase_date = fields.Date( related= 'invoice_id.invoice_date',
                                 string="Purchase Date")

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('to approve', 'To Approve'),
                   ('approved', 'Approved'), ('cancel', 'Cancel')],
        required="TRUE", default='draft')

    class InventoryInherit(models.Model):
        _inherit = "product.template"
        warranty_period = fields.Float()
        warranty_type = fields.Selection(string="Warranty Type", selection=
        [('type_1', '1. Service Warranty'),
         ('type_2', '2. Replacement warranty')])
        has_warranty = fields.Boolean(string="Has Warranty")
