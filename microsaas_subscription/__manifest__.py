# -*- coding: utf-8 -*-
{
    'name': 'MicroSaaS Suscripciones',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Gestión de suscripciones para instancias Odoo Docker',
    'author': 'MicroSaaS',
    'depends': ['base', 'account', 'micro_saas', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/subscription_views.xml',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
        'views/portal_templates.xml',  # ← nuevo
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}