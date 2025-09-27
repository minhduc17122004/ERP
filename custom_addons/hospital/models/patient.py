from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class HospitalPatient(models.Model):
    _name = 'my.hospital.patient'
    _description = 'Hospital Patient'
    _rec_name = 'name'

    name = fields.Char(string='Patient Name', required=True)
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    note = fields.Text(string='Notes')
    doctor_id = fields.Many2one('res.partner', string='Doctor')

    @api.depends('dob')
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = date.today()
                record.age = relativedelta(today, record.dob).years
            else:
                record.age = 0 