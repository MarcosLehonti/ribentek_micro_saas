{
    "name": "Micro SaaS - Interfaz Pago",
    "category": "Website",
    "summary": "Botón para redirigir a firma de contrato tras checkout via transferencia",
    "description": """
        Agrega un botón en la pantalla de confirmación de pago (ej. Wire Transfer)
        para redirigir al cliente a la página del portal y que pueda firmar y aceptar su compra.
    """,
    "author": "Marcos Guzman",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "depends": [
        "website_sale",
        "sale_management",
    ],
    "data": [
        "views/website_sale_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}