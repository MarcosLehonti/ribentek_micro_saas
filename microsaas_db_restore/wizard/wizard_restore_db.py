# -*- coding: utf-8 -*-
import os
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'db_backups'
)


class WizardRestoreDb(models.TransientModel):
    """
    Wizard de confirmación para la restauración de BD plantilla.

    Muestra al usuario:
    - La instancia destino
    - El ZIP que se usará
    - El nombre de BD que se creará
    - El tamaño del archivo
    - Un aviso de que la operación puede tardar varios minutos

    Al confirmar llama a instance_id.do_restore_db()
    """
    _name = 'wizard.restore.db'
    _description = 'Wizard: Confirmar Restauración de BD Plantilla'

    instance_id = fields.Many2one(
        'odoo.docker.instance',
        string='Instancia',
        required=True,
        readonly=True,
    )

    zip_plantilla = fields.Char(
        string='Archivo ZIP',
        readonly=True,
    )

    db_name = fields.Char(
        string='Nombre de la BD a crear',
        required=True,
    )

    master_password = fields.Char(
        string='Master Password de la Instancia',
        required=True,
    )

    file_size = fields.Char(
        string='Tamaño del archivo',
        compute='_compute_file_info',
    )

    file_exists = fields.Boolean(
        compute='_compute_file_info',
    )

    instance_url = fields.Char(
        related='instance_id.instance_url',
        string='URL de la instancia',
        readonly=True,
    )

    @api.depends('zip_plantilla')
    def _compute_file_info(self):
        for rec in self:
            if not rec.zip_plantilla:
                rec.file_size = 'Desconocido'
                rec.file_exists = False
                continue
            path = os.path.join(BACKUP_DIR, rec.zip_plantilla)
            if os.path.isfile(path):
                rec.file_exists = True
                size = os.path.getsize(path)
                if size > 1024 * 1024:
                    rec.file_size = f"{size / (1024 * 1024):.1f} MB"
                else:
                    rec.file_size = f"{size / 1024:.1f} KB"
            else:
                rec.file_exists = False
                rec.file_size = '— no encontrado —'

    def action_confirm_restore(self):
        """
        El usuario confirmó. Sincronizamos los campos editables de vuelta
        a la instancia y ejecutamos la restauración.
        """
        self.ensure_one()

        if not self.file_exists:
            raise UserError(
                f'El archivo "{self.zip_plantilla}" no existe en la carpeta de backups.\n'
                f'Ruta esperada: {os.path.join(BACKUP_DIR, self.zip_plantilla)}'
            )

        # Sincronizar nombre BD y master password por si el usuario los editó en el wizard
        self.instance_id.write({
            'db_restore_name': self.db_name,
            'db_restore_master_password': self.master_password,
        })

        # Ejecutar la restauración
        self.instance_id.do_restore_db()

        # Cerrar wizard y recargar la vista de la instancia
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'odoo.docker.instance',
            'res_id': self.instance_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
