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
    """,
    "author": "Marcos Guzman",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "depends": [
        "base",
        "mail",
        "account",
        "micro_saas",
        "crear_instancia_factura",
    ],
    "data": [
        "data/mail_template.xml",
        "views/odoo_docker_instance_correo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
