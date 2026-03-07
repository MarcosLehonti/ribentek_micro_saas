# -*- coding: utf-8 -*-
{
    "name": "SaaS Bridge - Puente de Suscripción e Instancia",
    "category": "Services",
    "summary": "Automatiza la creación/renovación de suscripciones e instancias al confirmar el pago.",
    "description": """
        SaaS Bridge Module
        ==================
        Módulo puente que conecta el flujo de ventas con la gestión de
        suscripciones (subscription.package) e instancias Docker (odoo.docker.instance).

        Cuando una factura SaaS pasa a estado 'Pagada':
          1. Si el cliente es NUEVO → Crea suscripción, cupon inicial y prepara instancia
          2. Si el cliente ya TIENE suscripción/instancia → Renueva agregando un nuevo 'seat/coupon'
          3. Actualiza el límite de usuarios en la instancia existente

        Nuevos Modelos:
          - subscription.seat: (Cupón) Maneja los usuarios incrementales y fechas de expiración.

        Nuevos Campos:
          - max_usuarios en odoo.docker.instance: calculado a partir de la suma de cupones activos.
          - total_active_users y instancia_id en subscription.package.
    """,
    "author": "Marco-Adolfo-Ribentek",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "depends": [
        "base",
        "account",
        "sale_management",
        "micro_saas",
        "micro_saas_mejora",
        "crear_instancia_factura",
        "micro_saas_portal_venta",
        "subscription_package",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/subscription_views.xml",
        "views/instance_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
