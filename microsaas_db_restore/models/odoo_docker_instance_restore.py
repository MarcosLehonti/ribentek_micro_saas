# -*- coding: utf-8 -*-
import os      # Manejo de rutas y archivos del sistema
import socket  # Resolucion de direcciones ip
import logging # Sistema de logs

#importaciones de Odoo
from odoo import models, fields, api
from odoo.exceptions import UserError

#inicializacón del logger para registrar eventos en el log de Odoo
_logger = logging.getLogger(__name__)

# Ruta donde se guardan los backups de base de datos
# esta ruta apunta a la carpeta: microsaas_db_restore/static/db_backpus/
# aqui se guardan los archivos ZIP que contienen respaldos de base de datos
BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static', 'db_backups'
)


# Modelo que extiende las instancia docker (micro_saas)
class OdooDockerInstanceRestore(models.Model):
    # se hereda del modelo que maneja las instancias (micro_saas)
    _inherit = 'odoo.docker.instance'

    # este campo muestra una lsita de archivos ZIP disponibles
    # en la carpeta db_backups del modulo
    # se llena dinamicamente usando el metodo _get_zip_selection
    zip_plantilla = fields.Selection(
        selection='_get_zip_selection',
        string='ZIP Plantilla',
        help='Archivo ZIP de respaldo guardado en microsaas_db_restore/static/db_backups/'
    )

    # define el nombre que tendra la base de datos restaurada
    # dentro de la nueva instancia de Odoo
    db_restore_name = fields.Char(
        string='Nombre de la Base de Datos',
        help='Nombre con el que se creará la BD dentro de la instancia.'
    )

    # Password maestro requerido por el endpoint
    # /web/database/restore de Odoo para permitir restauraciones.
    db_restore_master_password = fields.Char(
        string='Master Password de la Instancia',
        default='admin',
        help='Master password configurado en el Odoo de la instancia nueva.'
    )

    # CAMPO: ESTADO DE LA RESTAURACIÓN
    # permite mostrar en la interfaz el estado actual del proceso:
    db_restore_state = fields.Selection([
        ('not_started', 'No iniciada'),
        ('in_progress', 'En progreso...'),
        ('done', 'Restaurada'),
        ('error', 'Error'),
    ], string='Estado Restauracion', default='not_started', readonly=True)


    # CAMPO: LOG DEL PROCESO
    # Guarda mensajes generados durante la restauracion
    # para poder revisar errores o confirmaciones
    db_restore_log = fields.Text(
        string='Log Restauracion',
        readonly=True
    )

    # ------------------------------------------------------------------
    # SELECCIÓN DINÁMICA DE ZIPS
    # METODO: OBTENER LISTA DE ARCHIVOS ZIP DISPONIBLES
    # ------------------------------------------------------------------
    @api.model
    def _get_zip_selection(self):
        # si la carpeta de backups no existe, no se devuelve nada
        if not os.path.isdir(BACKUP_DIR):
            return []
        # se listan todos los archivos .zip dentro del directorio
        zips = sorted([
            f for f in os.listdir(BACKUP_DIR)
            if f.lower().endswith('.zip') and os.path.isfile(os.path.join(BACKUP_DIR, f))
        ])
        # Odoo requiere una lista de tuplas (valor, etiqueta)
        return [(z, z) for z in zips]

    # ------------------------------------------------------------------
    # IP DEL HOST DOCKER: para hacer requests desde dentro del contenedor
    # ------------------------------------------------------------------
    def _get_docker_host_ip(self):
        """
        Resuelve la IP del host Docker para poder hacer HTTP requests
        desde dentro del contenedor Odoo principal hacia otros contenedores
        expuestos en puertos del host.

        Orden de resolución:
        1. host.docker.internal  (Docker Desktop en Mac/Windows)
        2. IP del gateway de la red Docker (Linux: normalmente 172.17.0.1)
        3. Fallback: 127.0.0.1
        """
        # Intento 1: host.docker.internal (Mac, Windows, Docker Desktop)
        try:
            ip = socket.gethostbyname('host.docker.internal')
            _logger.info('[RESTORE] Docker host IP via host.docker.internal: %s', ip)
            return ip
        except socket.gaierror:
            pass

        # Intento 2: leer el gateway de la interfaz docker0 desde /proc/net/route
        try:
            with open('/proc/net/route') as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if parts[1] == '00000000':  # ruta default
                        # Gateway en hex little-endian
                        gw_hex = parts[2]
                        gw_bytes = bytes.fromhex(gw_hex)[::-1]
                        ip = '.'.join(str(b) for b in gw_bytes)
                        _logger.info('[RESTORE] Docker host IP via /proc/net/route: %s', ip)
                        return ip
        except Exception:
            pass

        # Fallback
        _logger.warning('[RESTORE] No se pudo resolver host Docker, usando 172.17.0.1')
        return '172.17.0.1'

    # ------------------------------------------------------------------
    # BOTÓN: abrir wizard de confirmación
    # ------------------------------------------------------------------
    def action_open_restore_wizard(self):
        self.ensure_one()

        if self.state != 'running':
            raise UserError(
                'La instancia debe estar en estado "Running" antes de restaurar la BD.'
            )
        if not self.zip_plantilla:
            raise UserError(
                'Selecciona un ZIP plantilla en la pestana "Restauracion de BD" antes de continuar.'
            )
        if not self.db_restore_name:
            raise UserError(
                'Escribe el nombre que tendra la base de datos en la instancia.'
            )

        zip_path = os.path.join(BACKUP_DIR, self.zip_plantilla)
        if not os.path.isfile(zip_path):
            raise UserError(
                f'El archivo "{self.zip_plantilla}" no se encontro en:\n{BACKUP_DIR}\n\n'
                f'Copia el ZIP a esa carpeta y vuelve a intentarlo.'
            )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirmar Restauracion de BD',
            'res_model': 'wizard.restore.db',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_instance_id': self.id,
                'default_zip_plantilla': self.zip_plantilla,
                'default_db_name': self.db_restore_name,
                'default_master_password': self.db_restore_master_password,
            },
        }

    # ------------------------------------------------------------------
    # LÓGICA PRINCIPAL: llamar al /web/database/restore de la instancia
    # ------------------------------------------------------------------
    def do_restore_db(self):
        self.ensure_one()
        import requests

        zip_path = os.path.join(BACKUP_DIR, self.zip_plantilla)

        if not self.http_port:
            raise UserError('La instancia no tiene http_port configurado.')

        # Construir URL usando la IP del host Docker, no localhost ni instance_url.
        # instance_url puede ser un dominio de Codespaces o usar localhost,
        # ambos inaccesibles desde dentro del contenedor via requests internos.
        host = self._get_docker_host_ip()
        restore_url = f"http://{host}:{self.http_port}/web/database/restore"

        self.add_to_log(f"[RESTORE] Iniciando restauracion de BD")
        self.add_to_log(f"[RESTORE] URL destino : {restore_url}")
        self.add_to_log(f"[RESTORE] ZIP         : {self.zip_plantilla}")
        self.add_to_log(f"[RESTORE] Nombre BD   : {self.db_restore_name}")
        self.write({'db_restore_state': 'in_progress', 'db_restore_log': ''})
        self.env.cr.commit()

        try:
            with open(zip_path, 'rb') as zip_file:
                response = requests.post(
                    restore_url,
                    data={
                        'master_pwd': self.db_restore_master_password,
                        'name': self.db_restore_name,
                        'copy': 'false',
                    },
                    files={
                        'backup_file': (self.zip_plantilla, zip_file, 'application/zip'),
                    },
                    timeout=600,
                    allow_redirects=True,
                )

            if response.status_code == 200:
                content = response.text.lower()
                if 'error' in content and 'database' in content and 'restore' not in content:
                    raise Exception(
                        f"La instancia respondio con un posible error.\n"
                        f"Primeros 500 chars:\n{response.text[:500]}"
                    )

                self.add_to_log(f"[RESTORE] BD '{self.db_restore_name}' restaurada exitosamente.")
                self.write({
                    'db_restore_state': 'done',
                    'db_restore_log': f"Restaurado exitosamente desde: {self.zip_plantilla}",
                })
                return True

            else:
                raise Exception(
                    f"HTTP {response.status_code} al llamar a {restore_url}\n"
                    f"Respuesta: {response.text[:500]}"
                )

        except Exception as e:
            error_msg = str(e)
            self.add_to_log(f"[RESTORE][ERROR] {error_msg}")
            self.write({
                'db_restore_state': 'error',
                'db_restore_log': error_msg,
            })
            raise UserError(
                f"Error al restaurar la base de datos:\n\n{error_msg}\n\n"
                f"Revisa el log de la instancia para mas detalles."
            )
