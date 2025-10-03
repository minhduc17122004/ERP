from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Thành viên thư viện'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Họ và tên',
        required=True,
        index=True,
        tracking=True
    )
    
    code = fields.Char(
        string='Mã thành viên',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        tracking=True
    )
    
    phone = fields.Char(
        string='Số điện thoại',
        tracking=True
    )
    
    mobile = fields.Char(
        string='Điện thoại di động'
    )
    
    address = fields.Text(
        string='Địa chỉ'
    )
    
    birth_date = fields.Date(
        string='Ngày sinh'
    )
    
    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    ], string='Giới tính')
    
    member_type = fields.Selection([
        ('student', 'Sinh viên'),
        ('teacher', 'Giáo viên'),
        ('staff', 'Nhân viên'),
        ('external', 'Bên ngoài'),
    ], string='Loại thành viên', required=True, default='student', tracking=True)
    
    student_id = fields.Char(
        string='Mã sinh viên/nhân viên'
    )
    
    department = fields.Char(
        string='Khoa/Phòng ban'
    )
    
    registration_date = fields.Date(
        string='Ngày đăng ký',
        default=fields.Date.context_today,
        required=True
    )
    
    expiry_date = fields.Date(
        string='Ngày hết hạn',
        compute='_compute_expiry_date',
        store=True
    )
    
    state = fields.Selection([
        ('active', 'Hoạt động'),
        ('suspended', 'Tạm ngưng'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Hủy bỏ'),
    ], string='Trạng thái', default='active', required=True, tracking=True)
    
    active = fields.Boolean(
        string='Kích hoạt',
        default=True
    )
    
    image = fields.Binary(
        string='Ảnh đại diện'
    )
    
    borrowing_ids = fields.One2many(
        'library.borrowing',
        'member_id',
        string='Lịch sử mượn sách'
    )
    
    current_borrowing_ids = fields.One2many(
        'library.borrowing',
        'member_id',
        string='Đang mượn',
        domain=[('state', '=', 'borrowed')]
    )
    
    borrowing_count = fields.Integer(
        string='Tổng số lần mượn',
        compute='_compute_borrowing_count'
    )
    
    current_borrowing_count = fields.Integer(
        string='Số sách đang mượn',
        compute='_compute_current_borrowing_count'
    )
    
    max_borrowing_limit = fields.Integer(
        string='Giới hạn mượn sách',
        compute='_compute_max_borrowing_limit'
    )
    
    overdue_count = fields.Integer(
        string='Số sách quá hạn',
        compute='_compute_overdue_count'
    )
    
    fine_amount = fields.Float(
        string='Số tiền phạt',
        compute='_compute_fine_amount',
        digits=(16, 2)
    )
    
    notes = fields.Text(
        string='Ghi chú'
    )
    
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('library.member') or _('New')
        return super(LibraryMember, self).create(vals)
    
    @api.depends('registration_date', 'member_type')
    def _compute_expiry_date(self):
        for record in self:
            if record.registration_date:
                if record.member_type in ['student', 'teacher', 'staff']:
                    # Thành viên nội bộ: 2 năm
                    record.expiry_date = record.registration_date + timedelta(days=730)
                else:
                    # Thành viên bên ngoài: 1 năm
                    record.expiry_date = record.registration_date + timedelta(days=365)
            else:
                record.expiry_date = False
    
    @api.depends('borrowing_ids')
    def _compute_borrowing_count(self):
        for record in self:
            record.borrowing_count = len(record.borrowing_ids)
    
    @api.depends('current_borrowing_ids')
    def _compute_current_borrowing_count(self):
        for record in self:
            record.current_borrowing_count = len(record.current_borrowing_ids)
    
    @api.depends('member_type')
    def _compute_max_borrowing_limit(self):
        for record in self:
            if record.member_type == 'student':
                record.max_borrowing_limit = 5
            elif record.member_type in ['teacher', 'staff']:
                record.max_borrowing_limit = 10
            else:
                record.max_borrowing_limit = 3
    
    @api.depends('current_borrowing_ids', 'current_borrowing_ids.due_date')
    def _compute_overdue_count(self):
        today = fields.Date.context_today(self)
        for record in self:
            overdue_borrowings = record.current_borrowing_ids.filtered(
                lambda b: b.due_date and b.due_date < today
            )
            record.overdue_count = len(overdue_borrowings)
    
    @api.depends('current_borrowing_ids', 'current_borrowing_ids.fine_amount')
    def _compute_fine_amount(self):
        for record in self:
            record.fine_amount = sum(record.current_borrowing_ids.mapped('fine_amount'))
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                # Kiểm tra định dạng email cơ bản
                import re
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError('Định dạng email không hợp lệ!')
                
                # Kiểm tra trùng lặp
                existing = self.search([
                    ('email', '=', record.email),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(f'Email {record.email} đã được sử dụng!')
    
    @api.constrains('birth_date')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.context_today(self):
                raise ValidationError('Ngày sinh không thể trong tương lai!')
    
    def action_suspend(self):
        """Tạm ngưng thành viên"""
        self.state = 'suspended'
        self.message_post(body='Thành viên đã bị tạm ngưng')
    
    def action_reactivate(self):
        """Kích hoạt lại thành viên"""
        self.state = 'active'
        self.message_post(body='Thành viên đã được kích hoạt lại')
    
    def action_cancel(self):
        """Hủy bỏ thành viên"""
        # Kiểm tra xem có sách đang mượn không
        if self.current_borrowing_count > 0:
            raise ValidationError('Không thể hủy thành viên khi còn sách đang mượn!')
        
        self.state = 'cancelled'
        self.active = False
        self.message_post(body='Thành viên đã bị hủy bỏ')
    
    def action_renew_membership(self):
        """Gia hạn thành viên"""
        if self.member_type in ['student', 'teacher', 'staff']:
            new_expiry = self.expiry_date + timedelta(days=730)
        else:
            new_expiry = self.expiry_date + timedelta(days=365)
        
        self.expiry_date = new_expiry
        self.state = 'active'
        self.message_post(body=f'Thành viên đã được gia hạn đến {new_expiry}')
    
    def can_borrow_book(self):
        """Kiểm tra xem thành viên có thể mượn sách không"""
        if self.state != 'active':
            return False, 'Thành viên không trong trạng thái hoạt động'
        
        if self.current_borrowing_count >= self.max_borrowing_limit:
            return False, f'Đã đạt giới hạn mượn sách ({self.max_borrowing_limit} cuốn)'
        
        if self.overdue_count > 0:
            return False, 'Có sách quá hạn chưa trả'
        
        if self.fine_amount > 0:
            return False, 'Còn tiền phạt chưa thanh toán'
        
        return True, 'Có thể mượn sách'
    
    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            if record.student_id:
                name += f' ({record.student_id})'
            result.append((record.id, name))
        return result 