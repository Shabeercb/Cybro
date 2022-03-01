from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pos_session_id = fields.Many2one('pos.session', string="POS Session",
                                     default=lambda self: self.env['pos.session']
                                     .search([('state', '=', 'opened')]))

    def action_pay(self):
        print(self)
        return {
            'name': 'Payment',
            'domain': [],
            'res_model': 'payment.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'new',
        }


class PaymentWizard(models.TransientModel):
    _name = "payment.wizard"

    method_id = fields.Many2one('pos.payment.method', string="Payment Methode")
    total_amount_id = fields.Many2one('')


