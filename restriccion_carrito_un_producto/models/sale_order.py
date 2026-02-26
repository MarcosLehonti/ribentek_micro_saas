# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """
        Override para asegurar que la cantidad total de cualquier producto
        en el eCommerce no exceda 1. Funciona como respaldo del controlador.
        """
        if self.website_id:  # Solo aplicar si estamos en el sitio web
            # Asegurar que no sean None para evitar TypeErrors
            add_qty = add_qty or 0
            set_qty = set_qty or 0

            if line_id:
                line = self.env['sale.order.line'].browse(line_id)
            elif product_id:
                line = self.order_line.filtered(lambda l: l.product_id.id == product_id)[:1]
            else:
                line = False

            # Validar cambio de cantidad (set_qty)
            if set_qty > 1:
                set_qty = 1
            
            # Validar adición (add_qty)
            if line and add_qty > 0 and (line.product_uom_qty + add_qty) > 1:
                add_qty = 1 - line.product_uom_qty
            elif not line and add_qty > 1:
                add_qty = 1

            # Además, validar que no se agregue un producto diferente si ya hay uno
            # (Ya manejado en el controlador, pero aquí como capa extra)
            otros_productos = self.order_line.filtered(lambda l: l.product_id and not l.is_delivery)
            if otros_productos and product_id and product_id not in otros_productos.mapped('product_id').ids:
                # En _cart_update usualmente no queremos lanzar UserError directo que rompa el flujo AJAX,
                # pero si llegamos aquí es porque el controlador falló.
                # Devolvemos 0 para no agregar nada.
                return {'line_id': False, 'quantity': 0}

        return super(SaleOrder, self)._cart_update(
            product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs
        )
