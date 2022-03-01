from odoo import models, fields, _
import openpyxl
import base64
from io import BytesIO
from odoo.exceptions import UserError


class ImportOrder(models.TransientModel):
    _name = "import.order"

    data = fields.Binary('file')

    def action_import_popup(self):
        try:
            active_id = self.env.context.get('active_id')
            print("active_id", active_id)
            print("self=", self)
            wb = openpyxl.load_workbook(
                filename=BytesIO(base64.b64decode(self.data)), read_only=True)
            print("WB=", wb)
            ws = wb.active
            for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,
                                       max_col=None, values_only=True):
                search = self.env['sale.order.line'].search(
                    [('name', '=', record[0])])
                print("search=", search)
                print('REC', record[0])
                print(record[1])
                print(record[2])
                print(record[3])
                print(record[4])

                if not search:
                    print({

                        'product_id': self.env['product.template'].search(
                            [('name', '=', record[0])]).id,
                        # 'product_id': record[0],
                        'name': record[2],
                        'product_uom_qty': record[1],
                        'price_unit': record[3],
                        'product_uom': self.env['uom.uom'].search([('name', '=',
                                                                    record[4])]).id,
                        'order_id': active_id,
                        # 'customer_lead': "3",
                        'display_type': False,
                        'tax_id': False,
                    })

                    self.env['sale.order.line'].create({
                        'product_id': self.env['product.template'].search(
                            [('name', '=', record[0])]).id,
                        # 'product_id': 0,
                        'name': record[2],
                        'product_uom_qty': record[1],
                        'price_unit': record[3],
                        'product_uom': self.env['uom.uom'].search([('name', '=',
                                                                    record[4])]).id,
                        'order_id': active_id,
                        'display_type': False,
                        'tax_id': False,
                    })
        except:
            raise UserError(_('Please insert a valid file'))


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    def action_import(self):
        # print(self)

        return {
            'name': 'Import Order line',
            'domain': [],
            'res_model': 'import.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'new',
        }

        #     name = record[0]
        #     product_id = self.env['product.product'].search(
        #         [('name', '=', name)])
        #     if not product_id:
        #         raise UserError(
        #             _("There is no product with code %s.") % name)
        #     uom = record[4]
        #     product_uom = self.env['uom.uom'].search(
        #         [('name', '=', uom)])
        #     if not product_uom:
        #         raise UserError(_("There is no uom with name %s.") % uom)
        #     line_ids = {
        #         'product_id': product_id.id,
        #         'name': record[2],
        #         'product_uom_qty': float(record[1]),
        #         'price_unit': record[3],
        #         'product_uom': product_uom.id
        # #     }
        #     print(line_ids)
        # return line_ids

        # except:
        #     raise UserError(_('Please insert a valid file'))

        # self.env['sale.order'].create({
        #     'product_id': record[0],
        #     'name': record[2],
        #     'product_uom_qty': record[1],
        #     'price_unit': record[3],
        #     'product_uom': product_uom.id
        #
        # })

    # # try:
    # fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    # print("fp", fp)
    # fp.write(binascii.a2b_base64(self.data))
    # # print("fp write",fp.write(binascii.a2b_base64(self.data)))
    # fp.seek(0)
    # book = xlrd.open_workbook(fp.name)
    # print("book", book)
    # # print("book1",StringIO(self.data))
    #
    # print("book", book)
    # # except FileNotFoundError:
    # #     raise UserError(
    # #         'No such file or directory found. \n%s.' % self.data)
    # # except xlrd.biffh.XLRDError:
    # #     raise UserError('Only excel files are supported.')
    # for sheet in book.sheets():
    #     try:
    #         line_vals = []
    #         if sheet.name == 'Sheet1':
    #             for row in range(sheet.nrows):
    #                 if row >= 1:
    #                     row_values = sheet.row_values(row)
    #                     print("row val", row_values)
    #                     vals = self._create_order_lines(row_values)
    #                     line_vals.append((0, 0, vals))
    #                 if line_vals:
    #                     search.update({
    #                         'order_line': line_vals
    #                     })
    #     except IndexError:
    #         pass

    # # print('name=',self.name)
    # print('data=', self.data)
    # try:
    #     fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    #     print('fp=', fp)
    #     print(self.data)
    #     fp.write(binascii.a2b_base64(self.data))
    #     print('fp.write', fp.write(binascii.a2b_base64(self.data)))
    #     fp.seek(0)
    #     print('fp.seek=', fp.seek(0))
    #     vals = {}
    #     print('aaaaaaaaaaaaaaaaaaaaaaa')
    #     print('1', fp.name)
    #
    #     workbook = xlrd.open_workbook(filename=fp.name)
    #
    #     print('bbbbbbbbbbbbbbbbbbbbbbbbbb')
    #     print('workbook=', workbook)
    #     print('add', fp.name)
    #     sheet = workbook.sheet_by_index(0)
    #     print('sheet', sheet)
    # except:
    #     raise Warning("File is not Valid!")
    # for row in range(sheet.nrows):
    #     if row >= 1:
    #         row_vals = sheet.row_values(row)
    #         vals = {
    #             'product_id': row_vals[1],
    #             'name': row_vals[2],
    #             'product_uom_qty': float(row_vals[3]),
    #             # 'product_uom': row_vals[4],
    #             'price_unit': row_vals[4],
    #             # 'order_id': self.
    #         }
    #         self.env['sale.order.line'].create(vals)
    #
    #

    # file_name = self.name.lower()
    # for data_file in self.data:
    #     file_name = data_file.name.lower()
    #     if file_name.strip().endswith('.xlsx'):
    #         try:
    #             fp = tempfile.NamedTemporaryFile(delete=False,
    #                                              suffix=".xlsx")
    #             fp.write(binascii.a2b_base64(data_file.datas))
    #             fp.seek(0)
    #             values = {}
    #             workbook = xlrd.open_workbook(fp.name)
    #             sheet = workbook.sheet_by_index(0)
    #         except:
    #             raise UserWarning("Invalid file!")
    #         vals_list = []
    #         for row_no in range(sheet.nrows):
    #             val = {}
    #             values = {}
    #             if row_no <= 0:
    #                 fields = map(lambda row: row.value.encode('utf-8'),
    #                              sheet.row(row_no))
    #             else:
    #                 line = list(map(
    #                     lambda row: isinstance(row.value,
    #                                            bytes) and row.value.encode(
    #                         'utf-8') or str(
    #                         row.value), sheet.row(row_no)))
    #                 vals={
    #                         'product_id': line[1],
    #                         'name': line[2],
    #                         'product_uom_qty': line[3],
    #                         'product_uom': line[4],
    #                         'price_unit': line[5]
    # #
    #                 }
    #                 self.env['sale.order.line'].create(vals)
    #                 # vals_list.append((0, 0, values))

    #     fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    #     fp.write(binascii.a2b_base64(self.name))
    #     fp.seek(0)
    #     vals = {}
    #     workbook = xlrd.open_workbook(fp.name)
    #     sheet = workbook.sheet_by_index(0)
    #     print(fp)
    # except:
    #     raise Warning("File nott Valid")
    #     file = base64.b64decode(self.name)
    # for row_no in range(sheet.nrows):
    #     val = {}
    #     values = {}
    #     if row_no <= 0:
    #         fields = map(lambda row: row.value.encode('utf-8'),
    #                      sheet.row(row_no))

#
#    # def import_file(self):
#    #  raise Warning(_("File not Valid"))
#
#
# sale_order_view = False
# if file_name.strip().endswith('.xlsx'):
#     try:
#         fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
#
#     except:
#         raise UserError('couldnt create file')
#     try:
#         fp.write(binascii.a2b_base64(self.data))
#
#     except:
#         raise UserError('couldnt write data')
#     try:
#         fp.seek(0)
#     except:
#         raise UserError('couldnt seek 0')
#     values = {}
#     try:
#         workbook = xlrd.open_workbook(fp.name)
#     except:
#         raise UserError(
#             f'couldnt create book object {fp.name}, for the following data: {self.data}')
#     try:
#         sheet = workbook.sheet_by_index(0)
#     except:
#         raise UserError('couldnt create sheet object')
#     # raise UserError(_("Invalid file!"))
#     # except:

# vals = {

# }
