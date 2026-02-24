# -*- coding: utf-8 -*-
import logging
import os
import shutil
import socket
import subprocess
import time

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Rango de puertos para instancias hijas.
# Empieza en 8073 para NO colisionar con el Odoo maestro (8069 HTTP, 8072 longpolling).
_DEFAULT_PORT_START = 8073
_DEFAULT_PORT_END = 9999


class OdooDockerInstanceMejora(models.Model):
    """
    Hereda odoo.docker.instance para corregir los problemas principales:

    1. CONFLICTO DE PUERTOS: El odoo maestro usa 8069 y 8072.
       Las instancias hijas empiezan desde 8073.

    2. PRIMER INICIO LENTO: Docker descarga la imagen (~900MB) bloqueando
       el proceso. Ahora hacemos docker pull antes de docker-compose up
       y se informa al usuario en el log.

    3. RE-INICIO TRAS ERROR: Si el primer start falla por puerto ocupado
       y se vuelve a intentar, los contenedores viejos quedan 'Created'.
       Ahora se hace docker-compose down antes de up.

    4. RUTAS CON ESPACIOS: El nombre de instancia puede tener espacios
       ('Instancia - Juan Perez'). Se entrecomillan las rutas.

    5. PUERTOS REUTILIZADOS: Registro histórico en micro.saas.puerto.usado.

    6. UNLINK INCOMPLETO: Limpia en cualquier estado, no solo 'running'.

    7. VARIABLES SE BORRAN: Copia variables por valor, no por referencia.
    """
    _inherit = 'odoo.docker.instance'

    # ==========================================
    #  PUERTOS
    # ==========================================

    def _get_available_port(self, start_port=_DEFAULT_PORT_START, end_port=_DEFAULT_PORT_END):
        """
        Busca un puerto disponible que NO esté:
        - Usado por otra instancia activa
        - Registrado en el historial de puertos (micro.saas.puerto.usado)
        - Ocupado a nivel de sistema operativo (socket bind)
        """
        # 1. Puertos de instancias existentes en DB
        instances = self.env['odoo.docker.instance'].search([])
        ports_in_use = set()
        for instance in instances:
            for port_field in ('http_port', 'longpolling_port'):
                val = getattr(instance, port_field, None)
                if val:
                    try:
                        ports_in_use.add(int(val))
                    except (ValueError, TypeError):
                        pass

        # 2. Puertos registrados históricamente (activos = reservados)
        puertos_reservados = self.env['micro.saas.puerto.usado'].search([
            ('activo', '=', True)
        ])
        for p in puertos_reservados:
            ports_in_use.add(p.puerto)

        # 3. Agregar los puertos del Odoo maestro (siempre reservados)
        ports_in_use.update({8069, 8071, 8072})

        # 4. Buscar un puerto libre
        for port in range(start_port, end_port + 1):
            if port in ports_in_use:
                continue

            # Verificar a nivel de SO
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except (OSError, socket.error):
                continue
            finally:
                sock.close()

        raise UserError(
            'No se encontraron puertos disponibles en el rango %d-%d. '
            'Libera puertos desde el menú de Puertos Usados o amplía el rango.'
            % (start_port, end_port)
        )

    @api.onchange('name')
    def onchange_name(self):
        """Asigna puertos al cambiar nombre. Manejo seguro contra None."""
        if not self.name:
            return
        try:
            http_port = self._get_available_port()
            self.http_port = str(http_port)
            # Longpolling = siguiente puerto disponible
            longpolling_port = self._get_available_port(http_port + 1)
            self.longpolling_port = str(longpolling_port)
        except Exception as e:
            _logger.warning("Error asignando puertos automáticamente: %s", str(e))
            self.http_port = ''
            self.longpolling_port = ''
            return {
                'warning': {
                    'title': 'Sin puertos disponibles',
                    'message': 'No se encontraron puertos disponibles. '
                               'Libera puertos desde el menú de Puertos Usados.',
                }
            }

    # ==========================================
    #  TEMPLATE / VARIABLES
    # ==========================================

    @api.onchange('template_id')
    def onchange_template_id(self):
        """
        Al seleccionar un template, copiar variables como registros NUEVOS
        (no por referencia) para evitar borrar las del template original.
        """
        if self.template_id:
            self.template_dc_body = self.template_id.template_dc_body
            self.template_odoo_conf = self.template_id.template_odoo_conf
            self.tag_ids = self.template_id.tag_ids
            self.repository_line = self.template_id.repository_line

            # Copiar variables como registros NUEVOS
            new_vars = []
            for var in self.template_id.variable_ids:
                new_vars.append((0, 0, {
                    'name': var.name,
                    'demo_value': var.demo_value,
                    'field_type': var.field_type,
                    'field_name': var.field_name,
                }))
            self.variable_ids = [(5, 0, 0)] + new_vars

            # Actualizar puertos en las variables copiadas
            if self.http_port:
                self.variable_ids.filtered(
                    lambda r: r.name == '{{HTTP-PORT}}'
                ).demo_value = self.http_port
            if self.longpolling_port:
                self.variable_ids.filtered(
                    lambda r: r.name == '{{LONGPOLLING-PORT}}'
                ).demo_value = self.longpolling_port

            self.result_dc_body = self._get_formatted_body(
                template_body=self.template_dc_body, demo_fallback=True
            )

    @api.onchange('http_port', 'longpolling_port')
    def onchange_http_port(self):
        """Manejo seguro de puertos vacíos o nulos."""
        if self.http_port:
            port_vars = self.variable_ids.filtered(
                lambda r: r.name == '{{HTTP-PORT}}'
            )
            if port_vars:
                port_vars.demo_value = self.http_port

        if self.longpolling_port:
            lp_vars = self.variable_ids.filtered(
                lambda r: r.name == '{{LONGPOLLING-PORT}}'
            )
            if lp_vars:
                lp_vars.demo_value = self.longpolling_port

    # ==========================================
    #  REGISTRO DE PUERTOS
    # ==========================================

    def _registrar_puertos(self):
        """Registra los puertos HTTP y Longpolling en el historial."""
        self.ensure_one()
        PuertoUsado = self.env['micro.saas.puerto.usado']

        for port_field, tipo in [('http_port', 'http'), ('longpolling_port', 'longpolling')]:
            val = getattr(self, port_field, None)
            if not val:
                continue
            try:
                puerto_int = int(val)
            except (ValueError, TypeError):
                continue

            existente = PuertoUsado.search([
                ('puerto', '=', puerto_int),
                ('tipo', '=', tipo),
            ], limit=1)
            if not existente:
                PuertoUsado.create({
                    'puerto': puerto_int,
                    'tipo': tipo,
                    'instancia_nombre': self.name,
                    'activo': True,
                })
            else:
                existente.write({
                    'activo': True,
                    'instancia_nombre': self.name,
                    'fecha_asignacion': fields.Datetime.now(),
                    'fecha_liberacion': False,
                })

    # ==========================================
    #  VALIDACIÓN DE PUERTOS ANTES DE INICIAR
    # ==========================================

    def _validate_ports_available(self):
        """
        Verifica que los puertos HTTP y Longpolling NO estén ocupados
        a nivel de SO antes de hacer docker-compose up.
        Si están ocupados, intenta identificar qué los usa.
        """
        self.ensure_one()
        for port_field, label in [('http_port', 'HTTP'), ('longpolling_port', 'Longpolling')]:
            val = getattr(self, port_field, None)
            if not val:
                continue
            try:
                port = int(val)
            except (ValueError, TypeError):
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.bind(("0.0.0.0", port))
            except (OSError, socket.error):
                raise UserError(
                    'El puerto %s (%d) ya está en uso por otro proceso en tu sistema. '
                    'Esto puede deberse a:\n'
                    '- El Odoo maestro usa ese puerto\n'
                    '- Otra instancia Docker ya lo tiene asignado\n'
                    '- Otro programa está usando ese puerto\n\n'
                    'Solución: Asigna otro puerto diferente o detén el proceso '
                    'que lo está usando.' % (label, port)
                )
            finally:
                sock.close()

    # ==========================================
    #  PRE-PULL DE IMAGEN DOCKER
    # ==========================================

    def _pre_pull_docker_image(self):
        """
        Descarga la imagen Docker ANTES de hacer docker-compose up.
        Esto evita que docker-compose se quede bloqueado descargando
        sin mostrar progreso al usuario.
        """
        self.ensure_one()
        if not self.result_dc_body:
            return

        # Extraer el nombre de la imagen de odoo del docker-compose resultante
        import re
        match = re.search(r'image:\s*(odoo:\S+)', self.result_dc_body)
        if not match:
            return

        image_name = match.group(1)
        self.add_to_log(
            f"[INFO] ⬇️ Descargando imagen Docker: {image_name} "
            f"(esto puede tardar varios minutos la primera vez...)"
        )

        try:
            result = subprocess.run(
                f'docker pull {image_name}',
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=900  # 15 minutos máximo
            )
            self.add_to_log(f"[INFO] ✅ Imagen {image_name} descargada correctamente312312321321")
        except subprocess.TimeoutExpired:
            self.add_to_log(
                f"[WARN] ⏰ La descarga de {image_name} tardó más de 15 minutos. "
                f"Verifique su conexión a internet."
            )
        except Exception as e:
            self.add_to_log(
                f"[WARN] ⚠️ No se pudo descargar {image_name} previamente: {str(e)}. "
                f"Docker compose intentará descargarla al iniciar."
            )

    # ==========================================
    #  CLEANUP DE CONTENEDORES PREVIOS
    # ==========================================

    def _cleanup_previous_containers(self, compose_path):
        """
        Ejecuta docker-compose down para limpiar contenedores de un intento
        previo fallido. Sin esto, al re-intentar start_instance los contenedores
        quedan en estado 'Created' y no arrancan.
        """
        if not os.path.exists(compose_path):
            return

        try:
            subprocess.run(
                f'docker-compose -f "{compose_path}" down --remove-orphans',
                shell=True,
                check=False,  # No fallar si no hay nada que limpiar
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            _logger.info("[MEJORA] Contenedores previos limpiados para: %s", compose_path)
        except Exception as e:
            _logger.warning("[MEJORA] No se pudieron limpiar contenedores previos: %s", str(e))

    # ==========================================
    #  START INSTANCE (OVERRIDE COMPLETO)
    # ==========================================

    def start_instance(self):
        """
        Override completo del start_instance con las siguientes mejoras:
        1. Valida puertos antes de iniciar
        2. Pre-descarga la imagen Docker
        3. Limpia contenedores previos (re-intentos)
        4. Registra puertos en el historial
        5. Entrecomilla rutas para evitar problemas con espacios
        6. Mejor manejo de errores con mensajes claros
        """
        self.ensure_one()
        self.add_to_log("[INFO] 🚀 Iniciando instancia Odoo...")

        # 1. Validar que los puertos estén disponibles
        try:
            self._validate_ports_available()
        except UserError as e:
            self.add_to_log(f"[ERROR] ❌ {str(e)}")
            self.write({'state': 'error'})
            raise

        # 2. Registrar puertos
        self._registrar_puertos()

        # 3. Generar archivos
        self.add_to_log("[INFO] 📝 Generando archivos de configuración...")
        self._update_docker_compose_file()
        self._clone_repositories()
        self._create_odoo_conf()

        # 4. Pre-descargar imagen Docker (evita bloqueo largo en docker-compose up)
        self._pre_pull_docker_image()

        # 5. Ruta al docker-compose.yml generado
        modified_path = os.path.join(self.instance_data_path, 'docker-compose.yml')

        if not os.path.exists(modified_path):
            self.add_to_log(f"[ERROR] ❌ No se encontró el archivo: {modified_path}")
            self.write({'state': 'error'})
            return

        # 6. Limpiar contenedores de intentos previos fallidos
        self.add_to_log("[INFO] 🧹 Limpiando contenedores previos (si existen)...")
        self._cleanup_previous_containers(modified_path)

        # 7. Iniciar con docker-compose
        self.add_to_log("[INFO] 🐳 Ejecutando docker-compose up...")
        try:
            cmd = f'docker-compose -f "{modified_path}" up -d'
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300  # 5 minutos
            )
            stdout_msg = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            stderr_msg = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''

            if stdout_msg:
                self.add_to_log(f"[INFO] {stdout_msg[:500]}")
            if stderr_msg and 'error' in stderr_msg.lower():
                self.add_to_log(f"[WARN] {stderr_msg[:500]}")

            self.write({'state': 'running'})
            self.add_to_log(
                f"[INFO] ✅ Instancia iniciada correctamente. "
                f"Abrir: {self.instance_url}"
            )
            self.add_to_log(
                "[INFO] ⏳ Nota: Odoo puede tardar 1-2 minutos en inicializar "
                "la base de datos la primera vez."
            )

        except subprocess.TimeoutExpired:
            self.write({'state': 'error'})
            self.add_to_log(
                "[ERROR] ⏰ docker-compose up tardó más de 5 minutos. "
                "Verifica la conexión a internet y el estado de Docker."
            )
        except subprocess.CalledProcessError as e:
            self.write({'state': 'error'})
            stderr_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)
            self.add_to_log(f"[ERROR] ❌ Error al iniciar: {stderr_msg[:1000]}")

            # Diagnóstico automático
            if 'port is already allocated' in stderr_msg:
                self.add_to_log(
                    "[ERROR] 💡 SOLUCIÓN: El puerto ya está en uso. "
                    "Ve a la instancia, cambia los puertos HTTP y Longpolling, "
                    "y vuelve a intentar."
                )
            elif 'pull access denied' in stderr_msg or 'not found' in stderr_msg:
                self.add_to_log(
                    "[ERROR] 💡 SOLUCIÓN: La imagen Docker no existe. "
                    "Verifica que la versión de Odoo en el template sea correcta "
                    "(ej: 17, 18). La versión 19 aún no existe en Docker Hub."
                )
        except Exception as e:
            self.write({'state': 'error'})
            self.add_to_log(f"[ERROR] ❌ Error inesperado: {str(e)}")

    # ==========================================
    #  STOP INSTANCE (OVERRIDE)
    # ==========================================

    def stop_instance(self):
        """Override: Entrecomilla rutas y libera puertos."""
        for instance in self:
            if instance.state == 'running':
                instance.add_to_log("[INFO] ⏹️ Deteniendo instancia...")
                modified_path = os.path.join(
                    instance.instance_data_path, 'docker-compose.yml'
                )
                try:
                    cmd = f'docker-compose -f "{modified_path}" down'
                    instance.excute_command(cmd, shell=True, check=True)
                    instance.write({'state': 'stopped'})
                    instance.add_to_log("[INFO] ✅ Instancia detenida correctamente.")
                except Exception as e:
                    instance.add_to_log(f"[ERROR] ❌ Error al detener: {str(e)}")

    # ==========================================
    #  RESTART INSTANCE (OVERRIDE)
    # ==========================================

    def restart_instance(self):
        """Override: Entrecomilla rutas."""
        for instance in self:
            if instance.state == 'running':
                instance.add_to_log("[INFO] 🔄 Reiniciando instancia...")
                modified_path = os.path.join(
                    instance.instance_data_path, 'docker-compose.yml'
                )
                try:
                    cmd = f'docker-compose -f "{modified_path}" restart'
                    instance.excute_command(cmd, shell=True, check=True)
                    instance.write({'state': 'running'})
                    instance.add_to_log("[INFO] ✅ Instancia reiniciada correctamente.")
                except Exception as e:
                    instance.add_to_log(f"[ERROR] ❌ Error al reiniciar: {str(e)}")
                    instance.write({'state': 'stopped'})

    # ==========================================
    #  UNLINK (OVERRIDE)
    # ==========================================

    def unlink(self):
        """
        Override: Limpia SIEMPRE archivos y contenedores al eliminar,
        sin importar el estado. Marca puertos como inactivos.
        """
        for instance in self:
            # 1. Detener contenedores (en cualquier estado)
            if instance.instance_data_path:
                modified_path = os.path.join(
                    instance.instance_data_path, 'docker-compose.yml'
                )
                if os.path.exists(modified_path):
                    try:
                        cmd = f'docker-compose -f "{modified_path}" down -v --remove-orphans'
                        subprocess.run(
                            cmd, shell=True, check=False,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=60
                        )
                    except Exception as e:
                        _logger.warning(
                            "[MEJORA] Error al detener contenedores de %s: %s",
                            instance.name, str(e)
                        )

                # 2. Limpiar archivos del filesystem
                if os.path.exists(instance.instance_data_path):
                    try:
                        shutil.rmtree(instance.instance_data_path)
                    except Exception as e:
                        _logger.warning(
                            "[MEJORA] Error al eliminar archivos de %s: %s",
                            instance.name, str(e)
                        )

            # 3. Marcar puertos como inactivos
            self._liberar_puertos_de_instancia(instance)

        return super(OdooDockerInstanceMejora, self).unlink()

    def _liberar_puertos_de_instancia(self, instance):
        """Marca los puertos de una instancia como liberados."""
        PuertoUsado = self.env['micro.saas.puerto.usado']
        for port_field in ('http_port', 'longpolling_port'):
            val = getattr(instance, port_field, None)
            if not val:
                continue
            try:
                puertos = PuertoUsado.search([
                    ('puerto', '=', int(val)),
                    ('activo', '=', True),
                ])
                puertos.write({
                    'activo': False,
                    'fecha_liberacion': fields.Datetime.now(),
                })
            except (ValueError, TypeError):
                pass

    # ==========================================
    #  UTILIDADES Y LOGS
    # ==========================================

    def add_to_log(self, message):
        """Override: Limpia el log y evita el 'False' inicial."""
        self.ensure_one()
        now = fields.Datetime.now()
        # Intentar obtener hora local del contexto
        try:
            timestamp = fields.Datetime.context_timestamp(self, now).strftime("%d/%m/%Y, %H:%M:%S")
        except:
            timestamp = now.strftime("%d/%m/%Y, %H:%M:%S")

        current_log = self.log if self.log and str(self.log) != 'False' else ""
        
        # Limitar el tamaño del log para no degradar performance
        if len(current_log) > 20000:
            current_log = current_log[:10000] + "...[LOG TRUNCADO PARA AGILIDAD]..."

        new_entry = f"<br/>\n#{timestamp} {message}"
        self.log = new_entry + current_log

    def _create_odoo_conf(self):
        """
        Override: Optimiza odoo.conf para evitar errores de estilos (proxy_mode)
        y crasheos (logfile).
        """
        for instance in self:
            odoo_conf_path = os.path.join(instance.instance_data_path, "etc", 'odoo.conf')
            instance._makedirs(os.path.dirname(odoo_conf_path))
            try:
                # Obtenemos el contenido del template
                content = instance.result_odoo_conf or ""
                
                lines = content.split('\n')
                new_lines = []
                has_proxy_mode = False
                has_options_header = False
                
                for line in lines:
                    clean_line = line.strip()
                    # 1. Eliminar logfile (causa crash en Docker oficial)
                    if clean_line.startswith('logfile'):
                        continue
                    # 2. Corregir addons_path para incluir los módulos base de Odoo
                    if clean_line.startswith('addons_path'):
                        path_val = line.split('=', 1)[1].strip()
                        base_path = "/usr/lib/python3/dist-packages/odoo/addons"
                        if base_path not in path_val:
                            line = f"addons_path = {base_path},{path_val}"
                    
                    # 3. Detectar si ya tiene proxy_mode
                    if clean_line.startswith('proxy_mode'):
                        has_proxy_mode = True
                    if clean_line == '[options]':
                        has_options_header = True
                    
                    new_lines.append(line)
                
                # 3. Forzar configuraciones críticas para SaaS
                if not has_options_header:
                    new_lines.insert(0, '[options]')
                    has_options_header = True
                
                if not has_proxy_mode:
                    # Insertar proxy_mode justo debajo de [options]
                    idx = new_lines.index('[options]')
                    new_lines.insert(idx + 1, "proxy_mode = True")
                    new_lines.insert(idx + 1, "db_maxconn = 64") # Mejora estabilidad
                
                final_content = '\n'.join(new_lines)
                instance.create_file(odoo_conf_path, final_content)
                instance.add_to_log(f"[INFO] Configuración odoo.conf generada correctamente (proxy_mode=ON)")
                
            except Exception as e:
                instance.add_to_log(f"[ERROR] No se pudo generar odoo.conf: {str(e)}")
                raise UserError(f"Error al crear configuración: {str(e)}")

    def action_view_instance_ports(self):
        """Acción para el Smart Button de Puertos."""
        self.ensure_one()
        return {
            'name': 'Puertos de Instancia',
            'type': 'ir.actions.act_window',
            'res_model': 'micro.saas.puerto.usado',
            'view_mode': 'tree,form',
            'domain': [('instancia_nombre', '=', self.name)],
            'context': {'default_instancia_nombre': self.name, 'default_activo': True},
        }

    def action_ver_puertos_disponibles(self):
        """
        Abre el wizard de escaneo de puertos disponibles.
        Aparece como botón en el header del formulario de instancia.
        """
        self.ensure_one()
        wizard = self.env['micro.saas.wizard.puertos.disponibles'].create({
            'instancia_id': self.id,
            'puerto_inicio': _DEFAULT_PORT_START,
            'puerto_fin': _DEFAULT_PORT_END,
            'max_resultados': 30,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': '🔌 Puertos Disponibles',
            'res_model': 'micro.saas.wizard.puertos.disponibles',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'context': self.env.context,
        }
