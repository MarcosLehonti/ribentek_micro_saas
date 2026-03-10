# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    instance_id = fields.Many2one(
        'odoo.docker.instance', 
        string='Instancia SaaS Relacionada',
        help='Instancia generada o actualizada mediante esta factura.',
        copy=False
    )
    
    has_saas_instance = fields.Boolean(
        string='Mantiene Instancia SaaS',
        compute='_compute_has_saas_instance',
        store=False
    )

    @api.depends('partner_id')
    def _compute_has_saas_instance(self):
        """
        Detecta si el cliente ya tiene una instancia técnica creada en el sistema.
        Se usa para ocultar el botón de 'Crear' y mostrar el de 'Actualizar'.
        """
        for move in self:
            if move.partner_id:
                # Buscamos en el modelo de micro_saas si existe un registro con este partner_id
                instance = self.env['odoo.docker.instance'].search([
                    ('partner_id', '=', move.partner_id.id)
                ], limit=1)
                move.has_saas_instance = bool(instance)
            else:
                move.has_saas_instance = False

    def write(self, vals):
        # Override write to detect payment
        res = super(AccountMove, self).write(vals)
        if 'payment_state' in vals:
            for move in self:
                if move.payment_state in ('paid', 'in_payment') and move.move_type == 'out_invoice':
                    move.sudo()._logica_tunel_saas()
        return res

    def _logica_tunel_saas(self):
        """
        ROBUSTA LÓGICA DE TÚNEL SAAS (Refactorizada para Acumulación):
        1. Identifica al Partner.
        2. Limpia cualquier suscripción Draft huérfana del partner ANTES de continuar.
        3. Busca Instancia y Suscripción existentes para evitar duplicidad técnica.
        4. Si existen, vincula la nueva compra de usuarios como un Cupón Adicional.
        5. Si no existen, crea el entorno desde cero.
        """
        self.ensure_one()
        
        # Validar existencia de datos capturados por el portal
        if not hasattr(self, 'subscription_months') or not hasattr(self, 'subscription_users'):
            return
            
        meses = int(self.subscription_months or 0)
        usuarios = int(self.subscription_users or 0)
        
        # Si la factura no tiene carga SaaS real, ignorar
        if meses <= 0 or usuarios <= 0:
            return
            
        SubPackage = self.env['subscription.package']
        Coupon = self.env['saas.coupon']
        Instance = self.env['odoo.docker.instance']
        
        # BLOQUEO DE SEGURIDAD: Evitar que la misma factura genere cupones dos veces
        if Coupon.search([('invoice_id', '=', self.id)]):
            return
            
        partner = self.partner_id

        # ══════════════════════════════════════════════════════════════
        # PASO 0: LIMPIEZA ANTI-HUÉRFANAS
        # Antes de operar, cerramos cualquier Draft que exista para este partner.
        # Esto elimina cualquier Draft escapado del _action_confirm.
        # ══════════════════════════════════════════════════════════════
        self._limpiar_drafts_de_partner(partner)
        
        # PASO 1: LOCALIZACIÓN - Buscar activos existentes del Cliente
        # Buscamos por partner_id para centralizar todas sus facturas en una sola instancia
        instancia_existente = Instance.search([('partner_id', '=', partner.id)], limit=1)
        suscripcion_existente = SubPackage.search([('partner_id', '=', partner.id)], limit=1)

        hoy = fields.Date.context_today(self)
        fecha_fin = hoy + relativedelta(months=meses)

        # PASO 2: GESTIÓN DE LA SUSCRIPCIÓN MADRE (UPSERT)
        # Si el cliente ya tiene contrato, lo usamos. Si no, creamos el contenedor financiero histórico.
        if suscripcion_existente:
            suscripcion = suscripcion_existente
        else:
            plan_defecto = self.env['subscription.package.plan'].search([], limit=1)
            suscripcion = SubPackage.create({
                'partner_id': partner.id,
                'plan_id': plan_defecto.id if plan_defecto else False,
                'name': f'Suscripción Principal: {partner.name}'
            })

        # PASO 3: GESTIÓN DE LA INSTANCIA TÉCNICA (UPSERT / ID ÚNICO)
        # Eliminamos nombres incrementales. Usamos un identificador estático basado en Partner ID o Correo.
        if instancia_existente:
            instancia = instancia_existente
            # Opcional: Registrar en el log de la instancia que recibió una nueva factura
            instancia.message_post(body=f"Factura {self.name} procesada: Se actualiza capacidad de usuarios.")
        else:
            # Creación inicial ÚNICA si es cliente nuevo
            nombre_limpio = partner.name[:10].replace(" ", "").lower()
            instancia = Instance.create({
                'name': f'saas-{partner.id}-{nombre_limpio}', # Nombre estático basado en ID para evitar colisiones
                'partner_id': partner.id,
                'factura_id': self.id,
                'state': 'draft',
            })
            
        # Sincronizar modelos
        if not suscripcion.instancia_id:
            suscripcion.instancia_id = instancia.id
            
        # Vincular ESTA factura a la instancia (ya sea nueva o existente) para el botón de navegación
        self.instance_id = instancia.id

        # PASO 4: ACUMULACIÓN ASÍNCRONA DE CUPONES (SEATS)
        # Creamos el registro del cupón. Esto disparará el cálculo de usuarios en la instancia.
        tipo_movimiento = 'Incremento Usuarios' if instancia_existente else 'Alta Inicial'
        Coupon.create({
            'name': f'{tipo_movimiento}: {usuarios} Usr / {meses} Mes(es)',
            'subscription_id': suscripcion.id,
            'instancia_id': instancia.id,
            'start_date': hoy,
            'expiration_date': fecha_fin,
            'user_count': usuarios,
            'invoice_id': self.id,
        })
        
        # PASO 5: RECALCULAR LÍMITES EN TIEMPO REAL
        # Forzamos la re-ejecución del cálculo para que la UI se actualice inmediatamente
        instancia._compute_max_usuarios()
        suscripcion._compute_active_users()
        
        # Auditoría Final
        self.message_post(body=f"🚀 **SaaS Unificado**: Se detectó instancia existente '{instancia.name}'. Capacidad sumada correctamente.")

    def _limpiar_drafts_de_partner(self, partner):
        """
        Limpieza transaccional (con sudo()) de suscripciones Draft para un partner específico
        que ya tiene una suscripción 'In Progress'.
        Se llama durante el procesamiento del pago de factura para garantizar máxima coherencia.
        """
        SubPackage = self.env['subscription.package'].sudo()

        # Solo hay trabajo si el partner tiene ya una suscripción activa
        tiene_activa = SubPackage.search_count([
            ('partner_id', '=', partner.id),
            ('stage_category', '=', 'progress'),
        ])
        if not tiene_activa:
            return  # Cliente nuevo, nada que limpiar

        # Buscar etapa 'closed' para mover los Drafts
        stage_cerrado = self.env['subscription.package.stage'].sudo().search([
            ('category', '=', 'closed')
        ], limit=1)
        if not stage_cerrado:
            return  # No hay etapa cerrada configurada, imposible continuar

        # Buscar Drafts huérfanos para este partner específico
        drafts_huerfanos = SubPackage.search([
            ('partner_id', '=', partner.id),
            ('stage_category', '=', 'draft'),
        ])

        if drafts_huerfanos:
            drafts_huerfanos.write({
                'stage_id': stage_cerrado.id,
                'is_closed': True,
            })
            for draft in drafts_huerfanos:
                draft.message_post(
                    body=(
                        f"🧹 <b>Limpieza Automática (Pago Registrado):</b> "
                        f"Esta suscripción Draft fue cerrada automáticamente porque "
                        f"el partner ya tiene una suscripción activa y la factura "
                        f"{self.name} fue pagada."
                    )
                )



    def action_gestionar_instancia_saas(self):
        """ Redirige al administrador a la ficha técnica de la instancia Docker. """
        self.ensure_one()
        if not self.instance_id:
            return
        return {
            'type': 'ir.actions.act_window',
            'name': 'Panel de Instancia SaaS',
            'res_model': 'odoo.docker.instance',
            'res_id': self.instance_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_crear_entorno_saas(self):
        """ Acción manual para Factura 1 (Creación total). """
        self.ensure_one()
        self._logica_tunel_saas()
        return self.action_gestionar_instancia_saas()

    def action_actualizar_capacidad_saas(self):
        """ Acción manual para Facturas 2, 3... (Acumulación). """
        self.ensure_one()
        self._logica_tunel_saas()
        return self.action_gestionar_instancia_saas()
        
    def action_ver_instancia_asociada(self):
        """
        Redirección directa: 'Ver Instancia Asociada'.
        Devuelve el formato ir.actions.act_window a la instancia del Micro SaaS
        utilizando consistentemente el partner_id.
        """
        self.ensure_one()
        instance = self.env['odoo.docker.instance'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        if not instance:
            return
            
        return {
            'type': 'ir.actions.act_window',
            'name': f'Instancia de {self.partner_id.name}',
            'res_model': 'odoo.docker.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'target': 'current',
        }
