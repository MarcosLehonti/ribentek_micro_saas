{
    "name": "Micro SaaS Billing",
    "category": "Tools",
    "summary": "Billing features for Micro SaaS extension",
    "description": """
        This module extends Micro SaaS to include billing functionalities:
        - Clients
        - Invoices
        - Payments
        - Subscriptions (Products)
    """,
    "author": "David Montero Crespo",
    "website": "https://github.com/davidmonterocrespo24/odoo_micro_saas",
    "license": "AGPL-3",
    "version": "17.0.1.0",
    "depends": ["base", "micro_saas", "account", "sale_management"],
    "data": [
        "views/billing_menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
