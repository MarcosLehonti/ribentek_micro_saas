# -*- coding: utf-8 -*-
{
    'name': 'SaaS - Portal de Suscripciones Cliente',
    'version': '1.0',
    'summary': 'Visualización de suscripciones e instancias desde el portal del cliente',
    'category': 'Website/Portal',
    'author': 'Marcos - Software Developer',
    'depends': [
        'portal',
        'subscription_package',
        'subscription_mejora_cupones', # Para leer los campos de usuarios activos
    ],
'data': [
        'security/ir.model.access.csv',
        'security/subscription_portal_security.xml',
        'views/subscription_portal_templates.xml',
    ],
    'installable': True,
    'application': False,
}