# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaasCoupon(models.Model):
    """
    Modelo de Cupones SaaS: Representa una 'cuota' o 'asiento' de suscripción.
    Cada vez que un cliente compra o renueva usuarios/meses, se genera uno de estos
    para rastrear la validez de esa compra específica.
    """
    _name = 'saas.coupon'
    _description = 'Cupón / Asiento de Suscripción SaaS'
    _order = 'expiration_date desc'
    
    name = fields.Char(string='Descripción', required=True)
    
    # Relación con la instancia técnica (donde se aplica el cupón)
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia', ondelete='cascade')
    
    # Relación con el paquete de suscripción comercial
    subscription_id = fields.Many2one('subscription.package', string='Suscripción Principal', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='subscription_id.partner_id', store=True, string='Cliente')
    
    # Trazabilidad: De qué orden y factura proviene este cupón
    sale_line_id = fields.Many2one('sale.order.line', string='Línea de Pedido')
    invoice_id = fields.Many2one('account.move', string='Factura Origen', required=True)
    
    # Vigencia del cupón
    start_date = fields.Date(string='Fecha Inicio', default=fields.Date.context_today, required=True)
    expiration_date = fields.Date(string='Fecha Expiración', required=True)
    
    # Cantidad de usuarios que habilita este cupón específico
    user_count = fields.Integer(string='Usuarios', required=True, default=1)
    
    state = fields.Selection([
        ('active', 'Activo'),
        ('expired', 'Expirado')
    ], string='Estado', compute='_compute_state', store=True)

    @api.depends('expiration_date')
    def _compute_state(self):
        """
        Calcula si el cupón sigue vigente comparando la fecha de expiración con hoy.
        """
        today = fields.Date.context_today(self)
        for coupon in self:
            if coupon.expiration_date and coupon.expiration_date >= today:
                coupon.state = 'active'
            else:
                coupon.state = 'expired'


class OdooDockerInstance(models.Model):
    """
    Extensión de la instancia Docker para calcular su capacidad total de usuarios.
    """
    _inherit = 'odoo.docker.instance'

    coupon_ids = fields.One2many('saas.coupon', 'instancia_id', string='Cupones SaaS')
    
    # Lógica Vital: El límite de usuarios de la instancia es la SUMA de usuarios de sus cupones ACTIVOS.
    max_usuarios = fields.Integer(
        string='Límite de Usuarios',
        compute='_compute_max_usuarios',
        store=True,
        help='Suma de todos los cupones activos de esta instancia'
    )

    @api.depends('coupon_ids.state', 'coupon_ids.user_count')
    def _compute_max_usuarios(self):
        """
        Suma recursiva de los asientos de usuarios válidos (no expirados).
        """
        for instance in self:
            total = sum(instance.coupon_ids.filtered(lambda c: c.state == 'active').mapped('user_count'))
            instance.max_usuarios = total


class SubscriptionPackage(models.Model):
    """
    Extensión del paquete de suscripción para vincularlo con los cupones y la instancia.
    """
    _inherit = 'subscription.package'

    coupon_ids = fields.One2many('saas.coupon', 'subscription_id', string='Cupones')
    
    # Usuarios totales que el cliente tiene derecho a usar según sus compras
    total_active_users = fields.Integer(
        string='Usuarios Activos Reales',
        compute='_compute_active_users',
        store=True
    )
    
    # Enlace técnico a la instancia real en el servidor
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia Técnica', help='Instancia de Odoo vinculada a la suscripción')
    instancia_id_url = fields.Char(string='URL Acceso (Instancia)', related='instancia_id.instance_url', readonly=True)

    @api.depends('coupon_ids.user_count', 'coupon_ids.state')
    def _compute_active_users(self):
        """
        Calcula la sumatoria de usuarios activos para mostrar en la suscripción.
        """
        for sub in self:
            sub.total_active_users = sum(sub.coupon_ids.filtered(lambda c: c.state == 'active').mapped('user_count'))
