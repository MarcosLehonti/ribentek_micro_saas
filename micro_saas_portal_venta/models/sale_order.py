# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Campos informativos a nivel de cabecera que resumen la suscripción
    subscription_months = fields.Float(string='Meses de Suscripción', compute='_compute_saas_summary', store=True)
    subscription_users = fields.Integer(string='Usuarios Permitidos', compute='_compute_saas_summary', store=True)

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'order_line.product_template_attribute_value_ids')
    def _compute_saas_summary(self):
        """
        Calcula el resumen de la suscripción para el pedido de venta.
        Toma los valores de la primera línea de producto que sea un paquete SaaS.
        """
        for order in self:
            # Filtramos las líneas que son paquetes SaaS
            saas_lines = order.order_line.filtered(lambda l: l.product_template_id.is_saas_package)
            if saas_lines:
                line = saas_lines[0]
                # Copiamos los valores de la línea a la cabecera
                order.subscription_months = line.saas_months
                order.subscription_users = line.saas_users
            else:
                order.subscription_months = 0
                order.subscription_users = 0

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Campos técnicos para almacenar los cálculos de meses y usuarios por línea
    saas_months = fields.Float(string='Meses SaaS', compute='_compute_saas_values', store=True)
    saas_users = fields.Integer(string='Usuarios SaaS', compute='_compute_saas_values', store=True)

    @api.depends('product_uom_qty', 'product_template_attribute_value_ids', 'product_template_id.is_saas_package')
    def _compute_saas_values(self):
        """
        Lógica vital: Determina cuántos meses y usuarios se están comprando.
        - Los meses se asumen como la cantidad (product_uom_qty).
        - Los usuarios se extraen del nombre de los atributos (ej: "5 Usuarios").
        """
        for line in self:
            if not line.product_template_id.is_saas_package:
                line.saas_months = 0
                line.saas_users = 0
                continue
            
            # Los meses corresponden a la cantidad del producto en la línea
            line.saas_months = line.product_uom_qty
            
            # Buscamos en los atributos del producto si hay alguno que mencione "usuario"
            users = 1 # Valor base por defecto
            for attr in line.product_template_attribute_value_ids:
                if 'usuario' in attr.attribute_id.name.lower():
                    # Usamos regex para encontrar el primer número en el nombre del atributo
                    try:
                        name = attr.name
                        found = re.findall(r'\d+', name)
                        if found:
                            users = int(found[0])
                    except:
                        pass
            line.saas_users = users

    def _prepare_invoice_line(self, **optional_values):
        """
        Asegura que los valores de meses y usuarios pasen del pedido a la factura.
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({
            'saas_months': self.saas_months,
            'saas_users': self.saas_users,
        })
        return res
