from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Sách'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Tên sách',
        required=True,
        index=True,
        tracking=True
    )
    
    code = fields.Char(
        string='Mã sách',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    isbn = fields.Char(
        string='ISBN',
        size=13,
        help='Mã số sách tiêu chuẩn quốc tế'
    )
    
    author_id = fields.Many2one(
        'library.author',
        string='Tác giả',
        required=True,
        tracking=True
    )
    
    category_id = fields.Many2one(
        'library.category',
        string='Thể loại',
        required=True,
        tracking=True
    )
    
    publisher = fields.Char(
        string='Nhà xuất bản'
    )
    
    publication_date = fields.Date(
        string='Ngày xuất bản'
    )
    
    edition = fields.Char(
        string='Phiên bản'
    )
    
    language = fields.Selection([
        ('vi', 'Tiếng Việt'),
        ('en', 'Tiếng Anh'),
        ('fr', 'Tiếng Pháp'),
        ('de', 'Tiếng Đức'),
        ('es', 'Tiếng Tây Ban Nha'),
        ('other', 'Khác'),
    ], string='Ngôn ngữ', default='vi')
    
    pages = fields.Integer(
        string='Số trang'
    )
    
    price = fields.Float(
        string='Giá tiền',
        digits=(16, 2)
    )
    
    description = fields.Text(
        string='Mô tả'
    )
    
    summary = fields.Html(
        string='Tóm tắt'
    )
    
    state = fields.Selection([
        ('available', 'Có sẵn'),
        ('borrowed', 'Đã mượn'),
        ('lost', 'Thất lạc'),
        ('damaged', 'Hư hỏng'),
        ('maintenance', 'Bảo trì'),
    ], string='Trạng thái', default='available', required=True, tracking=True)
    
    active = fields.Boolean(
        string='Kích hoạt',
        default=True
    )
    
    image = fields.Binary(
        string='Ảnh bìa'
    )
    
    location = fields.Char(
        string='Vị trí',
        help='Vị trí đặt sách trong thư viện'
    )
    
    borrowing_ids = fields.One2many(
        'library.borrowing',
        'book_id',
        string='Lịch sử mượn'
    )
    
    current_borrowing_id = fields.Many2one(
        'library.borrowing',
        string='Đang mượn',
        compute='_compute_current_borrowing'
    )
    
    borrowing_count = fields.Integer(
        string='Số lần mượn',
        compute='_compute_borrowing_count'
    )
    
    rating = fields.Float(
        string='Đánh giá',
        digits=(3, 2),
        help='Đánh giá trung bình từ 0-5 sao'
    )
    
    tags = fields.Char(
        string='Từ khóa',
        help='Các từ khóa cách nhau bởi dấu phẩy'
    )
    
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('library.book') or _('New')
        return super(LibraryBook, self).create(vals)
    
    @api.depends('borrowing_ids', 'borrowing_ids.state')
    def _compute_current_borrowing(self):
        for record in self:
            current_borrowing = record.borrowing_ids.filtered(
                lambda b: b.state == 'borrowed'
            )
            record.current_borrowing_id = current_borrowing[0] if current_borrowing else False
    
    @api.depends('borrowing_ids')
    def _compute_borrowing_count(self):
        for record in self:
            record.borrowing_count = len(record.borrowing_ids)
    
    @api.constrains('isbn')
    def _check_isbn(self):
        for record in self:
            if record.isbn:
                if len(record.isbn) not in [10, 13]:
                    raise ValidationError('ISBN phải có 10 hoặc 13 ký tự!')
                
                # Kiểm tra trùng lặp
                existing = self.search([
                    ('isbn', '=', record.isbn),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f'ISBN {record.isbn} đã tồn tại!')
    
    @api.constrains('pages')
    def _check_pages(self):
        for record in self:
            if record.pages and record.pages <= 0:
                raise ValidationError('Số trang phải lớn hơn 0!')
    
    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price and record.price < 0:
                raise ValidationError('Giá tiền không thể âm!')
    
    def action_set_available(self):
        """Đặt trạng thái sách thành có sẵn"""
        self.state = 'available'
        self.message_post(body='Sách đã được đặt thành trạng thái có sẵn')
    
    def action_set_maintenance(self):
        """Đặt trạng thái sách thành bảo trì"""
        self.state = 'maintenance'
        self.message_post(body='Sách đang được bảo trì')
    
    def action_set_damaged(self):
        """Đặt trạng thái sách thành hư hỏng"""
        self.state = 'damaged'
        self.message_post(body='Sách đã bị hư hỏng')
    
    def action_set_lost(self):
        """Đặt trạng thái sách thành thất lạc"""
        self.state = 'lost'
        self.message_post(body='Sách đã thất lạc')
    
    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            if record.author_id:
                name += f' - {record.author_id.name}'
            result.append((record.id, name))
        return result 