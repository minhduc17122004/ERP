{
    'name': 'Library Management System',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Hệ thống quản lý thư viện hoàn chỉnh',
    'description': """
        Hệ thống quản lý thư viện bao gồm:
        - Quản lý sách, tác giả, thể loại
        - Quản lý thành viên thư viện
        - Hệ thống mượn/trả sách
        - Báo cáo và thống kê
        - Quản lý phạt và gia hạn
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
    ],
    'data': [
        # Security
        'security/library_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/library_sequence.xml',
        'data/library_category_data.xml',
        
        # Views
        'views/library_author_views.xml',
        'views/library_category_views.xml',
        'views/library_book_views.xml',
        'views/library_member_views.xml',
        'views/library_borrowing_views.xml',
        'views/library_menus.xml',
    ],
    'demo': [
        'data/library_demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
} 