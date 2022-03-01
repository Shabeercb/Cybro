from odoo import fields, models, api
import math
from datetime import *


class HrShift(models.Model):
    _name = "hr.shift"

    name = fields.Char(string="Name")
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    shift_id = fields.Many2one('hr.shift', string="Shift")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    late = fields.Boolean(string="Late Check In")
    early = fields.Boolean(string="Early Check Out")
    check_out_time = fields.Float(string="Check Out Time",
                                  _compute="_compute_check_out_time")
    check_in_time = fields.Float(string="Check In Time",
                                 _compute="_compute_check_in_time")

    @api.depends('check_in')
    def _compute_check_in_time(self):
        for rec in self:
            rec.check_in_time = False
            if rec.check_in:
                rec.check_in_time = rec.check_in.time()

    @api.depends('check_out')
    def _compute_check_out_time(self):
        for rec in self:
            rec.check_out_time = False
            if rec.check_out:
                rec.check_out_time = rec.check_out.time()

    @api.model
    def create(self, vals):
        result = super(HrAttendance, self).create(vals)
        shift = result.employee_id.shift_id
        print(shift)
        # print(result.employee_id.shift_id.start_time)
        # print(result.employee_id.shift_id.end_time)
        # checked_in = vals.check_in.strptime(vals.check_in, "%H:%M")
        # print(checked_in)
        # print(float(str(result.check_in.time())))
        minutes, hours = math.modf(shift.start_time)
        print(hours)
        minutes = minutes * 60
        print(minutes)
        date = datetime.now()
        print(date)
        checked_in = datetime.strptime(str(result.check_in.time()), "%H:%M:%S")
        print(checked_in)
        print(checked_in.hour)
        print(checked_in.minute)

        if hours < checked_in.hour:
            result.late = True
        elif hours == checked_in.hour:
            if minutes < checked_in.minute:
                result.late = True
        if result.check_out:
            minutes_l, hours_l = math.modf(shift.end_time)
            print(hours_l)
            minutes_l = minutes * 60
            print(minutes_l)
            # date = datetime.now()
            print(date)
            checked_out = datetime.strptime(str(result.check_out.time()),
                                            "%H:%M:%S")
            print(checked_out)
            print(checked_out.hour)
            print(checked_out.minute)
            if hours_l > checked_out.hour:
                result.early = True
            elif hours_l == checked_out.hour:
                if minutes_l > checked_out.minute:
                    result.early = True

        return result














