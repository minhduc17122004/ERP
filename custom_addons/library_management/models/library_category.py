from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Thể loại sách'
    _order = 'name'
    _parent_store = True

    name = fields.Char(
        string='Tên thể loại',
        required=True,
        index=True
    )
    
    code = fields.Char(
        string='Mã thể loại',
        required=True,
        index=True
    )
    
    description = fields.Text(
        string='Mô tả'
    )
    
    active = fields.Boolean(
        string='Kích hoạt',
        default=True
    )
    
    parent_id = fields.Many2one(
        'library.category',
        string='Thể loại cha',
        index=True,
        ondelete='cascade'
    )
    
    child_ids = fields.One2many(
        'library.category',
        'parent_id',
        string='Thể loại con'
    )
    
    parent_path = fields.Char(
        index=True
    )
    
    book_ids = fields.One2many(
        'library.book',
        'category_id',
        string='Sách'
    )
    
    book_count = fields.Integer(
        string='Số lượng sách',
        compute='_compute_book_count'
    )
    
    color = fields.Integer(
        string='Màu sắc'
    )
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.book_ids)
    
    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError('Không thể tạo thể loại đệ quy!')
    
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f'[{record.code}] {name}'
            if record.parent_id:
                name = f'{record.parent_id.name} / {name}'
            result.append((record.id, name))
        return result 