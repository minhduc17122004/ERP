# Library Management System

Hệ thống quản lý thư viện hoàn chỉnh cho Odoo 17.

## Tính năng chính

### 📚 Quản lý sách
- Thêm, sửa, xóa thông tin sách
- Phân loại sách theo thể loại
- Quản lý tác giả và thông tin xuất bản
- Theo dõi trạng thái sách (có sẵn, đã mượn, bảo trì, hư hỏng, thất lạc)
- Đánh giá và gắn thẻ sách

### 👥 Quản lý thành viên
- Đăng ký và quản lý thành viên thư viện
- Phân loại thành viên (sinh viên, giáo viên, nhân viên, bên ngoài)
- Theo dõi thời hạn thành viên
- Quản lý giới hạn mượn sách theo loại thành viên

### 📖 Hệ thống mượn/trả sách
- Tạo phiếu mượn sách
- Theo dõi ngày hạn trả
- Gia hạn mượn sách (tối đa 2 lần)
- Tính toán tiền phạt tự động cho sách quá hạn
- Trả sách và cập nhật trạng thái

### 🔐 Phân quyền người dùng
- **Người dùng thư viện**: Xem sách, mượn/trả sách
- **Thủ thư**: Quản lý sách, thành viên, mượn/trả
- **Quản lý thư viện**: Toàn quyền quản lý hệ thống

### 📊 Báo cáo và thống kê
- Thống kê sách được mượn nhiều nhất
- Danh sách sách quá hạn
- Báo cáo tiền phạt
- Thống kê theo thành viên

## Cài đặt

1. Copy thư mục `library_management` vào `custom_addons`
2. Cập nhật danh sách Apps trong Odoo
3. Tìm và cài đặt "Library Management System"
4. Cấu hình quyền người dùng theo nhu cầu

## Sử dụng

### Bước đầu
1. Tạo các thể loại sách cơ bản
2. Thêm thông tin tác giả
3. Nhập sách vào hệ thống
4. Đăng ký thành viên thư viện

### Quy trình mượn sách
1. Kiểm tra thành viên có đủ điều kiện mượn
2. Tạo phiếu mượn sách
3. Xác nhận mượn sách
4. Theo dõi ngày hạn trả

### Quy trình trả sách
1. Tìm phiếu mượn
2. Nhấn "Trả sách"
3. Thanh toán phạt (nếu có)
4. Hoàn tất trả sách

## Cấu hình

### Giới hạn mượn sách
- Sinh viên: 5 cuốn
- Giáo viên/Nhân viên: 10 cuốn  
- Bên ngoài: 3 cuốn

### Thời hạn thành viên
- Nội bộ: 2 năm
- Bên ngoài: 1 năm

### Tiền phạt
- 5,000 VND/ngày cho mỗi sách quá hạn

## Cấu trúc dữ liệu

### Models chính
- `library.author` - Tác giả
- `library.category` - Thể loại sách  
- `library.book` - Sách
- `library.member` - Thành viên
- `library.borrowing` - Phiếu mượn sách

### Trạng thái sách
- `available` - Có sẵn
- `borrowed` - Đã mượn
- `lost` - Thất lạc  
- `damaged` - Hư hỏng
- `maintenance` - Bảo trì

### Trạng thái thành viên
- `active` - Hoạt động
- `suspended` - Tạm ngưng
- `expired` - Hết hạn
- `cancelled` - Hủy bỏ

## Hỗ trợ

Để được hỗ trợ và báo lỗi, vui lòng liên hệ qua email hoặc tạo issue trên repository.

## Phiên bản

- **v1.0.0**: Phiên bản đầu tiên với đầy đủ tính năng cơ bản
- **Odoo version**: 17.0+
- **License**: AGPL-3 