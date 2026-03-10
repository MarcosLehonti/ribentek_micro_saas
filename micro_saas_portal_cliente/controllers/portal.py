# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portalPager

class SaaSPagePortal(CustomerPortal):
    """
    Controlador extendido para gestionar el acceso de los clientes a sus
    suscripciones MicroSaaS desde el portal web de Odoo
    """

    def _prepare_home_portal_values(self, counters):
        """
        Añade el controlador de suscripciones activas al menú principal del portal.
        : param counters: Lista de contadores solicitados por la vista portal_my_home.
        : return: Diccionario de valores con el conteo de suscripciones incluido.
        """
        values = super()._prepare_home_portal_values(counters)
        if 'subscription_count' in counters:
            # Contamos los paquetes de suscripción del partner actual
            count = request.env['subscription.package'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('stage_id.category', '!=', 'closed')
            ])
            values['subscription_count'] = count
        return values

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_subscriptions(self, page=1, **kwargs):
        """
        Muestra el listado paginado de todas las suscripciones del cliente
        -Ruta principal : /my/subscriptions
        -Paginación: /my/subscriptions/page/x
        """
        partner = request.env.user.partner_id
        SubscriptionModel = request.env['subscription.package']

        # Filtro: Suscripciones del cliente que no estén cerradas
        # Definimos el dominio de busqueda: solo registros pertenecientes al usuario actual
        domain = [('partner_id', '=', partner.id)]
        
        # Configuracion del Pager (paginador)
        subscription_count = SubscriptionModel.search_count(domain)
        pager = portalPager(
            url='/my/subscriptions',
            total=subscription_count,
            page=page,
            step=10,
        )

        # Búsqueda de registros con limite y desplazamiento para la paginación
        subscriptions = SubscriptionModel.search(
            domain, limit=10, offset=pager['offset'], order='start_date desc'
        )

       # Retorno de la plantilla con los datos necesarios apra renderizar la lista 
        return request.render('micro_saas_portal_cliente.portal_my_subscriptions_list', {
            'subscriptions': subscriptions,
            'pager': pager,
            'page_name': 'subscription', # Para activar el breadcrumb
        })

    @http.route('/my/subscriptions/<int:sub_id>', type='http', auth='user', website=True)
    def portal_subscription_detail(self, sub_id, **kwargs):
        """
        Muestra el detalle técnico de una suscripción especifica.
        Incluye validación de seguridad para evitar que usuarios vean suscripciones ajeanas.
        : param sub_id: ID de la suscripción (subscription.package)
        """
        subscription = request.env['subscription.package'].browse(sub_id)

        # VALIDACIÓN DE SEGURIDAD (Record Rule Manual)
        # si el registro no existe o el partner no coincide con el usuario logueado, redirigir 
        # Seguridad: Verificar que sea el dueño
        if not subscription.exists() or subscription.partner_id != request.env.user.partner_id:
            return request.redirect('/my/subscriptions')

        # Renderizado de la vista de detalle con el objetivo de la suscripcióñ
        return request.render('micro_saas_portal_cliente.portal_subscription_detail_view', {
            'subscription': subscription,
            'page_name': 'subscription',
        })