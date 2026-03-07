# -*- coding: utf-8 -*-
{
    'name': 'SaaS - Túnel de Suscripción a Instancia',
    'version': '1.0',
    'summary': 'Conexión automatizada entre Venta (Factura), Suscripción e Instancia',
    'category': 'Sales/Subscriptions',
    'author': 'Marco-Adolfo-Ribentek',
    'depends': [
        'base', 
        'account', 
        'micro_saas', 
        'subscription_mejora_cupones',
        'micro_saas_portal_venta' # Necesario para leer subscription_months y users de la factura
    ],
    'data': [
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
