import logging
import os

from odoo import models

_logger = logging.getLogger(__name__)

class OdooDockerInstance(models.Model):
    _inherit = 'odoo.docker.instance'

    def _get_computed_addons_path(self):
        self.ensure_one()
        # Siempre incluir el path base que mapea a ./addons directamente por si hay módulos extra sueltos
        paths = ["/mnt/extra-addons"]
        if self.repository_line:
            for line in self.repository_line:
                repo_name = self._get_repo_name(line)
                if repo_name:
                    paths.append("/mnt/extra-addons/" + repo_name)
        return ",".join(paths)

    def _create_odoo_conf(self):
        # Sobrescribimos esto para interceptar e inyectar correctamente {{ADDONS_PATH}}
        # garantizando que sea la lista completa de directorios de cada repositorio.
        for instance in self:
            computed_path = instance._get_computed_addons_path()
            
            content = instance.template_odoo_conf or ''
            
            # Reemplazar variables directamente para evitar fallos si variable_ids está vacío o des-sincronizado
            import re
            
            # Extraer variables del template y buscar su valor en instance.variable_ids
            # o aplicar valores por defecto de la macro
            var_dict = {}
            for var in instance.variable_ids:
                var_dict[var.name] = var.demo_value or ' '
                
            # Sobrescribir ADDONS_PATH con nuestra ruta calculada
            var_dict['{{ADDONS_PATH}}'] = computed_path
            
            # Reemplazos de seguridad por si no existen en val_dict
            default_vars = {
                '{{DB_HOST}}': 'db',
                '{{DB_USER}}': 'odoo',
                '{{DB_PASSWORD}}': 'odoo',
                '{{HTTP-PORT}}': instance.http_port or '8069',
                '{{LONGPOLLING-PORT}}': instance.longpolling_port or '8072',
                '{{ADDONS_PATH}}': computed_path
            }
            
            # Realizar el reemplazo real
            for placeholder, default_val in default_vars.items():
                val = var_dict.get(placeholder, default_val)
                content = content.replace(placeholder, val)
                
            # Limpiar cualquier otro placeholder que haya quedado sin reemplazar
            content = re.sub(r'{{.*?}}', ' ', content)

                
            odoo_conf_content = content
            odoo_conf_path = os.path.join(instance.instance_data_path, "etc", 'odoo.conf')
            instance._makedirs(os.path.dirname(odoo_conf_path))
            try:
                instance.create_file(odoo_conf_path, odoo_conf_content)
                instance.add_to_log(f"[INFO] Archivo odoo.conf creado/actualizado exitosamente con addons: {computed_path}")
            except Exception as e:
                instance.add_to_log(f"[ERROR] Error al crear el archivo odoo.conf en {odoo_conf_path}")
                instance.write({'state': 'error'})
                if hasattr(e, 'stderr') and e.stderr:
                    instance.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
                else:
                    instance.add_to_log("[ERROR]  " + str(e))
                instance.write({'state': 'stopped'})

    def _clone_repositories(self):
        # Sobrescribimos el clonado para agregar la funcionalidad de que si la carpeta ya existe,
        # ejecute directamente un git pull en vez de dar error en el clone.
        for instance in self:
            for line in instance.repository_line:
                repo_name = self._get_repo_name(line)
                repo_path = os.path.join(instance.instance_data_path, "addons", repo_name)
                
                if os.path.exists(repo_path) and os.path.isdir(os.path.join(repo_path, '.git')):
                    try:
                        cmd = f"cd {repo_path} && git fetch --all && git reset --hard origin/{line.name} && git pull origin {line.name}"
                        instance.excute_command(cmd, shell=True, check=True)
                        instance.add_to_log(f"[INFO] Repository updated (pull): {line.repository_id.name} (Branch: {line.name})")
                        line.is_clone = True
                    except Exception as e:
                        instance.add_to_log(f"[ERROR] Error to update repository: {line.repository_id.name} (Branch: {line.name})")
                        if hasattr(e, 'stderr') and e.stderr:
                            instance.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
                        else:
                            instance.add_to_log("[ERROR]  " + str(e))
                else:
                    instance._makedirs(repo_path)
                    try:
                        cmd = f"git clone {line.repository_id.name} -b {line.name} {repo_path}"
                        instance.excute_command(cmd, shell=True, check=True)
                        instance.add_to_log(f"[INFO] Repository cloned: {line.repository_id.name} (Branch: {line.name})")
                        line.is_clone = True
                    except Exception as e:
                        instance.add_to_log(f"[ERROR] Error to clone repository: {line.repository_id.name} (Branch: {line.name})")
                        if hasattr(e, 'stderr') and e.stderr:
                            instance.add_to_log("[ERROR]  " + e.stderr.decode('utf-8'))
                        else:
                            instance.add_to_log("[ERROR]  " + str(e))
