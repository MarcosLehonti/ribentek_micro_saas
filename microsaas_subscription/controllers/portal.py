# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portalPager


class SubscriptionPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """
        Agrega el contador de suscripciones al portal home.
        """
        values = super()._prepare_home_portal_values(counters)
        if 'subscriptionCount' in counters:
            values['subscriptionCount'] = request.env['microsaas.subscription'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('state', 'not in', ['cancelled']),
            ])
        return values

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'],
                type='http', auth='user', website=True)
    def portalMySubscriptions(self, page=1, **kwargs):
        """
        Muestra la lista de suscripciones del cliente autenticado.
        """
        partner = request.env.user.partner_id
        subscriptionModel = request.env['microsaas.subscription']

        subscriptionCount = subscriptionModel.search_count([
            ('partner_id', '=', partner.id),
            ('state', 'not in', ['cancelled']),
        ])

        pager = portalPager(
            url='/my/subscriptions',
            total=subscriptionCount,
            page=page,
            step=10,
        )

        subscriptions = subscriptionModel.search([
            ('partner_id', '=', partner.id),
            ('state', 'not in', ['cancelled']),
        ], limit=10, offset=pager['offset'], order='fecha_inicio desc')

        return request.render('microsaas_subscription.portal_my_subscriptions', {
            'subscriptions': subscriptions,
            'pager': pager,
            'page_name': 'subscriptions',
        })

    @http.route('/my/subscriptions/<int:subscriptionId>',
                type='http', auth='user', website=True)
    def portalSubscriptionDetail(self, subscriptionId, **kwargs):
        """
        Muestra el detalle de una suscripción específica del cliente.
        """
        subscription = request.env['microsaas.subscription'].search([
            ('id', '=', subscriptionId),
            ('partner_id', '=', request.env.user.partner_id.id),
        ], limit=1)

        if not subscription:
            return request.redirect('/my/subscriptions')

        return request.render('microsaas_subscription.portal_subscription_detail', {
            'subscription': subscription,
            'page_name': 'subscriptions',
        })