# -*- coding: utf-8 -*-
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class PuertoUsado(models.Model):
    """
    Registro histórico de puertos asignados.
    Previene que un puerto se reasigne después de eliminar una instancia.
    Los puertos solo se liberan manualmente por un administrador.
    """
    _name = 'micro.saas.puerto.usado'
    _description = 'Registro de puertos usados por instancias'
    _order = 'puerto asc'

    puerto = fields.Integer(
        string='Puerto',
        required=True,
        index=True,
    )
    tipo = fields.Selection([
        ('http', 'HTTP'),
        ('longpolling', 'Longpolling'),
    ], string='Tipo', required=True)
    instancia_nombre = fields.Char(
        string='Nombre de Instancia',
        help='Nombre de la instancia que usó/usa este puerto',
    )
    activo = fields.Boolean(
        string='En uso',
        default=True,
        help='Si está activo, el puerto está reservado y no será reasignado.',
    )
    fecha_asignacion = fields.Datetime(
        string='Fecha de Asignación',
        default=fields.Datetime.now,
    )
    fecha_liberacion = fields.Datetime(
        string='Fecha de Liberación',
    )

    _sql_constraints = [
        ('puerto_tipo_unique', 'UNIQUE(puerto, tipo)',
         'Este puerto ya está registrado para este tipo.'),
    ]

    def action_liberar_puerto(self):
        """
        Libera un puerto. Si la instancia asociada está corriendo,
        pide confirmación antes de proceder.
        """
        for record in self:
            if record.activo and record.instancia_nombre:
                # Verificar si hay una instancia corriendo con este nombre
                instancia = self.env['odoo.docker.instance'].search([
                    ('name', '=', record.instancia_nombre),
                    ('state', '=', 'running'),
                ], limit=1)

                if instancia:
                    # Mostrar diálogo de confirmación
                    return {
                        'type': 'ir.actions.act_window',
                        'name': '⚠️ Instancia en Ejecución',
                        'res_model': 'micro.saas.puerto.usado',
                        'view_mode': 'form',
                        'res_id': record.id,
                        'target': 'new',
                        'context': {
                            '_confirmar_liberar': True,
                        },
                    }

            # Sin instancia corriendo → liberar directamente
            record._do_liberar_puerto()

    def action_confirmar_liberar_puerto(self):
        """Acción llamada cuando el usuario confirma liberar el puerto."""
        for record in self:
            record._do_liberar_puerto()

    def _do_liberar_puerto(self):
        """Lógica real de liberación del puerto."""
        self.write({
            'activo': False,
            'fecha_liberacion': fields.Datetime.now(),
        })
