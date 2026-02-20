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

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        """
        Calcula el número de suscripciones asociadas a cada factura.
        Se recalcula automáticamente cada vez que cambia subscription_ids.
        """
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)

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
        # Solo se toma la primera línea encontrada (un plan por suscripción).

        linea_plan = None
        for linea in self.invoice_line_ids:
            if linea.product_id and linea.product_id.product_tmpl_id.es_plan_microsaas:
                linea_plan = linea
                break

        # Validación 4: La factura debe contener al menos un producto MicroSaaS.
        # Sin un plan definido no es posible crear la suscripción.
        if not linea_plan:
            raise UserError(_('No se encontró un producto MicroSaaS en esta factura.'))
        
        # Validación 5: El producto MicroSaaS encontrado debe tener configurada
        # su duración (mensual, semestral, anual), ya que es necesaria para
        # calcular las fechas de inicio y fin de la suscripción.
        if not linea_plan.product_id.product_tmpl_id.duracion_suscripcion:
            raise UserError(_('El producto "%s" no tiene duración configurada.') % linea_plan.product_id.name)

        # Busca si ya existe una instancia Docker vinculada a esta factura.
        # Si existe, se asocia automáticamente a la suscripción.
        # Si no existe (instancia aún no creada), se deja el campo vacío.
        instancia = self.env['odoo.docker.instance'].search([
            ('factura_id', '=', self.id)
        ], limit=1)

        # Crea la suscripción en estado 'draft' con los datos obtenidos:
        # - partner_id: cliente de la factura
        # - factura_id: esta factura como origen
        # - product_id: el plan MicroSaaS encontrado en las líneas
        # - instancia_id: la instancia Docker si ya fue creada, sino False
        suscripcion = self.env['microsaas.subscription'].create({
            'partner_id': self.partner_id.id,
            'factura_id': self.id,
            'product_id': linea_plan.product_id.id,
            'instancia_id': instancia.id if instancia else False,  # ← agregado
            'state': 'draft',
        })

        # Redirige al formulario de la suscripción recién creada
        # para que el administrador pueda revisarla y activarla.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Suscripción - %s') % self.partner_id.name,
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
        # Garantiza que la acción se ejecute sobre un único registro
        self.ensure_one()

        # Caso 1: Una sola suscripción — abre directamente el formulario
        # para no obligar al usuario a pasar por una lista innecesaria.
        if self.subscription_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Suscripción'),
                'res_model': 'microsaas.subscription',
                'res_id': self.subscription_ids[0].id, # ID de la única suscripción
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Caso 2: Múltiples suscripciones — muestra una lista filtrada
        # usando domain para mostrar solo las suscripciones de esta factura.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Suscripciones de %s') % self.name,
            'res_model': 'microsaas.subscription',
            'view_mode': 'tree,form',
            'domain': [('factura_id', '=', self.id)], # Filtra por esta factura
            'target': 'current',
        }