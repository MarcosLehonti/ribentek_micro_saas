# -*- coding: utf-8 -*-
{
    'name': 'Restricción de Carrito - Un Producto',
    'version': '17.0.1.0.0',
    'category': 'Website/eCommerce',
    'summary': 'Restringe el carrito a un solo producto por compra',
    'description': """
        Módulo que controla que el cliente solo pueda agregar
        un producto a la vez en el carrito del ecommerce.
        Si intenta agregar un segundo producto, se muestra
        una notificación informándole que debe comprar de uno en uno.
    """,
    'author': 'Tu Empresa',
    'depends': ['website_sale'],
    'data': [
        'views/cart_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}