# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_ids = fields.One2many(
        'microsaas.subscription', 'factura_id', string='Suscripciones'
    )

    subscription_count = fields.Integer(
        string='Suscripciones', compute='_compute_subscription_count'
    )

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)

    def action_crear_suscripcion(self):
        self.ensure_one()
        if self.move_type != 'out_invoice':
            raise UserError(_('Solo puedes crear suscripciones desde facturas de cliente.'))
        if self.payment_state != 'paid':
            raise UserError(_('La factura debe estar completamente pagada.'))
        if not self.partner_id:
            raise UserError(_('La factura debe tener un cliente asignado.'))

        linea_plan = None
        for linea in self.invoice_line_ids:
            if linea.product_id and linea.product_id.product_tmpl_id.es_plan_microsaas:
                linea_plan = linea
                break

        if not linea_plan:
            raise UserError(_('No se encontró un producto MicroSaaS en esta factura.'))

        if not linea_plan.product_id.product_tmpl_id.duracion_suscripcion:
            raise UserError(_('El producto "%s" no tiene duración configurada.') % linea_plan.product_id.name)

        # Buscar instancia asociada a esta factura
        instancia = self.env['odoo.docker.instance'].search([
            ('factura_id', '=', self.id)
        ], limit=1)

        suscripcion = self.env['microsaas.subscription'].create({
            'partner_id': self.partner_id.id,
            'factura_id': self.id,
            'product_id': linea_plan.product_id.id,
            'instancia_id': instancia.id if instancia else False,  # ← agregado
            'state': 'draft',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Nueva Suscripción - %s') % self.partner_id.name,
            'res_model': 'microsaas.subscription',
            'res_id': suscripcion.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ver_suscripciones(self):
        self.ensure_one()
        if self.subscription_count == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Suscripción'),
                'res_model': 'microsaas.subscription',
                'res_id': self.subscription_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Suscripciones de %s') % self.name,
            'res_model': 'microsaas.subscription',
            'view_mode': 'tree,form',
            'domain': [('factura_id', '=', self.id)],
            'target': 'current',
        }