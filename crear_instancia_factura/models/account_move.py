# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """
    Extiende el modelo nativo de facturas de Odoo (account.move)
    para agregar funcionalidad de gestión de instancias Docker
    asociadas a cada factura.
    """    
    _inherit = 'account.move'
    
    # Relación inversa: busca instancias que tengan factura_id = este ID
    instancia_ids = fields.One2many(
        'odoo.docker.instance',
        'factura_id',
        string='Instancias Creadas'
    )
    
    # Cuenta cuántas instancias tiene esta factura
    instancia_count = fields.Integer(
        string='Número de Instancias',
        compute='_compute_instancia_count',
        store=False
    )
    
    @api.depends('instancia_ids')
    def _compute_instancia_count(self):
        for record in self:
            record.instancia_count = len(record.instancia_ids)
    
    def action_crear_instancia(self):
        """
        Acción que se ejecuta al presionar el botón 'Crear Instancia' en la factura.
        Valida que la factura cumpla las condiciones necesarias y luego redirige
        al formulario de nueva instancia Docker con los datos del cliente prellenados.
        """
        self.ensure_one()
        
        # Validación 1: Solo se pueden crear instancias desde facturas de venta (cliente),
        # no desde facturas de proveedor u otros tipos de movimientos contables.
        if self.move_type != 'out_invoice':
            raise UserError(_('Solo puedes crear instancias desde facturas de cliente.'))
        
        # Validación 2: La factura debe estar completamente pagada antes de
        # aprovisionar una instancia, evitando crear recursos sin cobro confirmado.
        if self.payment_state != 'paid':
            raise UserError(_('La factura debe estar completamente pagada para crear la instancia.'))
        
        # Validación 3: La factura debe tener un cliente asignado para poder
        # vincular correctamente la instancia a un partner en Odoo.
        if not self.partner_id:
            raise UserError(_('La factura debe tener un cliente asignado.'))
        
        # Redirige al formulario de creación de instancia Docker.
        # Usa el contexto 'default_*' para precargar campos automáticamente:
        # - default_partner_id: asigna el cliente de la factura
        # - default_factura_id: vincula la instancia a esta factura
        # - default_name: genera un nombre descriptivo automático
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Instancia Docker - %s') % self.partner_id.name,
            'res_model': 'odoo.docker.instance',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_factura_id': self.id,
                'default_name': f'Instancia - {self.partner_id.name} - {self.name}',            },
        }
    
    def action_ver_instancias(self):
        """
        Acción que se ejecuta al presionar el botón 'Ver Instancias' en la factura.
        Navega a la(s) instancia(s) Docker vinculadas a esta factura.
        Si hay una sola instancia, abre directamente su formulario.
        Si hay varias, muestra una lista filtrada por esta factura.
        """
        # Garantiza que la acción se ejecute sobre un único registro
        self.ensure_one()
        
        # Caso 1: Una sola instancia — abre directamente el formulario
        # para no obligar al usuario a pasar por una lista innecesaria.
        if self.instancia_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Instancia - %s') % self.partner_id.name,
                'res_model': 'odoo.docker.instance',
                'res_id': self.instancia_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Caso 2: Múltiples instancias — muestra una lista filtrada
        # usando domain para mostrar solo las instancias de esta factura.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Instancias de %s') % self.name,
            'res_model': 'odoo.docker.instance',
            'view_mode': 'tree,form',
            'domain': [('factura_id', '=', self.id)],
            'target': 'current',
        }

    def action_post(self):
        """
        Sobrescribe la confirmación de factura para validar que
        solo tenga una línea de producto antes de publicarla.
        """
        for record in self:
            if record.move_type == 'out_invoice':
                # Filtra líneas reales (excluye secciones, notas, etc.)
                lineas_producto = record.invoice_line_ids.filtered(
                    lambda l: l.display_type not in ('line_section', 'line_note')
                )
                if len(lineas_producto) > 1:
                    raise UserError(_(
                        'Solo se permite un producto por factura. '
                        'Esta factura tiene %d productos. '
                        'Por favor, crea una factura separada por cada suscripción.'
                    ) % len(lineas_producto))
        return super().action_post()




    # Campo que detecta si esta factura es una renovación
    es_renovacion = fields.Boolean(
        string='Es Renovación',
        compute='_compute_es_renovacion',
        store=False,
    )

    @api.depends('partner_id', 'invoice_line_ids', 'move_type')
    def _compute_es_renovacion(self):
        for rec in self:
            if rec.move_type != 'out_invoice' or not rec.partner_id:
                rec.es_renovacion = False
                continue

            if 'microsaas.subscription' not in self.env:
                rec.es_renovacion = False
                continue

            linea_plan = None
            for linea in rec.invoice_line_ids:
                if linea.product_id and linea.product_id.product_tmpl_id.es_plan_microsaas:
                    linea_plan = linea
                    break

            if not linea_plan:
                rec.es_renovacion = False
                continue

            suscripcion = self.env['microsaas.subscription'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('product_id', '=', linea_plan.product_id.id),
                ('state', 'in', ('active', 'expiring_soon', 'expired')),
            ], limit=1)

            rec.es_renovacion = bool(suscripcion)

