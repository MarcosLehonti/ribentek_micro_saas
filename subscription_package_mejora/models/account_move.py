# -*- coding: utf-8 -*-
from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'
    # La lógica incremental de account.move ha sido trasladada al módulo
    # micro_saas_subscription_tunel para modularidad.
