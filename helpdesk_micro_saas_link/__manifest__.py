{
    'name': 'Helpdesk → Micro SaaS Link',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Vincula tickets de soporte con instancias Micro SaaS del cliente',
    'description': """
        Cuando el admin abre un ticket de soporte, puede ver automáticamente
        si el cliente (buscado por email) tiene una instancia Docker creada.
        Si existe, aparece un botón para ir directo a su instancia.
    """,
    'author': 'Marco-Adolfo-Ribentek',
    'license': 'LGPL-3',
    'version': '17.0.1.0.0',
    'depends': ['odoo_website_helpdesk', 'micro_saas'],
    'data': [
        'views/ticket_helpdesk_views_ext.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
