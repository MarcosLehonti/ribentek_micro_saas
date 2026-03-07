# -*- coding: utf-8 -*-
{
    'name': 'SaaS - Mejoras de Cupones',
    'version': '1.0',
    'summary': 'Gestión de Cupones Asíncronos para Instancias SaaS',
    'category': 'Sales/Subscriptions',
    'author': 'Marco-Adolfo-Ribentek',
    'depends': [
        'base', 
        'subscription_package', 
        'micro_saas', 
        'subscription_package_mejora',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_coupon_views.xml',
        'views/instance_inherit_views.xml',
        'views/subscription_inherit_views.xml',
    ],
    'installable': True,
    'application': False,
}
