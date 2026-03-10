# -*- coding: utf-8 -*-
{
    'name': 'MicroSaaS - Restauración de Base de Datos',
    'version': '17.0.1.0.0',
    'summary': 'Copia una BD plantilla (ZIP) a una instancia Docker recién creada',
    'description': """
        Flujo:
        1. Se crea y levanta la instancia Docker normalmente (sin BD)
        2. Desde la instancia, el usuario presiona "Restaurar BD Plantilla"
        3. Se abre un wizard de confirmación con el ZIP seleccionado
        4. El servidor llama al endpoint /web/database/restore de la instancia nueva
        5. Odoo restaura el ZIP (BD + filestore) internamente
        6. Al abrir la URL ya está el Odoo configurado con los datos de la plantilla
    """,
    'author': 'MicroSaaS',
    'category': 'Technical',
    'depends': ['base', 'micro_saas'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_restore_db_views.xml',
        'views/odoo_docker_instance_restore_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
