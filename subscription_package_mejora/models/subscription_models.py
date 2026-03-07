# -*- coding: utf-8 -*-
from odoo import models

class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'
    # La lógica de Asientos/Cupones (subscription.seat -> saas.coupon)
    # y los campos total_active_users e instancia_id
    # han sido trasladados al módulo subscription_mejora_cupones.
