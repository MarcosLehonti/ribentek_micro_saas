# -*- coding: utf-8 -*-
{
    "name": "Micro SaaS - Portal de Suscripción Dinámico",
    "category": "Website/eCommerce",
    "summary": "Configurador de meses y usuarios en la tienda.",
    "description": """
        Micro SaaS - Portal de Suscripción Dinámico
        ============================================
        Flujo del cliente:

        Flujo del administrador:
  

        Nuevos campos:
 
    """,
    "author": "Marco-Adolfo-Ribentek",
    "license": "LGPL-3",
    "version": "17.0.2.0.0",
    "depends": [
        "base",
        "product",
        "account",
        "sale",
        "sale_management",
        "portal",
        "website_sale",
        "micro_saas",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}