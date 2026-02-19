# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    duracion_suscripcion = fields.Selection([
        ('monthly', 'Mensual (1 mes)'),
        ('biannual', 'Semestral (6 meses)'),
        ('annual', 'Anual (1 año)'),
    ], string='Duración de Suscripción')

    es_plan_microsaas = fields.Boolean(
        string='Es Plan MicroSaaS',
        default=False,
    )