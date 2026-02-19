# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class MicrosaasSubscription(models.Model):
    _name = 'microsaas.subscription'
    _description = 'Suscripción MicroSaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nueva Suscripción'))
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('expiring_soon', 'Por Vencer'),
        ('expired', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia Docker', tracking=True)
    factura_id = fields.Many2one('account.move', string='Factura Origen', readonly=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Plan', required=True, tracking=True)

    duracion_suscripcion = fields.Selection(
        related='product_id.product_tmpl_id.duracion_suscripcion',
        string='Duración', store=True, readonly=True
    )

    # Campos relacionados de la instancia
    instancia_url = fields.Char(
        related='instancia_id.instance_url',
        string='URL de la Instancia',
        readonly=True
    )
    instancia_template_id = fields.Many2one(
        'docker.compose.template',
        related='instancia_id.template_id',
        string='Template',
        readonly=True
    )
    instancia_state = fields.Selection(
        related='instancia_id.state',
        string='Estado Instancia',
        readonly=True
    )

    fecha_inicio = fields.Date(string='Fecha Inicio', tracking=True)
    fecha_fin = fields.Date(string='Fecha Fin', compute='_compute_fecha_fin', store=True, readonly=False, tracking=True)
    dias_restantes = fields.Integer(string='Días Restantes', compute='_compute_dias_restantes')

    renovacion_ids = fields.One2many('microsaas.subscription.renovacion', 'subscription_id', string='Renovaciones')
    renovacion_count = fields.Integer(compute='_compute_renovacion_count')
    notas = fields.Text(string='Notas')

    @api.depends('fecha_inicio', 'duracion_suscripcion')
    def _compute_fecha_fin(self):
        for rec in self:
            if not rec.fecha_inicio or not rec.duracion_suscripcion:
                rec.fecha_fin = False
                continue
            if rec.duracion_suscripcion == 'monthly':
                rec.fecha_fin = rec.fecha_inicio + relativedelta(months=1)
            elif rec.duracion_suscripcion == 'biannual':
                rec.fecha_fin = rec.fecha_inicio + relativedelta(months=6)
            elif rec.duracion_suscripcion == 'annual':
                rec.fecha_fin = rec.fecha_inicio + relativedelta(years=1)

    @api.depends('fecha_fin')
    def _compute_dias_restantes(self):
        today = date.today()
        for rec in self:
            if rec.fecha_fin:
                rec.dias_restantes = (rec.fecha_fin - today).days
            else:
                rec.dias_restantes = 0

    @api.depends('renovacion_ids')
    def _compute_renovacion_count(self):
        for rec in self:
            rec.renovacion_count = len(rec.renovacion_ids)

    def action_ver_renovaciones(self):
        return {
            'name': 'Renovaciones',
            'type': 'ir.actions.act_window',
            'res_model': 'microsaas.subscription.renovacion',
            'view_mode': 'list,form',
            'domain': [('subscription_id', '=', self.id)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nueva Suscripción')) == _('Nueva Suscripción'):
                vals['name'] = self.env['ir.sequence'].next_by_code('microsaas.subscription') or _('Nueva Suscripción')
        return super().create(vals_list)

    def action_activar(self):
        for rec in self:
            rec.state = 'active'
            if rec.instancia_id and rec.instancia_id.state != 'running':
                rec.instancia_id.start_instance()
            rec.message_post(body=_('Suscripción activada.'))

    def action_cancelar(self):
        for rec in self:
            rec.state = 'cancelled'
            if rec.instancia_id and rec.instancia_id.state == 'running':
                rec.instancia_id.stop_instance()
            rec.message_post(body=_('Suscripción cancelada.'))

    def action_renovar(self):
        for rec in self:
            if rec.state in ('expired', 'active', 'expiring_soon'):
                fecha_base = rec.fecha_fin if rec.fecha_fin and rec.fecha_fin >= date.today() else date.today()
                if rec.duracion_suscripcion == 'monthly':
                    nueva_fecha_fin = fecha_base + relativedelta(months=1)
                elif rec.duracion_suscripcion == 'biannual':
                    nueva_fecha_fin = fecha_base + relativedelta(months=6)
                elif rec.duracion_suscripcion == 'annual':
                    nueva_fecha_fin = fecha_base + relativedelta(years=1)
                else:
                    raise UserError(_('El plan no tiene duración definida.'))

                self.env['microsaas.subscription.renovacion'].create({
                    'subscription_id': rec.id,
                    'fecha_renovacion': date.today(),
                    'fecha_fin_anterior': rec.fecha_fin,
                    'fecha_fin_nueva': nueva_fecha_fin,
                })

                rec.fecha_fin = nueva_fecha_fin
                rec.state = 'active'
                if rec.instancia_id and rec.instancia_id.state == 'stopped':
                    rec.instancia_id.start_instance()
                rec.message_post(body=_('Suscripción renovada hasta %s.') % nueva_fecha_fin.strftime('%d/%m/%Y'))

    def cron_verificar_suscripciones(self):
        today = date.today()
        vencidas = self.search([('state', 'in', ('active', 'expiring_soon')), ('fecha_fin', '<', today)])
        for sub in vencidas:
            sub.state = 'expired'
            if sub.instancia_id and sub.instancia_id.state == 'running':
                sub.instancia_id.stop_instance()
            sub.message_post(body=_('Suscripción vencida. Instancia detenida automáticamente.'))

        limite_aviso = today + relativedelta(days=7)
        por_vencer = self.search([('state', '=', 'active'), ('fecha_fin', '>=', today), ('fecha_fin', '<=', limite_aviso)])
        for sub in por_vencer:
            sub.state = 'expiring_soon'
            sub.message_post(body=_('⚠️ La suscripción vence en %s días (%s).') % (sub.dias_restantes, sub.fecha_fin.strftime('%d/%m/%Y')))


class MicrosaasSubscriptionRenovacion(models.Model):
    _name = 'microsaas.subscription.renovacion'
    _description = 'Historial de Renovaciones'
    _order = 'fecha_renovacion desc'

    subscription_id = fields.Many2one('microsaas.subscription', string='Suscripción', required=True, ondelete='cascade')
    fecha_renovacion = fields.Date(string='Fecha de Renovación', required=True)
    fecha_fin_anterior = fields.Date(string='Fecha Fin Anterior')
    fecha_fin_nueva = fields.Date(string='Nueva Fecha Fin')
    factura_id = fields.Many2one('account.move', string='Factura de Renovación')
    notas = fields.Text(string='Notas')