# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class SaasCoupon(models.Model):
    _name = 'saas.coupon'
    _description = 'Cupón / Asiento de Suscripción SaaS'
    _order = 'expiration_date desc'
    
    name = fields.Char(string='Descripción', required=True)
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia', ondelete='cascade')
    subscription_id = fields.Many2one('subscription.package', string='Suscripción Principal', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='subscription_id.partner_id', store=True, string='Cliente')
    
    sale_line_id = fields.Many2one('sale.order.line', string='Línea de Pedido')
    invoice_id = fields.Many2one('account.move', string='Factura Origen', required=True)
    
    start_date = fields.Date(string='Fecha Inicio', default=fields.Date.context_today, required=True)
    expiration_date = fields.Date(string='Fecha Expiración', required=True)
    
    user_count = fields.Integer(string='Usuarios', required=True, default=1)
    
    state = fields.Selection([
        ('active', 'Activo'),
        ('expired', 'Expirado')
    ], string='Estado', compute='_compute_state', store=True)

    @api.depends('expiration_date')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for coupon in self:
            if coupon.expiration_date and coupon.expiration_date >= today:
                coupon.state = 'active'
            else:
                coupon.state = 'expired'


class OdooDockerInstance(models.Model):
    _inherit = 'odoo.docker.instance'

    coupon_ids = fields.One2many('saas.coupon', 'instancia_id', string='Cupones SaaS')
    max_usuarios = fields.Integer(
        string='Mínimo Permitido / Límite de Usuarios',
        compute='_compute_max_usuarios',
        store=True,
        help='Suma de todos los cupones activos de esta instancia'
    )

    @api.depends('coupon_ids.state', 'coupon_ids.user_count')
    def _compute_max_usuarios(self):
        for instance in self:
            total = sum(instance.coupon_ids.filtered(lambda c: c.state == 'active').mapped('user_count'))
            instance.max_usuarios = total


class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    coupon_ids = fields.One2many('saas.coupon', 'subscription_id', string='Cupones')
    total_active_users = fields.Integer(
        string='Usuarios Activos Reales',
        compute='_compute_active_users',
        store=True
    )
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia Técnica', help='Instancia de Odoo vinculada a la suscripción')
    instancia_id_url = fields.Char(string='URL Acceso (Instancia)', related='instancia_id.instance_url', readonly=True)

    @api.depends('coupon_ids.user_count', 'coupon_ids.state')
    def _compute_active_users(self):
        for sub in self:
            sub.total_active_users = sum(sub.coupon_ids.filtered(lambda c: c.state == 'active').mapped('user_count'))
