# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TicketHelpdeskExt(models.Model):
    """Extensión de ticket.helpdesk para vincular con instancias Micro SaaS."""
    _inherit = 'ticket.helpdesk'

    # Campo computed: instancia asociada al email del ticket
    instancia_id = fields.Many2one(
        'odoo.docker.instance',
        string='Instancia del Cliente',
        compute='_compute_instancia_id',
        store=False,
        help='Instancia Docker asociada al email del cliente de este ticket',
    )
    tiene_instancia = fields.Boolean(
        string='¿Tiene Instancia?',
        compute='_compute_instancia_id',
        store=False,
    )

    @api.depends('email', 'customer_id')
    def _compute_instancia_id(self):
        """
        Busca si el email del ticket corresponde a un partner
        que tiene una instancia Micro SaaS creada.
        """
        for ticket in self:
            instancia = False

            # 1. Primero intentar con customer_id directo
            if ticket.customer_id and ticket.customer_id.email:
                email_buscar = ticket.customer_id.email.strip().lower()
                instancia = self._buscar_instancia_por_email(email_buscar)

            # 2. Si no, usar el campo email del ticket
            if not instancia and ticket.email:
                email_buscar = ticket.email.strip().lower()
                instancia = self._buscar_instancia_por_email(email_buscar)

            ticket.instancia_id = instancia
            ticket.tiene_instancia = bool(instancia)

    def _buscar_instancia_por_email(self, email):
        """
        Busca una instancia cuyo partner tenga ese email.
        Devuelve el primer resultado o False.
        """
        if not email:
            return False

        # Buscar el partner con ese email
        partner = self.env['res.partner'].sudo().search(
            [('email', '=ilike', email)], limit=1
        )
        if not partner:
            return False

        # Buscar instancia asociada a ese partner
        instancia = self.env['odoo.docker.instance'].sudo().search([
            ('partner_id', '=', partner.id),
        ], limit=1)

        # Si no hay por partner_id, intentar por nombre de instancia
        # (muchas instancias se crean con el email como parte del nombre)
        if not instancia:
            instancia = self.env['odoo.docker.instance'].sudo().search([
                ('name', 'ilike', email.split('@')[0]),
            ], limit=1)

        return instancia or False

    def action_ir_a_instancia(self):
        """Abre el formulario de la instancia del cliente."""
        self.ensure_one()
        if not self.instancia_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin instancia',
                    'message': 'No se encontró ninguna instancia para este cliente.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Instancia del Cliente',
            'res_model': 'odoo.docker.instance',
            'view_mode': 'form',
            'res_id': self.instancia_id.id,
            'target': 'current',
        }
