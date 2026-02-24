{
    'name': 'Crear Instancia desde Factura',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Botón para crear instancia Docker cuando la factura está pagada',
    'description': """
        Crear Instancia desde Factura
        ==============================
        
        Este módulo agrega un botón "Crear instancia" en las facturas de cliente
        que solo se habilita cuando la factura está completamente pagada.
        
        Características:
        ----------------
        * Botón visible solo en facturas de cliente (out_invoice)
        * Se habilita únicamente cuando payment_state = 'paid'
        * Relación directa entre factura e instancia
        * Botón cambia a "Ver Instancia" cuando ya existe
    """,
    'author': 'Marco-Adolfo-Ribentek',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'micro_saas',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/menu.xml',  # ← NUEVO
        'views/facturas_instancias_views.xml',  # ← NUEVO
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}