# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class MicrosaasSubscription(models.Model):
    """
    Modelo principal del módulo MicroSaaS. Representa una suscripción
    de un cliente a un plan, vinculada a una factura de origen y a una
    instancia Docker que provee el servicio.
    
    Gestiona el ciclo de vida completo de la suscripción:
    draft → active → expiring_soon → expired / cancelled
    """
    _name = 'microsaas.subscription'
    _description = 'Suscripción MicroSaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    # Referencia única generada por secuencia (ej: SUB/2024/001).
    # readonly=True porque se asigna automáticamente al crear.
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True,
                       default=lambda self: _('Nueva Suscripción'))
    
    # Estado actual de la suscripción. tracking=True registra cambios en el chatter.
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('expiring_soon', 'Por Vencer'),
        ('expired', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', tracking=True)

    # Relaciones principales de la suscripción
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    instancia_id = fields.Many2one('odoo.docker.instance', string='Instancia Docker', tracking=True)
    factura_id = fields.Many2one('account.move', string='Factura Origen', readonly=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Plan', required=True, tracking=True)


    # Duración obtenida directamente del producto (mensual, semestral, anual).
    # store=True para permitir búsquedas y filtros sobre este campo.
    duracion_suscripcion = fields.Selection(
        related='product_id.product_tmpl_id.duracion_suscripcion',
        string='Duración', store=True, readonly=True
    )

    # Campos relacionados de la instancia Docker vinculada.
    # Se muestran en la suscripción para que el administrador
    # pueda ver el estado del servicio sin salir del formulario.
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

    # Fecha de fin calculada automáticamente según la duración del plan,
    # pero editable manualmente si se necesita ajustar en casos especiales.
    fecha_fin = fields.Date(string='Fecha Fin', compute='_compute_fecha_fin', store=True, readonly=False, tracking=True)
    # Días restantes calculados en tiempo real, no se almacena en BD.
    dias_restantes = fields.Integer(string='Días Restantes', compute='_compute_dias_restantes')

    # Historial de renovaciones vinculadas a esta suscripción
    renovacion_ids = fields.One2many('microsaas.subscription.renovacion', 'subscription_id', string='Renovaciones')
    renovacion_count = fields.Integer(compute='_compute_renovacion_count')
    notas = fields.Text(string='Notas')

    @api.depends('fecha_inicio', 'duracion_suscripcion')
    def _compute_fecha_fin(self):
        """
        Calcula la fecha de fin sumando la duración del plan a la fecha de inicio.
        Se recalcula automáticamente si cambia la fecha de inicio o el plan.
        Si falta alguno de los dos datos, deja fecha_fin en False.
        """
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
        """
        Calcula los días restantes restando la fecha de hoy a la fecha de fin.
        Retorna 0 si no hay fecha de fin definida.
        Puede retornar valores negativos si la suscripción ya venció.
        """
        today = date.today()
        for rec in self:
            if rec.fecha_fin:
                rec.dias_restantes = (rec.fecha_fin - today).days
            else:
                rec.dias_restantes = 0

    @api.depends('renovacion_ids')
    def _compute_renovacion_count(self):
        """
        Cuenta el número de renovaciones registradas para esta suscripción.
        Se usa para mostrar el contador en el smart button del formulario.
        """
        for rec in self:
            rec.renovacion_count = len(rec.renovacion_ids)

    def action_ver_renovaciones(self):
        """
        Abre la lista de renovaciones filtrada por esta suscripción.
        Se ejecuta al presionar el smart button 'Renovaciones' en el formulario.
        """
        return {
            'name': 'Renovaciones',
            'type': 'ir.actions.act_window',
            'res_model': 'microsaas.subscription.renovacion',
            'view_mode': 'list,form',
            'domain': [('subscription_id', '=', self.id)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para asignar automáticamente
        la referencia única (name) usando la secuencia 'microsaas.subscription'.
        Si la secuencia no está configurada, mantiene el valor por defecto.
        """
        for vals in vals_list:
            if vals.get('name', _('Nueva Suscripción')) == _('Nueva Suscripción'):
                vals['name'] = self.env['ir.sequence'].next_by_code('microsaas.subscription') or _('Nueva Suscripción')
        return super().create(vals_list)

    def action_activar(self):
        """
        Activa la suscripción cambiando su estado a 'active'.
        Si tiene una instancia Docker asociada y está detenida, la inicia.
        Registra el evento en el chatter.
        """

        for rec in self:
            rec.state = 'active'
            if rec.instancia_id and rec.instancia_id.state != 'running':
                rec.instancia_id.start_instance()
            rec.message_post(body=_('Suscripción activada.'))

    def action_cancelar(self):
        """
        Cancela la suscripción cambiando su estado a 'cancelled'.
        Si tiene una instancia Docker corriendo, la detiene para liberar recursos.
        Registra el evento en el chatter.
        """
        for rec in self:
            rec.state = 'cancelled'
            if rec.instancia_id and rec.instancia_id.state == 'running':
                rec.instancia_id.stop_instance()
            rec.message_post(body=_('Suscripción cancelada.'))

    def action_renovar(self):
        """
        Renueva la suscripción extendiendo su fecha de fin según la duración del plan.
        
        Lógica de fecha base:
        - Si la suscripción aún no venció, extiende desde la fecha de fin actual
          (evita perder días al cliente).
        - Si ya venció, extiende desde hoy.
        
        Además:
        - Crea un registro en el historial de renovaciones.
        - Reactiva la instancia Docker si estaba detenida.
        - Registra el evento en el chatter.
        """
        for rec in self:
            # Determina la fecha base para calcular la nueva fecha de fin
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
                # Registra la renovación en el historial con las fechas anterior y nueva
                self.env['microsaas.subscription.renovacion'].create({
                    'subscription_id': rec.id,
                    'fecha_renovacion': date.today(),
                    'fecha_fin_anterior': rec.fecha_fin,
                    'fecha_fin_nueva': nueva_fecha_fin,
                })

                rec.fecha_fin = nueva_fecha_fin
                rec.state = 'active'

                # Reactiva la instancia si estaba detenida por vencimiento
                if rec.instancia_id and rec.instancia_id.state == 'stopped':
                    rec.instancia_id.start_instance()
                rec.message_post(body=_('Suscripción renovada hasta %s.') % nueva_fecha_fin.strftime('%d/%m/%Y'))

    def cron_verificar_suscripciones(self):
        """
        Tarea programada (cron) que se ejecuta diariamente para mantener
        los estados de las suscripciones actualizados automáticamente.
        
        Realiza dos verificaciones:
        
        1. Vencimientos: Busca suscripciones activas o por vencer cuya fecha_fin
           ya pasó, las marca como 'expired' y detiene su instancia Docker.
        
        2. Próximas a vencer: Busca suscripciones activas que vencen en los
           próximos 7 días y las marca como 'expiring_soon' para alertar al cliente.
        """
        today = date.today()

        # --- Paso 1: Marcar como vencidas ---
        vencidas = self.search([('state', 'in', ('active', 'expiring_soon')), ('fecha_fin', '<', today)])
        for sub in vencidas:
            sub.state = 'expired'
            if sub.instancia_id and sub.instancia_id.state == 'running':
                sub.instancia_id.stop_instance()
            sub.message_post(body=_('Suscripción vencida. Instancia detenida automáticamente.'))

        # --- Paso 2: Marcar como por vencer (dentro de 7 días) ---
        limite_aviso = today + relativedelta(days=7)
        por_vencer = self.search([('state', '=', 'active'), ('fecha_fin', '>=', today), ('fecha_fin', '<=', limite_aviso)])
        for sub in por_vencer:
            sub.state = 'expiring_soon'
            sub.message_post(body=_('⚠️ La suscripción vence en %s días (%s).') % (sub.dias_restantes, sub.fecha_fin.strftime('%d/%m/%Y')))


class MicrosaasSubscriptionRenovacion(models.Model):
    """
    Modelo que registra el historial de renovaciones de una suscripción.
    Cada vez que se renueva una suscripción se crea un registro aquí
    con las fechas anterior y nueva, permitiendo trazabilidad completa.
    """
    _name = 'microsaas.subscription.renovacion'
    _description = 'Historial de Renovaciones'
    _order = 'fecha_renovacion desc' # Más recientes primero


    # Suscripción a la que pertenece esta renovación.
    # ondelete='cascade': si se elimina la suscripción, se eliminan sus renovaciones.
    subscription_id = fields.Many2one('microsaas.subscription', string='Suscripción', required=True, ondelete='cascade')
    fecha_renovacion = fields.Date(string='Fecha de Renovación', required=True)
    fecha_fin_anterior = fields.Date(string='Fecha Fin Anterior')
    fecha_fin_nueva = fields.Date(string='Nueva Fecha Fin')
    factura_id = fields.Many2one('account.move', string='Factura de Renovación')# Factura del pago de renovación
    notas = fields.Text(string='Notas')