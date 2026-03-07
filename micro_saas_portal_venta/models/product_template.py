# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saas_package = fields.Boolean(
        string='Es un Paquete SaaS',
        help='Marcar este check si el producto es un paquete SaaS base con meses y usuarios.'
    )
