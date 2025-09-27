{
    'name': 'Hospital Management',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Hospital Patient Management System',
    'description': """
Hospital Management System
==========================
This module allows you to manage hospital patients with following features:
* Patient Registration
* Patient Information Management
* Doctor Assignment
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/patient_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
} 