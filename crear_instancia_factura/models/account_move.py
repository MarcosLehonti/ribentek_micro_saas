# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
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
        Redirige al formulario de creación de instancia Docker
        Pre-llena los campos partner_id y factura_id
        """
        self.ensure_one()
        
        # Validación 1: Solo facturas de cliente
        if self.move_type != 'out_invoice':
            raise UserError(_('Solo puedes crear instancias desde facturas de cliente.'))
        
        # Validación 2: Factura debe estar pagada
        if self.payment_state != 'paid':
            raise UserError(_('La factura debe estar completamente pagada para crear la instancia.'))
        
        # Validación 3: Debe tener cliente
        if not self.partner_id:
            raise UserError(_('La factura debe tener un cliente asignado.'))
        
        # Redirigir a crear nueva instancia con datos prellenados
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
        Abre la(s) instancia(s) creada(s) desde esta factura
        """
        self.ensure_one()
        
        # Si solo hay 1 instancia, abrirla directamente
        if self.instancia_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Instancia - %s') % self.partner_id.name,
                'res_model': 'odoo.docker.instance',
                'res_id': self.instancia_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Si hay varias, mostrar lista filtrada
        return {
            'type': 'ir.actions.act_window',
            'name': _('Instancias de %s') % self.name,
            'res_model': 'odoo.docker.instance',
            'view_mode': 'tree,form',
            'domain': [('factura_id', '=', self.id)],
            'target': 'current',
        }