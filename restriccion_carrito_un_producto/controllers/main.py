# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class RestriccionCarritoUnProducto(WebsiteSale):

    @http.route(['/shop/cart/update_json'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kwargs):
        order = request.website.sale_get_order()
        
        # Forzar que si intenta agregar más de 1 al primer intento, solo sea 1
        if add_qty and add_qty > 1:
            add_qty = 1
        if set_qty and set_qty > 1:
            set_qty = 1

        if order and order.order_line:
            lineas = order.order_line.filtered(
                lambda l: l.product_id and not l.is_delivery
            )
            
            if lineas:
                linea_existente = lineas[0]
                # 1. Si intenta agregar un producto DIFERENTE
                if str(linea_existente.product_id.id) != str(product_id):
                    return {
                        'quantity': int(linea_existente.product_uom_qty),
                        'cart_quantity': int(order.cart_quantity),
                        'warning': 'Solo se permite un producto por compra. Por favor, finaliza tu suscripción actual primero.',
                        'notification_info': {
                            'warning': 'Solo se permite un producto por compra.'
                        }
                    }
                
                # 2. Si intenta aumentar la cantidad del MISMO producto
                current_qty = linea_existente.product_uom_qty
                if add_qty and (current_qty + add_qty) > 1:
                    return {
                        'quantity': 1,
                        'cart_quantity': int(order.cart_quantity),
                        'warning': 'Solo puedes adquirir 1 unidad de esta suscripción.',
                        'notification_info': {
                            'warning': 'Máximo 1 unidad permitida.'
                        }
                    }
                if set_qty and set_qty > 1:
                    return {
                        'quantity': 1,
                        'cart_quantity': int(order.cart_quantity),
                        'warning': 'Solo puedes adquirir 1 unidad de esta suscripción.',
                        'notification_info': {
                            'warning': 'Máximo 1 unidad permitida.'
                        }
                    }

        return super().cart_update_json(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
            **kwargs
        )