# -*- coding: utf-8 -*-
from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)


class MicrosaasSubscriptionCorreo(models.Model):
    """
    Hereda microsaas.subscription para agregar funcionalidad de
    envío de correo de aviso de vencimiento próximo al cliente.
    Valida que el correo solo se envíe una vez por ciclo de suscripción.
    """
    _inherit = 'microsaas.subscription'

    # ─────────────────────────────────────────────
    # CAMPOS NUEVOS
    # ─────────────────────────────────────────────
    correo_aviso_enviado = fields.Boolean(
        string='Correo de aviso enviado',
        default=False,
        copy=False,
        help='Indica si ya se envió el correo de aviso de vencimiento.',
    )

    correo_aviso_fecha = fields.Datetime(
        string='Fecha de envío del aviso',
        readonly=True,
        copy=False,
        help='Fecha y hora en que se envió el correo de aviso de vencimiento.',
    )

    # ─────────────────────────────────────────────
    # ACCIÓN: ENVIAR CORREO MANUAL
    # ─────────────────────────────────────────────
    def action_enviar_correo_aviso_vencimiento(self):
        """
        Envía manualmente el correo de aviso de vencimiento al cliente.
        Se puede usar desde el botón en el formulario de la suscripción.
        """
        self.ensure_one()

        from odoo.exceptions import UserError

        if not self.partner_id.email:
            raise UserError(_(
                'El cliente "%s" no tiene correo electrónico registrado.'
            ) % self.partner_id.name)

        template = self.env.ref(
            'micro_saas_correo.email_template_aviso_vencimiento',
            raise_if_not_found=False,
        )
        if not template:
            raise UserError(_(
                'No se encontró la plantilla "email_template_aviso_vencimiento". '
                'Verifica que el módulo esté instalado correctamente.'
            ))

        template.send_mail(self.id, force_send=True)

        self.write({
            'correo_aviso_enviado': True,
            'correo_aviso_fecha': fields.Datetime.now(),
        })

        self.message_post(body=_(
            '📧 Correo de aviso de vencimiento enviado manualmente a %s (%s).'
        ) % (self.partner_id.name, self.partner_id.email))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Correo enviado'),
                'message': _('Correo de aviso enviado a %s.') % self.partner_id.email,
                'type': 'success',
                'sticky': False,
            },
        }

    def action_reenviar_correo_aviso_vencimiento(self):
        """
        Permite reenviar el correo de aviso aunque ya haya sido enviado.
        Resetea el flag y llama al método principal.
        """
        self.ensure_one()
        self.correo_aviso_enviado = False
        return self.action_enviar_correo_aviso_vencimiento()

    # ─────────────────────────────────────────────
    # OVERRIDE DEL CRON
    # ─────────────────────────────────────────────
    def cron_verificar_suscripciones(self):
        """
        Extiende el cron original para que además de marcar el estado,
        envíe automáticamente el correo de aviso cuando falte 1 día,
        validando que no se haya enviado antes.
        """
        # Primero ejecuta la lógica original del cron
        super().cron_verificar_suscripciones()

        # Busca suscripciones por vencer sin correo enviado
        por_avisar = self.search([
            ('state', '=', 'expiring_soon'),
            ('correo_aviso_enviado', '=', False),
            ('partner_id.email', '!=', False),
        ])

        template = self.env.ref(
            'micro_saas_correo.email_template_aviso_vencimiento',
            raise_if_not_found=False,
        )

        if not template:
            _logger.warning('No se encontró la plantilla email_template_aviso_vencimiento.')
            return

        for sub in por_avisar:
            try:
                template.send_mail(sub.id, force_send=True)
                sub.write({
                    'correo_aviso_enviado': True,
                    'correo_aviso_fecha': fields.Datetime.now(),
                })
                sub.message_post(body=_(
                    '📧 Correo de aviso enviado automáticamente a %s (%s). Vence: %s'
                ) % (sub.partner_id.name, sub.partner_id.email, sub.fecha_fin.strftime('%d/%m/%Y')))
            except Exception as e:
                _logger.error('Error al enviar correo de aviso a %s: %s', sub.partner_id.email, str(e))
                sub.message_post(body=_('❌ Error al enviar correo de aviso: %s') % str(e))