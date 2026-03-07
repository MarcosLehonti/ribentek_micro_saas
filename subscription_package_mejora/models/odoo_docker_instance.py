# -*- coding: utf-8 -*-
from odoo import models

class OdooDockerInstance(models.Model):
    _inherit = 'odoo.docker.instance'
    # max_usuarios y vinculaciones fueron movidas a subscription_mejora_cupones
