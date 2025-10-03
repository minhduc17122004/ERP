from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class LibraryBorrowing(models.Model):
    _name = 'library.borrowing'
    _description = 'Mượn sách'
    _order = 'borrow_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Mã mượn sách',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True
    )
    
    member_id = fields.Many2one(
        'library.member',
        string='Thành viên',
        required=True,
        tracking=True
    )
    
    book_id = fields.Many2one(
        'library.book',
        string='Sách',
        required=True,
        tracking=True
    )
    
    borrow_date = fields.Date(
        string='Ngày mượn',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    due_date = fields.Date(
        string='Ngày hạn trả',
        required=True,
        tracking=True
    )
    
    return_date = fields.Date(
        string='Ngày trả thực tế',
        tracking=True
    )
    
    state = fields.Selection([
        ('borrowed', 'Đang mượn'),
        ('returned', 'Đã trả'),
        ('overdue', 'Quá hạn'),
        ('lost', 'Thất lạc'),
        ('cancelled', 'Hủy bỏ'),
    ], string='Trạng thái', default='borrowed', required=True, tracking=True)
    
    days_borrowed = fields.Integer(
        string='Số ngày mượn',
        compute='_compute_days_borrowed'
    )
    
    days_overdue = fields.Integer(
        string='Số ngày quá hạn',
        compute='_compute_days_overdue'
    )
    
    fine_amount = fields.Float(
        string='Tiền phạt',
        digits=(16, 2),
        compute='_compute_fine_amount',
        store=True
    )
    
    fine_paid = fields.Boolean(
        string='Đã thanh toán phạt',
        default=False,
        tracking=True
    )
    
    notes = fields.Text(
        string='Ghi chú'
    )
    
    renewal_count = fields.Integer(
        string='Số lần gia hạn',
        default=0
    )
    
    max_renewals = fields.Integer(
        string='Số lần gia hạn tối đa',
        default=2
    )
    
    librarian_id = fields.Many2one(
        'res.users',
        string='Thủ thư',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('library.borrowing') or _('New')
        
        # Tự động tính ngày hạn trả nếu chưa có
        if 'due_date' not in vals and 'borrow_date' in vals:
            borrow_date = fields.Date.from_string(vals['borrow_date'])
            vals['due_date'] = borrow_date + timedelta(days=14)  # Mặc định 14 ngày
        
        return super(LibraryBorrowing, self).create(vals)
    
    @api.depends('borrow_date', 'return_date')
    def _compute_days_borrowed(self):
        for record in self:
            if record.borrow_date:
                end_date = record.return_date or fields.Date.context_today(self)
                delta = end_date - record.borrow_date
                record.days_borrowed = delta.days
            else:
                record.days_borrowed = 0
    
    @api.depends('due_date', 'return_date', 'state')
    def _compute_days_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.due_date:
                if record.state == 'returned' and record.return_date:
                    # Đã trả: tính từ ngày hạn đến ngày trả
                    if record.return_date > record.due_date:
                        delta = record.return_date - record.due_date
                        record.days_overdue = delta.days
                    else:
                        record.days_overdue = 0
                elif record.state in ['borrowed', 'overdue']:
                    # Chưa trả: tính từ ngày hạn đến hôm nay
                    if today > record.due_date:
                        delta = today - record.due_date
                        record.days_overdue = delta.days
                    else:
                        record.days_overdue = 0
                else:
                    record.days_overdue = 0
            else:
                record.days_overdue = 0
    
    @api.depends('days_overdue', 'state')
    def _compute_fine_amount(self):
        fine_per_day = 5000  # 5,000 VND mỗi ngày
        for record in self:
            if record.days_overdue > 0 and not record.fine_paid:
                record.fine_amount = record.days_overdue * fine_per_day
            else:
                record.fine_amount = 0
    
    @api.model
    def _update_overdue_status(self):
        """Cron job để cập nhật trạng thái quá hạn"""
        today = fields.Date.context_today(self)
        overdue_borrowings = self.search([
            ('state', '=', 'borrowed'),
            ('due_date', '<', today)
        ])
        overdue_borrowings.write({'state': 'overdue'})
        
        # Gửi thông báo
        for borrowing in overdue_borrowings:
            borrowing.message_post(
                body=f'Sách "{borrowing.book_id.name}" đã quá hạn {borrowing.days_overdue} ngày'
            )
    
    @api.constrains('member_id', 'book_id')
    def _check_borrowing_constraints(self):
        for record in self:
            if record.state == 'borrowed':
                # Kiểm tra thành viên có thể mượn sách không
                can_borrow, message = record.member_id.can_borrow_book()
                if not can_borrow:
                    raise ValidationError(f'Thành viên không thể mượn sách: {message}')
                
                # Kiểm tra sách có sẵn không
                if record.book_id.state != 'available':
                    raise ValidationError(f'Sách "{record.book_id.name}" không có sẵn để mượn!')
                
                # Kiểm tra thành viên đã mượn sách này chưa
                existing = self.search([
                    ('member_id', '=', record.member_id.id),
                    ('book_id', '=', record.book_id.id),
                    ('state', '=', 'borrowed'),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError('Thành viên đã mượn sách này rồi!')
    
    @api.constrains('borrow_date', 'due_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.borrow_date and record.due_date:
                if record.borrow_date > record.due_date:
                    raise ValidationError('Ngày hạn trả không thể trước ngày mượn!')
            
            if record.return_date:
                if record.return_date < record.borrow_date:
                    raise ValidationError('Ngày trả không thể trước ngày mượn!')
    
    def action_confirm_borrow(self):
        """Xác nhận mượn sách"""
        for record in self:
            if record.state != 'borrowed':
                raise UserError('Chỉ có thể xác nhận những phiếu mượn đang ở trạng thái mượn!')
            
            # Cập nhật trạng thái sách
            record.book_id.state = 'borrowed'
            record.message_post(body=f'Đã xác nhận mượn sách "{record.book_id.name}"')
    
    def action_return_book(self):
        """Trả sách"""
        for record in self:
            if record.state not in ['borrowed', 'overdue']:
                raise UserError('Chỉ có thể trả những sách đang được mượn!')
            
            record.return_date = fields.Date.context_today(self)
            record.state = 'returned'
            
            # Cập nhật trạng thái sách
            record.book_id.state = 'available'
            
            # Thông báo
            message = f'Đã trả sách "{record.book_id.name}"'
            if record.days_overdue > 0:
                message += f' (Quá hạn {record.days_overdue} ngày, phạt {record.fine_amount:,.0f} VND)'
            
            record.message_post(body=message)
    
    def action_renew(self):
        """Gia hạn mượn sách"""
        for record in self:
            if record.state != 'borrowed':
                raise UserError('Chỉ có thể gia hạn những sách đang được mượn!')
            
            if record.renewal_count >= record.max_renewals:
                raise UserError(f'Đã đạt số lần gia hạn tối đa ({record.max_renewals} lần)!')
            
            if record.days_overdue > 0:
                raise UserError('Không thể gia hạn sách quá hạn!')
            
            # Gia hạn thêm 14 ngày
            record.due_date = record.due_date + timedelta(days=14)
            record.renewal_count += 1
            
            record.message_post(
                body=f'Đã gia hạn sách đến ngày {record.due_date} (lần {record.renewal_count})'
            )
    
    def action_mark_lost(self):
        """Đánh dấu sách thất lạc"""
        for record in self:
            record.state = 'lost'
            record.book_id.state = 'lost'
            record.message_post(body='Sách đã được đánh dấu thất lạc')
    
    def action_cancel(self):
        """Hủy bỏ phiếu mượn"""
        for record in self:
            if record.state != 'borrowed':
                raise UserError('Chỉ có thể hủy những phiếu mượn đang ở trạng thái mượn!')
            
            record.state = 'cancelled'
            # Nếu sách đang ở trạng thái borrowed, đặt lại thành available
            if record.book_id.state == 'borrowed':
                record.book_id.state = 'available'
            
            record.message_post(body='Phiếu mượn đã bị hủy bỏ')
    
    def action_pay_fine(self):
        """Thanh toán tiền phạt"""
        for record in self:
            if record.fine_amount <= 0:
                raise UserError('Không có tiền phạt để thanh toán!')
            
            record.fine_paid = True
            record.message_post(
                body=f'Đã thanh toán tiền phạt {record.fine_amount:,.0f} VND'
            )
    
    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.name}] {record.member_id.name} - {record.book_id.name}'
            result.append((record.id, name))
        return result 