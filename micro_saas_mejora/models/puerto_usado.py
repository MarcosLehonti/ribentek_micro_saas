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
        """Permite al administrador liberar manualmente un puerto."""
        for record in self:
            record.write({
                'activo': False,
                'fecha_liberacion': fields.Datetime.now(),
            })
