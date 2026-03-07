# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subscription_months = fields.Float(string='Meses de Suscripción', compute='_compute_saas_summary', store=True)
    subscription_users = fields.Integer(string='Usuarios Permetidos', compute='_compute_saas_summary', store=True)

    @api.depends('order_line.product_id', 'order_line.product_uom_qty', 'order_line.product_template_attribute_value_ids')
    def _compute_saas_summary(self):
        for order in self:
            # We take values from the first SaaS line we find
            saas_lines = order.order_line.filtered(lambda l: l.product_template_id.is_saas_package)
            if saas_lines:
                line = saas_lines[0]
                order.subscription_months = line.saas_months
                order.subscription_users = line.saas_users
            else:
                order.subscription_months = 0
                order.subscription_users = 0

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    saas_months = fields.Float(string='Meses SaaS', compute='_compute_saas_values', store=True)
    saas_users = fields.Integer(string='Usuarios SaaS', compute='_compute_saas_values', store=True)

    @api.depends('product_uom_qty', 'product_template_attribute_value_ids', 'product_template_id.is_saas_package')
    def _compute_saas_values(self):
        for line in self:
            if not line.product_template_id.is_saas_package:
                line.saas_months = 0
                line.saas_users = 0
                continue
            
            # Months is the quantity
            line.saas_months = line.product_uom_qty
            
            # Users extracted from attributes
            users = 1 # Default or base? The user says he adds 1-5.
            for attr in line.product_template_attribute_value_ids:
                if 'usuario' in attr.attribute_id.name.lower():
                    # Extract the first integer from the attribute value name
                    try:
                        name = attr.name
                        found = re.findall(r'\d+', name)
                        if found:
                            users = int(found[0])
                    except:
                        pass
            line.saas_users = users

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({
            'saas_months': self.saas_months,
            'saas_users': self.saas_users,
        })
        return res
