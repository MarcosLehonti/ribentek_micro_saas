# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """
    Extiende el modelo de facturas de Odoo (account.move)
    para gestionar las suscripciones MicroSaaS vinculadas a cada factura.
    Permite crear y visualizar suscripciones directamente desde la factura de venta.
    """    
    _inherit = 'account.move'

    # Relación inversa One2many: una factura puede tener múltiples suscripciones.
    # Busca todos los registros en 'microsaas.subscription' donde factura_id = este registro.
    subscription_ids = fields.One2many(
        'microsaas.subscription', 'factura_id', string='Suscripciones'
    )
    # Campo calculado que muestra cuántas suscripciones están vinculadas a esta factura.
    # Se usa principalmente para el botón de acceso rápido (smart button) en la vista.
    subscription_count = fields.Integer(
        string='Suscripciones', compute='_compute_subscription_count'
    )

    # Campo para saber si esta factura ya fue usada para renovar una suscripción.
    # Evita que se renueve dos veces desde la misma factura.
    es_factura_renovacion = fields.Boolean(
        string='Es Factura de Renovación',
        default=False,
        copy=False,
        help='Indica si esta factura ya fue usada para renovar una suscripción.',
    )

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        """
        Calcula el número de suscripciones asociadas a cada factura.
        Se recalcula automáticamente cada vez que cambia subscription_ids.
        """
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)

    def _get_linea_plan_microsaas(self):
        """
        Busca en las líneas de la factura el primer producto marcado como plan MicroSaaS.
        Retorna la línea encontrada o None.
        """
        for linea in self.invoice_line_ids:
            if linea.product_id and linea.product_id.product_tmpl_id.es_plan_microsaas:
                return linea
        return None

    def action_crear_suscripcion(self):
        """
        Acción que se ejecuta al presionar el botón 'Crear Suscripción' en la factura.
        
        Flujo:
        1. Valida que la factura cumpla las condiciones necesarias.
        2. Busca en las líneas de la factura un producto MicroSaaS con duración configurada.
        3. Busca si ya existe una instancia Docker vinculada a esta factura.
        4. Crea la suscripción en estado borrador y redirige a su formulario.
        """
        # Garantiza que la acción se ejecute sobre un único registro
        self.ensure_one()

        # Validación 1: Solo facturas de venta a clientes (out_invoice).
        # Se excluyen facturas de proveedor, notas de crédito, etc.
        if self.move_type != 'out_invoice':
            raise UserError(_('Solo puedes crear suscripciones desde facturas de cliente.'))
        
        # Validación 2: La factura debe estar completamente pagada.
        # No se activa ningún servicio sin confirmar el cobro.
        if self.payment_state != 'paid':
            raise UserError(_('La factura debe estar completamente pagada.'))
        
        # Validación 3: La factura debe tener un cliente asignado
        # para poder vincular la suscripción a un partner en Odoo.
        if not self.partner_id:
            raise UserError(_('La factura debe tener un cliente asignado.'))
        
        # Busca en las líneas de la factura el primer producto marcado como
        # plan MicroSaaS (es_plan_microsaas = True en la plantilla del producto).
        linea_plan = self._get_linea_plan_microsaas()

        # Validación 4: La factura debe contener al menos un producto MicroSaaS.
        if not linea_plan:
            raise UserError(_('No se encontró un producto MicroSaaS en esta factura.'))
        
        # Validación 5: El producto MicroSaaS encontrado debe tener configurada su duración.
        if not linea_plan.product_id.product_tmpl_id.duracion_suscripcion:
            raise UserError(_('El producto "%s" no tiene duración configurada.') % linea_plan.product_id.name)

        # Busca si ya existe una instancia Docker vinculada a esta factura.
        instancia = self.env['odoo.docker.instance'].search([
            ('factura_id', '=', self.id)
        ], limit=1)

        # Crea la suscripción en estado 'draft' con los datos obtenidos.
        suscripcion = self.env['microsaas.subscription'].create({
            'partner_id': self.partner_id.id,
            'factura_id': self.id,
            'product_id': linea_plan.product_id.id,
            'instancia_id': instancia.id if instancia else False,
            'state': 'draft',
        })

        # Redirige al formulario de la suscripción recién creada.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Suscripción - %s') % self.partner_id.name,
            'res_model': 'microsaas.subscription',
            'res_id': suscripcion.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_renovar_suscripcion(self):
        """
        Renueva la suscripción existente del cliente desde esta factura.
        
        Flujo:
        1. Valida que la factura cumpla las condiciones necesarias.
        2. Busca la suscripción activa/vencida del cliente para ese producto.
        3. Llama al método action_renovar() de la suscripción.
        4. Registra esta factura en el historial de renovaciones.
        5. Marca la factura como usada para renovación.
        """
        self.ensure_one()

        if self.move_type != 'out_invoice':
            raise UserError(_('Solo puedes renovar suscripciones desde facturas de cliente.'))
        
        if self.payment_state != 'paid':
            raise UserError(_('La factura debe estar completamente pagada para renovar.'))

        if self.es_factura_renovacion:
            raise UserError(_('Esta factura ya fue usada para renovar una suscripción.'))

        linea_plan = self._get_linea_plan_microsaas()
        if not linea_plan:
            raise UserError(_('No se encontró un producto MicroSaaS en esta factura.'))

        # Busca suscripción existente del cliente para ese producto
        suscripcion = self.env['microsaas.subscription'].search([
            ('partner_id', '=', self.partner_id.id),
            ('product_id', '=', linea_plan.product_id.id),
            ('state', 'in', ('active', 'expiring_soon', 'expired')),
        ], limit=1)

        if not suscripcion:
            raise UserError(_(
                'No se encontró una suscripción activa para "%s" '
                'del cliente "%s". Usa "Crear Suscripción" en su lugar.'
            ) % (linea_plan.product_id.name, self.partner_id.name))

        # Llama al método de renovación existente en subscription.py
        suscripcion.action_renovar()

        # Registra esta factura en el último registro de renovación creado
        ultima_renovacion = suscripcion.renovacion_ids.sorted('fecha_renovacion', reverse=True)[:1]
        if ultima_renovacion:
            ultima_renovacion.write({'factura_id': self.id})

        # Marca la factura como usada para renovación para evitar duplicados
        self.es_factura_renovacion = True

        return {
            'type': 'ir.actions.act_window',
            'name': _('Suscripción Renovada - %s') % self.partner_id.name,
            'res_model': 'microsaas.subscription',
            'res_id': suscripcion.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ver_suscripciones(self):
        """
        Acción que se ejecuta al presionar el botón 'Ver Suscripciones' en la factura.
        Navega a la(s) suscripción(es) vinculadas a esta factura.
        Si hay una sola, abre directamente su formulario.
        Si hay varias, muestra una lista filtrada por esta factura.
        """
        self.ensure_one()

        # Caso 1: Una sola suscripción — abre directamente el formulario
        if self.subscription_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Suscripción'),
                'res_model': 'microsaas.subscription',
                'res_id': self.subscription_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Caso 2: Múltiples suscripciones — muestra lista filtrada
        return {
            'type': 'ir.actions.act_window',
            'name': _('Suscripciones de %s') % self.name,
            'res_model': 'microsaas.subscription',
            'view_mode': 'tree,form',
            'domain': [('factura_id', '=', self.id)],
            'target': 'current',
        }