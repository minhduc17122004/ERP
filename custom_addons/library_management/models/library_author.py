from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Tác giả'
    _order = 'name'

    name = fields.Char(
        string='Tên tác giả',
        required=True,
        index=True
    )
    
    full_name = fields.Char(
        string='Họ và tên đầy đủ'
    )
    
    birth_date = fields.Date(
        string='Ngày sinh'
    )
    
    death_date = fields.Date(
        string='Ngày mất'
    )
    
    nationality = fields.Char(
        string='Quốc tịch'
    )
    
    biography = fields.Text(
        string='Tiểu sử'
    )
    
    active = fields.Boolean(
        string='Kích hoạt',
        default=True
    )
    
    book_ids = fields.One2many(
        'library.book',
        'author_id',
        string='Sách'
    )
    
    book_count = fields.Integer(
        string='Số lượng sách',
        compute='_compute_book_count'
    )
    
    image = fields.Binary(
        string='Ảnh'
    )
    
    email = fields.Char(
        string='Email'
    )
    
    website = fields.Char(
        string='Website'
    )
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.book_ids)
    
    @api.constrains('birth_date', 'death_date')
    def _check_dates(self):
        for record in self:
            if record.birth_date and record.death_date:
                if record.birth_date > record.death_date:
                    raise ValidationError('Ngày sinh không thể sau ngày mất!')
    
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.nationality:
                name += f' ({record.nationality})'
            result.append((record.id, name))
        return result 