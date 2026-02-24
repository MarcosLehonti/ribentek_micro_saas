{
    "name": "Micro SaaS - Correo de Bienvenida",
    "category": "Tools",
    "summary": "Envía correo de bienvenida al cliente cuando se crea su instancia Docker",
    "description": """
        Micro SaaS Correo
        =================
        Este módulo extiende micro_saas y crear_instancia_factura para:
        - Agregar un botón "Enviar Correo de Bienvenida" en el formulario de instancia Docker
        - Enviar al cliente su URL de acceso, usuario y contraseña inicial
        - Registrar si el correo ya fue enviado para evitar duplicados
        - Plantilla de correo HTML profesional y personalizable
        - Envío automático de aviso de vencimiento de suscripción
        - Vista de historial de correos de aviso enviados
    """,
    "author": "Marcos Guzman y Adolfo Mendoza",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "depends": [
        "base",
        "mail",
        "account",
        "micro_saas",
        "crear_instancia_factura",
        "microsaas_subscription",  # ← agregar esto
    ],

    "data": [
        "data/mail_template.xml",
        "data/mail_template_aviso_vencimiento.xml",  # ← nuevo
        "views/odoo_docker_instance_correo.xml",
        "views/microsaas_subscription_correo.xml",  # ← nuevo
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}

