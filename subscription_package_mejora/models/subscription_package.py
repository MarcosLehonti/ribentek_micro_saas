from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    # Campo que conecta la suscripción con la instancia física
    x_instance_id = fields.Many2one(
        'saas.instance', string='Instancia Odoo',
        help="Instancia de Odoo vinculada a esta suscripción."
    )
    
    # Este campo sirve para saber cuántos usuarios máximo soporta esta suscripción
    x_max_users = fields.Integer(string='Límite de Usuarios', default=0)

    @api.depends('start_date', 'sale_order_id')
    def _compute_next_invoice_date(self):
        """
        Sobrescribe la función nativa del paquete de suscripción.
        Calcula dinámicamente el next_invoice_date y close_date basado en
        los meses comprados (saas_months / x_months) en la orden de venta.
        Si la suscripción no tiene meses dinámicos, usa el plan por defecto.
        """
        for sub in self:
            if sub.start_date:
                months = 0
                if sub.sale_order_id:
                    # Localiza la línea del producto de suscripción
                    saas_lines = sub.sale_order_id.order_line.filtered(
                        lambda l: l.product_id.is_subscription or getattr(l.product_template_id, 'is_saas_package', False)
                    )
                    if saas_lines:
                        line = saas_lines[0]
                        # Extrae el número de meses usando los campos disponibles (soporta múltiples módulos)
                        if hasattr(line, 'saas_months') and line.saas_months > 0:
                            months = int(line.saas_months)
                        elif hasattr(line, 'x_months') and line.x_months > 0:
                            months = int(line.x_months)

                if months > 0:
                    # Lógica Dinámica: Sumamos los meses comprados a la fecha de inicio
                    new_date = sub.start_date + relativedelta(months=months)
                    sub.next_invoice_date = new_date
                    sub.close_date = new_date  # Actualizamos también la fecha de cierre de la suscripción
                elif sub.plan_id:
                    # Lógica de fallback: Si no hay meses dinámicos, usamos el plan
                    sub.next_invoice_date = sub.start_date + relativedelta(days=sub.plan_id.renewal_time)
                else:
                    sub.next_invoice_date = False

    def get_cotermination_months(self, from_date=None):
        """
        Calcula cuántos meses faltan desde la fecha actual (o from_date)
        hasta la fecha de vencimiento (close_date) de la suscripción.
        """
        if not self.close_date:
            return 0
        if not from_date:
            from_date = fields.Date.context_today(self)
            
        if from_date >= self.close_date:
            return 0
            
        # Calcular meses enteros restantes. 
        # Si un usuario se añade a la mitad del mes, se le cobra el mes completo según la regla de negocio.
        diferencia = relativedelta(self.close_date, from_date)
        meses_restantes = diferencia.years * 12 + diferencia.months
        if diferencia.days > 0:
            meses_restantes += 1
            
        return meses_restantes

    def activate_subscription(self):
        """
        Activa la suscripción e inicia/crea la instancia en micro_saas.
        """
        self.ensure_one()
        # Aquí se conectaría la lógica con micro_saas
        # Si la instancia no existe, deberíamos solicitar la creación
        if not self.x_instance_id:
            # Buscar si hay alguna instancia con cupo disponible o crear nueva
            pass
        
        if self.x_instance_id:
            self.x_instance_id.max_users = self.x_max_users
            if self.x_instance_id.state != 'active':
                self.x_instance_id.action_start()
                
    def action_prepare_instance(self):
        """
        Busca o crea un registro en micro_saas.instance vinculado al cliente.
        Mapea campos de 'Usuarios' y 'Meses'.
        Redirige al usuario al formulario de la instancia.
        """
        self.ensure_one()
        instance_env = self.env['saas.instance'].sudo()

        # Si ya existe una instancia vinculada, simplemente la actualiza
        if not self.x_instance_id:
            # Busca si el partner ya tiene una instancia
            existing_instance = instance_env.search([('partner_id', '=', self.partner_id.id)], limit=1)
            
            if existing_instance:
                self.x_instance_id = existing_instance
            else:
                # Crea una nueva instancia base
                new_instance = instance_env.create({
                    'name': f'Instancia de {self.partner_id.name}',
                    'partner_id': self.partner_id.id,
                    'max_users': self.x_max_users,
                    # Se asume que saas.instance tiene meses o usa las fechas de la suscripción.
                    # 'months': self.months_agreed o similar, dependiendo tu implementación de micro saas
                })
                self.x_instance_id = new_instance

        # Mapea automáticamente los valores
        self.x_instance_id.sudo().write({
            'max_users': self.x_max_users,
        })
        
        # Redirige a la vista del formulario de la instancia
        return {
            'type': 'ir.actions.act_window',
            'name': 'Preparar Instancia SaaS',
            'res_model': 'saas.instance',
            'view_mode': 'form',
            'res_id': self.x_instance_id.id,
            'target': 'current',
        }
                
    def stop_subscription(self):
        """
        Detiene la suscripción y detiene la instancia sin borrarla.
        """
        self.ensure_one()
        if self.x_instance_id and self.x_instance_id.state == 'active':
            self.x_instance_id.action_stop()

class SubscriptionUserLine(models.Model):
    """
    Nuevo modelo extra para registrar la trazabilidad individual de vencimiento 
    de cada usuario de manera independiente.
    (Sugiere hacerlo en micro_saas o donde corresponda mantener la referencia de res.users).
    """
    _name = 'subscription.user.line'
    _description = 'Línea de Usuario por Suscripción'

    subscription_id = fields.Many2one('subscription.package', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Usuario")
    months_paid = fields.Integer(string="Meses Pagados")
    date_start = fields.Date("Fecha de Inicio")
    date_end = fields.Date("Fecha de Fin")
    invoice_id = fields.Many2one('account.move', "Factura de Origen")
    state = fields.Selection([
        ('active', 'Activo'),
        ('expired', 'Expirado')
    ], string="Estado", compute="_compute_state", store=True)

    @api.depends('date_end')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for line in self:
            if line.date_end and line.date_end < today:
                line.state = 'expired'
            else:
                line.state = 'active'
