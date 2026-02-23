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

        if order and order.order_line:
            lineas = order.order_line.filtered(
                lambda l: l.product_id and not l.is_delivery
            )
            # Si ya hay un producto y el que intenta agregar es diferente, bloquear
            if lineas and str(lineas[0].product_id.id) != str(product_id):
                return {
                    'quantity': int(lineas[0].product_uom_qty),
                    'cart_quantity': int(order.cart_quantity),
                    'warning': ' Solo se permite un producto por compra. Si deseas más suscripciones, realiza una compra separada.',
                    'notification_info': {
                        'warning': ' Solo se permite un producto por compra. Si deseas más suscripciones, realiza una compra separada.'
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