from odoo import fields, models, api
from odoo.exceptions import UserError


class DiscountLimit(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_limit = fields.Float(string="Discount Limit")

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].set_param("commission.discount",
                                                  self.discount_limit or '')
        super(DiscountLimit, self).set_values()

    @api.model
    def get_values(self):
        res = super(DiscountLimit, self).get_values()
        res['discount_limit'] = self.env['ir.config_parameter'].sudo().\
            get_param("commission.discount", default="")
        print(res)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('discount')
    def _check_discount(self):

        if self.discount:
            monthly_discount = float(self.env['ir.config_parameter'].sudo().
                                     get_param('commission.discount'))
            print(monthly_discount)

            if self.discount > monthly_discount:
                raise UserError('You Exceed The Monthly Discount Limit')
