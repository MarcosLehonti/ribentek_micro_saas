# -*- coding: utf-8 -*-
import os
import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# Ruta base donde se almacenan los ZIPs dentro del módulo
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'db_backups')


class DbBackup(models.Model):
    """
    Registra los archivos ZIP de respaldo de bases de datos Odoo.
    Los ZIPs deben copiarse manualmente a:
        microsaas_db_restore/static/db_backups/
    Este modelo permite seleccionarlos desde la interfaz.
    """
    _name = 'db.backup'
    _description = 'Respaldo de Base de Datos'
    _order = 'name asc'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre descriptivo para identificar este respaldo'
    )

    filename = fields.Char(
        string='Archivo ZIP',
        required=True,
        help='Nombre del archivo ZIP dentro de static/db_backups/ (ej: mi_empresa.zip)'
    )

    file_path = fields.Char(
        string='Ruta Completa',
        compute='_compute_file_path',
        store=False,
        help='Ruta absoluta al archivo ZIP en el servidor'
    )

    file_exists = fields.Boolean(
        string='Archivo Existe',
        compute='_compute_file_path',
        store=False,
    )

    file_size = fields.Char(
        string='Tamaño',
        compute='_compute_file_path',
        store=False,
    )

    odoo_version = fields.Selection([
        ('16.0', 'Odoo 16'),
        ('17.0', 'Odoo 17'),
        ('18.0', 'Odoo 18'),
    ], string='Versión Odoo', default='17.0')

    master_password = fields.Char(
        string='Master Password del Respaldo',
        default='admin',
        help='Master password que se usará al restaurar vía el Database Manager de Odoo'
    )

    notes = fields.Text(string='Notas')

    # Instancias que usan este respaldo
    instance_ids = fields.One2many(
        'odoo.docker.instance',
        'db_backup_id',
        string='Instancias que usan este respaldo'
    )

    instance_count = fields.Integer(
        string='# Instancias',
        compute='_compute_instance_count'
    )

    @api.depends('filename')
    def _compute_file_path(self):
        for rec in self:
            if not rec.filename:
                rec.file_path = False
                rec.file_exists = False
                rec.file_size = '0 KB'
                continue
            path = os.path.join(BACKUP_DIR, rec.filename)
            rec.file_path = path
            rec.file_exists = os.path.isfile(path)
            if rec.file_exists:
                size_bytes = os.path.getsize(path)
                if size_bytes > 1024 * 1024:
                    rec.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    rec.file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                rec.file_size = '— archivo no encontrado —'

    @api.depends('instance_ids')
    def _compute_instance_count(self):
        for rec in self:
            rec.instance_count = len(rec.instance_ids)

    @api.constrains('filename')
    def _check_filename(self):
        for rec in self:
            if not rec.filename.endswith('.zip'):
                raise ValidationError('El archivo debe tener extensión .zip')
            if '/' in rec.filename or '\\' in rec.filename:
                raise ValidationError('El nombre del archivo no puede contener rutas. Solo el nombre del archivo.')

    def action_view_instances(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Instancias',
            'res_model': 'odoo.docker.instance',
            'view_mode': 'list,form',
            'domain': [('db_backup_id', '=', self.id)],
        }

    @api.model
    def get_available_zip_files(self):
        """
        Escanea la carpeta static/db_backups/ y retorna lista de ZIPs disponibles.
        Útil para mostrar advertencias cuando el archivo registrado no existe físicamente.
        """
        if not os.path.isdir(BACKUP_DIR):
            return []
        return [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]
