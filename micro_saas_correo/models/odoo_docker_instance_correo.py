# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OdooDockerInstanceCorreo(models.Model):
    """
    Hereda odoo.docker.instance para agregar funcionalidad de
    envío de correo de bienvenida al cliente con su URL de acceso.
    """
    _inherit = 'odoo.docker.instance'

    # ─────────────────────────────────────────────
    # CAMPOS NUEVOS
    # ─────────────────────────────────────────────
    correo_bienvenida_enviado = fields.Boolean(
        string='Correo enviado',
        default=False,
        help='Indica si ya se envió el correo de bienvenida al cliente.',
        copy=False,
    )

    correo_bienvenida_fecha = fields.Datetime(
        string='Fecha de envío',
        readonly=True,
        copy=False,
        help='Fecha y hora en que se envió el correo de bienvenida.',
    )

    # ─────────────────────────────────────────────
    # ACCIÓN: ENVIAR CORREO DE BIENVENIDA
    # ─────────────────────────────────────────────
    def action_enviar_correo_bienvenida(self):
        """
        Envía el correo de bienvenida al cliente con la URL de su instancia.
        Usa la plantilla 'micro_saas_correo.email_template_bienvenida_instancia'.
        """
        self.ensure_one()

        # Validaciones previas
        if not self.partner_id:
            raise UserError(_(
                'Esta instancia no tiene un cliente asignado. '
                'Por favor asigna un cliente antes de enviar el correo.'
            ))

        if not self.partner_id.email:
            raise UserError(_(
                'El cliente "%s" no tiene una dirección de correo electrónico registrada.'
            ) % self.partner_id.name)

        if not self.instance_url:
            raise UserError(_(
                'La instancia aún no tiene una URL generada. '
                'Asegúrate de que la instancia esté iniciada y tenga un puerto HTTP asignado.'
            ))

        # Buscar la plantilla de correo
        template = self.env.ref(
            'micro_saas_correo.email_template_bienvenida_instancia',
            raise_if_not_found=False,
        )
        if not template:
            raise UserError(_(
                'No se encontró la plantilla de correo "email_template_bienvenida_instancia". '
                'Verifica que el módulo esté instalado correctamente.'
            ))

        # Enviar el correo usando la plantilla
        template.send_mail(self.id, force_send=True)

        # Marcar como enviado y registrar fecha
        self.write({
            'correo_bienvenida_enviado': True,
            'correo_bienvenida_fecha': fields.Datetime.now(),
        })

        # Notificación de éxito en el chatter (si el modelo tiene mail.thread)
        # odoo.docker.instance no hereda mail.thread, así que usamos un mensaje de log
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Correo enviado'),
                'message': _(
                    'El correo de bienvenida fue enviado exitosamente a %s (%s).'
                ) % (self.partner_id.name, self.partner_id.email),
                'type': 'success',
                'sticky': False,
            },
        }

    def action_reenviar_correo_bienvenida(self):
        """
        Permite reenviar el correo aunque ya haya sido enviado antes.
        Resetea el flag y llama al método principal.
        """
        self.ensure_one()
        self.correo_bienvenida_enviado = False
        return self.action_enviar_correo_bienvenida()
