import logging
import os
import socket
import subprocess
from datetime import datetime, date

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class OdooDockerInstance(models.Model):
    _name = 'odoo.docker.instance'
    _inherit = "docker.compose.template"
    _description = 'Odoo Docker Instance'

    name = fields.Char(string='Instance Name', required=True)
    state = fields.Selection([('draft', 'Draft'), ('stopped', 'Stopped'), ('running', 'Running'), ('error', 'Error')],
                             string='State', default='draft')
    http_port = fields.Char(string='HTTP Port')
    longpolling_port = fields.Char(string='Longpolling Port')
    instance_url = fields.Char(string='Instance URL', compute='_compute_instance_url', store=True)
    repository_line = fields.One2many('repository.repo.line', 'instance_id', string='Repository and Branch')
    log = fields.Html(string='Log')
    addons_path = fields.Char(string='Addons Path', compute='_compute_addons_path', store=True)
    user_path = fields.Char(string='User Path', compute='_compute_user_path', store=True)
    instance_data_path = fields.Char(string='Instance Data Path', compute='_compute_user_path', store=True)
    template_id = fields.Many2one('docker.compose.template', string='Template')
    variable_ids = fields.One2many('docker.compose.template.variable', 'instance_id',
                                   string="Template Variables", store=True, compute='_compute_variable_ids',
                                   precompute=True, readonly=False)
    
    # ============================================
    # CAMPOS PARA RELACIÓN CON FACTURAS
    # ============================================
    factura_id = fields.Many2one(
        'account.move',
        string='Factura Origen',
        readonly=True,
        ondelete='set null',
        help='Factura desde la cual se creó esta instancia'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        help='Cliente propietario de esta instancia'
    )
    # ============================================

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            self.template_dc_body = self.template_id.template_dc_body
            self.tag_ids = self.template_id.tag_ids
            self.repository_line = self.template_id.repository_line
            self.result_dc_body = self._get_formatted_body(template_body=self.template_dc_body, demo_fallback=True)
            self.variable_ids = self.template_id.variable_ids
            self.variable_ids.filtered(lambda r: r.name == '{{HTTP-PORT}}').demo_value = self.http_port
            self.variable_ids.filtered(lambda r: r.name == '{{LONGPOLLING-PORT}}').demo_value = self.longpolling_port
            self.variable_ids.filtered(lambda r: r.name == '{{DB_HOST}}').demo_value = 'db'
            self.variable_ids.filtered(lambda r: r.name == '{{DB_USER}}').demo_value = 'odoo'
            self.variable_ids.filtered(lambda r: r.name == '{{DB_PASSWORD}}').demo_value = 'odoo'
            self.variable_ids.filtered(lambda r: r.name == '{{ADDONS_PATH}}').demo_value = '/mnt/extra-addons'

    @api.onchange('http_port', 'longpolling_port', 'addons_path')
    def onchange_http_port(self):
        self.variable_ids.filtered(lambda r: r.name == '{{HTTP-PORT}}').demo_value = self.http_port
        self.variable_ids.filtered(lambda r: r.name == '{{LONGPOLLING-PORT}}').demo_value = self.longpolling_port
        self.variable_ids.filtered(lambda r: r.name == '{{ADDONS_PATH}}').demo_value = self.addons_path or '/mnt/extra-addons'
        self.variable_ids.filtered(lambda r: r.name == '{{DB_HOST}}').demo_value = 'db'
        self.variable_ids.filtered(lambda r: r.name == '{{DB_USER}}').demo_value = 'odoo'
        self.variable_ids.filtered(lambda r: r.name == '{{DB_PASSWORD}}').demo_value = 'odoo'

    @api.onchange('name')
    def onchange_name(self):
        self.http_port = self._get_available_port()
        self.longpolling_port = self._get_available_port(int(self.http_port) + 1)

    @api.depends('name')
    def _compute_user_path(self):
        for instance in self:
            if not instance.name:
                continue
            instance.user_path = os.path.expanduser('~')
            instance.instance_data_path = os.path.join(instance.user_path, 'odoo_docker', 'data',
                                                       instance.name.replace('.', '_').replace(' ', '_').lower())
            instance.result_dc_body = self._get_formatted_body(template_body=instance.template_dc_body,
                                                               demo_fallback=True)
            instance.result_odoo_conf = self._get_formatted_body(template_body=instance.template_odoo_conf,
                                                                 demo_fallback=True)

    @api.depends('repository_line')
    def _compute_addons_path(self):
        for instance in self:
            if not instance.repository_line:
                continue
            addons_path = []
            for line in instance.repository_line:
                addons_path.append("/mnt/extra-addons/" + self._get_repo_name(line))
            instance.addons_path = ','.join(addons_path)

    def add_to_log(self, message):
        """Agrega un mensaje al registro (log) y lo limpia si supera 1000 caracteres."""
        now = datetime.now()
        new_log = "</br> \n#" + str(now.strftime("%m/%d/%Y, %H:%M:%S")) + " " + str(message) + " " + str(self.log)
        if len(new_log) > 10000:
            new_log = "</br>" + str(now.strftime("%m/%d/%Y, %H:%M:%S")) + " " + str(message)
        self.log = new_log

    # @api.depends('http_port')
    # def _compute_instance_url(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     base_url = base_url.split(':')
    #     base_url = base_url[0] + ':' + base_url[1] + ':'
    #     for instance in self:
    #         if not instance.http_port:
    #             continue
    #         instance.instance_url = f"{base_url}{instance.http_port}"

    @api.depends('http_port')
    def _compute_instance_url(self):
        codespace_name = os.environ.get('CODESPACE_NAME')
        
        for instance in self:
            if not instance.http_port:
                continue
            if codespace_name:
                instance.instance_url = f"https://{codespace_name}-{instance.http_port}.app.github.dev"
            else:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url = base_url.split(':')
                base_url = base_url[0] + ':' + base_url[1] + ':'
                instance.instance_url = f"{base_url}{instance.http_port}"

    def open_instance_url(self):
        for instance in self:
            if instance.http_port:
                url = instance.instance_url
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }


    def _get_available_port(self, start_port=8069, end_port=9000):
        instances = self.env['odoo.docker.instance'].search([])
        ports = []
        for instance in instances:
            ports.append(int(instance.http_port))
            ports.append(int(instance.longpolling_port))

        for port in range(start_port, end_port + 1):
            if port in ports:
                continue
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except Exception as e:
                pass
            finally:
                sock.close()
        self.add_to_log("[ERROR] No se encontraron puertos disponibles en el rango especificado.")

    def _update_docker_compose_file(self):
        self._makedirs(self.instance_data_path)
        modified_path = os.path.join(self.instance_data_path, 'docker-compose.yml')
        self.create_file(modified_path, self.result_dc_body)

    def _get_repo_name(self, line):
        if not line.repository_id or not line.name or not line.repository_id.name:
            return ''
        name_repo_url = line.repository_id.name.split('/')[-1]
        name = name_repo_url.replace('.git', '').replace('.', '_').replace('-', '_').replace(' ', '_').replace(
            '/', '_').replace('\\', '_') + "_branch_" + line.name.replace('.', '_')
        return name

    def _clone_repositories(self):
        for instance in self:
            for line in instance.repository_line:
                repo_name = self._get_repo_name(line)
                repo_path = os.path.join(instance.instance_data_path, "addons", repo_name)
                self._makedirs(repo_path)
                try:
                    cmd = f"git clone {line.repository_id.name} -b {line.name} {repo_path}"
                    self.excute_command(cmd, shell=True, check=True)
                    self.add_to_log(f"[INFO] Repository cloned: {line.repository_id.name} (Branch: {line.name})")
                    line.is_clone = True
                except Exception as e:
                    self.add_to_log(
                        f"[ERROR] Error to clone repository: {line.repository_id.name} (Branch: {line.name})")
                    if hasattr(e, 'stderr') and e.stderr:
                        self.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
                    else:
                        self.add_to_log("[ERROR]  " + str(e))

    def _create_odoo_conf(self):
        for instance in self:
            odoo_conf_path = os.path.join(instance.instance_data_path, "etc", 'odoo.conf')
            instance._makedirs(os.path.dirname(odoo_conf_path))
            try:
                odoo_conf_content = instance.result_odoo_conf
                instance.create_file(odoo_conf_path, odoo_conf_content)
                instance.add_to_log(f"[INFO] Archivo odoo.conf creado exitosamente en {odoo_conf_path}")
            except Exception as e:
                instance.add_to_log(f"[ERROR] Error al crear el archivo odoo.conf en {odoo_conf_path}")
                instance.write({'state': 'error'})
                if hasattr(e, 'stderr') and e.stderr:
                    instance.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
                else:
                    instance.add_to_log("[ERROR]  " + str(e))
                instance.write({'state': 'stopped'})

    # ============================================
    # ACTIVAR SUSCRIPCIÓN AL LEVANTAR INSTANCIA
    # ============================================
    def _activar_suscripcion(self):
        """
        Busca la suscripción en borrador asociada a esta instancia
        y la activa, registrando fecha_inicio = hoy.
        """
        # Verificar que el módulo de suscripciones esté instalado
        if 'microsaas.subscription' not in self.env:
            return

        suscripcion = self.env['microsaas.subscription'].search([
            ('instancia_id', '=', self.id),
            ('state', '=', 'draft'),
        ], limit=1)

        if suscripcion:
            suscripcion.write({
                'fecha_inicio': date.today(),
                'state': 'active',
            })
            self.add_to_log(
                f"[INFO] Suscripción {suscripcion.name} activada. "
                f"Vence el: {suscripcion.fecha_fin.strftime('%d/%m/%Y')}"
            )
        else:
            self.add_to_log("[INFO] No se encontró suscripción en borrador asociada a esta instancia.")

    def _pausar_suscripcion(self):
        """
        Cuando la instancia se detiene, marca la suscripción como pausada
        pero NO la vence (eso lo hace el cron).
        """
        if 'microsaas.subscription' not in self.env:
            return

        suscripcion = self.env['microsaas.subscription'].search([
            ('instancia_id', '=', self.id),
            ('state', 'in', ('active', 'expiring_soon')),
        ], limit=1)

        if suscripcion:
            self.add_to_log(
                f"[INFO] Instancia detenida. Suscripción {suscripcion.name} "
                f"sigue activa hasta {suscripcion.fecha_fin.strftime('%d/%m/%Y')}."
            )
    # ============================================

    def start_instance(self):
        self.add_to_log("[INFO] Starting Odoo Instance")
        self._update_docker_compose_file()

        self._clone_repositories()
        self._create_odoo_conf()

        self.add_to_log("[INFO] Path to modified docker-compose.yml file")
        modified_path = self.instance_data_path + '/docker-compose.yml'

        try:
            # Ejecuta el comando de Docker Compose para levantar la instancia
            cmd = f"docker-compose -f \"{modified_path}\" up -d"
            self.excute_command(cmd, shell=True, check=True)
            self.write({'state': 'running'})

            # ✅ Activar suscripción una vez que la instancia está corriendo
            self._activar_suscripcion()

        except Exception as e:
            self.write({'state': 'error'})

    def stop_instance(self):
        for instance in self:
            if instance.state == 'running':
                self.add_to_log("[INFO] Stopping Odoo Instance")
                modified_path = instance.instance_data_path + '/docker-compose.yml'

                try:
                    # Ejecuta el comando de Docker Compose para detener la instancia
                    cmd = f"docker-compose -f \"{modified_path}\" down"
                    self.excute_command(cmd, shell=True, check=True)
                    instance.write({'state': 'stopped'})

                    # ℹ️ Informar en el log que la suscripción sigue corriendo
                    instance._pausar_suscripcion()

                except Exception as e:
                    self.add_to_log(f"[ERROR] Error to stop Odoo Instance: {str(e)}")

    def restart_instance(self):
        for instance in self:
            if instance.state == 'running':
                self.add_to_log("[INFO] Restarting Odoo Instance")
                modified_path = instance.instance_data_path + '/docker-compose.yml'
                try:
                    cmd = f"docker-compose -f {modified_path} restart"
                    self.excute_command(cmd, shell=True, check=True)
                    instance.write({'state': 'running'})
                except Exception as e:
                    self.add_to_log(f"[ERROR] Error to restart Odoo Instance: {str(e)}")
                    self.write({'state': 'stopped'})

    def unlink(self):
        for instance in self:
            if instance.state == 'running':
                modified_path = instance.instance_data_path + '/docker-compose.yml'
                try:
                    cmd = f"docker-compose -f {modified_path} down"
                    self.excute_command(cmd, shell=True, check=True)
                except Exception as e:
                    pass
                try:
                    for root, dirs, files in os.walk(instance.instance_data_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                except Exception as e:
                    pass

        return super(OdooDockerInstance, self).unlink()

    def excute_command(self, cmd, shell=True, check=True):
        try:
            result = subprocess.run(cmd, shell=shell, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result
        except Exception as e:
            self.add_to_log(f"Error to execute command: {str(e)}")
            self.add_to_log("[INFO] **** Execute the following command manually from the terminal for more details "
                            "****  " + cmd)
            if hasattr(e, 'stderr') and e.stderr:
                self.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
            else:
                self.add_to_log("[ERROR]  " + str(e))
            raise e

    def _makedirs(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as e:
            self.add_to_log(f"Error while creating directory {path} : {str(e)}")

    def create_file(self, modified_path, result_dc_body):
        try:
            with open(modified_path, "w") as modified_file:
                modified_file.write(result_dc_body)
        except Exception as e:
            self.state = 'error'
            self.add_to_log(f"[ERROR] Error to create file: {str(e)}")