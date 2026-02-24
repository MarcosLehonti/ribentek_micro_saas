# -*- coding: utf-8 -*-
import logging
import re

from odoo import models, api, Command

_logger = logging.getLogger(__name__)


class DockerComposeTemplateMejora(models.Model):
    """
    Hereda docker.compose.template para corregir el bug donde
    las variables del template se borran cuando se elimina una instancia.

    También mejora _default_template_odoo_conf para que no use logfile
    (la carpeta /var/log/odoo no existe en las imágenes oficiales y causa crash).
    """
    _inherit = 'docker.compose.template'

    def _default_template_odoo_conf(self):
        """
        Override: NO incluir logfile y asegurar addons_path completo.
        """
        odoo_conf_content = "[options]\n"
        odoo_conf_content += "addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons\n"
        odoo_conf_content += "admin_passwd = admin\n"
        odoo_conf_content += "data_dir = /var/lib/odoo\n"
        odoo_conf_content += "db_host = db\n"
        odoo_conf_content += "db_user = odoo\n"
        odoo_conf_content += "db_password = odoo\n"
        odoo_conf_content += "db_port = 5432\n"
        return odoo_conf_content

    @api.depends('template_dc_body', 'template_odoo_conf', 'template_postgres_conf')
    def _compute_variable_ids(self):
        """
        Override: compute template variables según los placeholders.
        Corrige el bug donde al borrar una instancia, se eliminaban las variables
        del template padre.
        """
        for tmpl in self:
            # Extraer todas las variables de las 3 plantillas
            body_variables = set(re.findall(r'{{[^{}]+}}', tmpl.template_dc_body or ''))
            body_variables = body_variables.union(
                set(re.findall(r'{{[^{}]+}}', tmpl.template_odoo_conf or ''))
            )
            body_variables = body_variables.union(
                set(re.findall(r'{{[^{}]+}}', tmpl.template_postgres_conf or ''))
            )

            # Variables existentes indexadas por nombre
            existing_vars = {var.name: var for var in tmpl.variable_ids}

            # Variables nuevas
            new_var_names = [
                var_name for var_name in body_variables
                if var_name not in existing_vars
            ]

            # Variables a eliminar (solo las que ya no aparecen y pertenecen a ESTE registro)
            vars_to_delete = []
            for name, var in existing_vars.items():
                if name not in body_variables:
                    if var.id:
                        vars_to_delete.append(var.id)

            # Comandos de actualización
            update_commands = []
            for del_id in vars_to_delete:
                update_commands.append(Command.delete(del_id))
            for var_name in set(new_var_names):
                update_commands.append(Command.create({'name': var_name}))

            if update_commands:
                tmpl.variable_ids = update_commands
