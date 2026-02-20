# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    """
    Extiende el modelo de productos de Odoo (product.template)
    para agregar campos específicos de los planes MicroSaaS.
    Permite identificar qué productos son planes de suscripción
    y configurar su duración.
    """
    _inherit = 'product.template'
    
    # Define la duración del plan de suscripción.
    # Se usa para calcular automáticamente la fecha de fin
    # al momento de crear o renovar una suscripción.
    duracion_suscripcion = fields.Selection([
        ('monthly', 'Mensual (1 mes)'),
        ('biannual', 'Semestral (6 meses)'),
        ('annual', 'Anual (1 año)'),
    ], string='Duración de Suscripción')

    # Marca si este producto es un plan MicroSaaS.
    # Se usa como filtro en action_crear_suscripcion para identificar
    # qué línea de la factura corresponde al plan a suscribir.
    es_plan_microsaas = fields.Boolean(
        string='Es Plan MicroSaaS',
        default=False,
    )