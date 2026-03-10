# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_months = fields.Float(string='Meses de Suscripción', compute='_compute_saas_summary', store=True)
    subscription_users = fields.Integer(string='Usuarios Permitidos', compute='_compute_saas_summary', store=True)

    @api.depends('invoice_line_ids.saas_months', 'invoice_line_ids.saas_users')
    def _compute_saas_summary(self):
        for move in self:
            # We take values from the first SaaS line we find (not 0)
            saas_lines = move.invoice_line_ids.filtered(lambda l: l.saas_months > 0 or l.saas_users > 0)
            if saas_lines:
                line = saas_lines[0]
                move.subscription_months = line.saas_months
                move.subscription_users = line.saas_users
            else:
                move.subscription_months = 0
                move.subscription_users = 0

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    saas_months = fields.Float(string='Meses SaaS', readonly=True)
    saas_users = fields.Integer(string='Usuarios SaaS', readonly=True)
