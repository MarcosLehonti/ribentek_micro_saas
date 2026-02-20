{
    "name": "Micro SaaS - Mejoras y Correcciones",
    "category": "Tools",
    "summary": "Correcciones de puertos, descarga de imágenes y estabilidad para Micro SaaS",
    "description": """
        Micro SaaS Mejora v2
        ====================
        Corrige los problemas principales del módulo micro_saas:
        
        🔧 Correcciones críticas:
        - Puerto 8072 ya no colisiona con el Odoo maestro (rango inicia en 8073)
        - Descarga imagen Docker ANTES de iniciar (evita timeout bloqueante)
        - Limpia contenedores fallidos antes de re-intentar inicio
        - Valida puertos a nivel de SO antes de asignarlos
        - Entrecomilla rutas con espacios en comandos Docker
        - Elimina logfile de odoo.conf (causaba crash en imágenes oficiales)
        
        📋 Mejoras:
        - Registro histórico de puertos usados
        - Variables de template copiadas por valor (no por referencia)
        - Limpieza completa al eliminar instancia (cualquier estado)
        - Mensajes de log claros con emojis y diagnóstico automático
        - Mejor manejo de errores con soluciones sugeridas
    """,
    "author": "Marcos Guzman",
    "license": "LGPL-3",
    "version": "17.0.2.0.0",
    "depends": [
        "base",
        "micro_saas",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/odoo_docker_instance_mejora.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}