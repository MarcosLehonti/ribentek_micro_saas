# -*- coding: utf-8 -*-
import socket
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

_DEFAULT_PORT_START = 8073
_DEFAULT_PORT_END   = 9999
_MAX_PUERTOS_MOSTRAR = 30   # Limitar para no bloquear el UI con miles de registros


class LineaPuertoDisponible(models.TransientModel):
    """Línea de puerto disponible que se muestra en el wizard."""
    _name = 'micro.saas.linea.puerto.disponible'
    _description = 'Línea de puerto disponible'

    wizard_id = fields.Many2one(
        'micro.saas.wizard.puertos.disponibles',
        string='Wizard',
        ondelete='cascade',
    )
    puerto = fields.Integer(string='Puerto')
    disponible = fields.Boolean(string='Disponible', default=True)
    nota = fields.Char(string='Nota')


class WizardPuertosDisponibles(models.TransientModel):
    """
    Wizard temporal que escanea el rango de puertos y
    muestra cuáles están libres para asignar a nuevas instancias.
    """
    _name = 'micro.saas.wizard.puertos.disponibles'
    _description = 'Puertos Disponibles para Instancias'

    instancia_id = fields.Many2one(
        'odoo.docker.instance',
        string='Instancia',
        readonly=True,
    )
    puerto_inicio = fields.Integer(
        string='Puerto Inicio',
        default=_DEFAULT_PORT_START,
    )
    puerto_fin = fields.Integer(
        string='Puerto Fin',
        default=_DEFAULT_PORT_END,
    )
    max_resultados = fields.Integer(
        string='Máx. resultados',
        default=_MAX_PUERTOS_MOSTRAR,
        help='Cantidad máxima de puertos disponibles a mostrar',
    )
    puerto_ids = fields.One2many(
        'micro.saas.linea.puerto.disponible',
        'wizard_id',
        string='Puertos Disponibles',
        readonly=True,
    )
    total_encontrados = fields.Integer(
        string='Total encontrados',
        readonly=True,
    )
    resumen = fields.Html(
        string='Resumen',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        return res

    def action_escanear(self):
        """
        Escanea el rango de puertos y devuelve los disponibles.
        Un puerto es 'disponible' si:
          - No está registrado como activo en micro.saas.puerto.usado
          - No está en uso por ninguna instancia activa en BD
          - No está ocupado a nivel de SO (socket bind)
          - No es reservado del Odoo maestro (8069, 8071, 8072)
        """
        self.ensure_one()
        inicio = self.puerto_inicio or _DEFAULT_PORT_START
        fin = self.puerto_fin or _DEFAULT_PORT_END
        max_res = self.max_resultados or _MAX_PUERTOS_MOSTRAR

        # 1. Puertos de instancias en BD
        instances = self.env['odoo.docker.instance'].search([])
        ports_en_uso = set()
        for inst in instances:
            for pf in ('http_port', 'longpolling_port'):
                val = getattr(inst, pf, None)
                if val:
                    try:
                        ports_en_uso.add(int(val))
                    except (ValueError, TypeError):
                        pass

        # 2. Puertos reservados en historial
        puertos_reservados = self.env['micro.saas.puerto.usado'].search([
            ('activo', '=', True)
        ])
        for p in puertos_reservados:
            ports_en_uso.add(p.puerto)

        # 3. Reservados del Odoo maestro
        ports_en_uso.update({8069, 8071, 8072})

        # 4. Borrar líneas anteriores
        self.puerto_ids.unlink()

        # 5. Escanear
        disponibles = []
        escaneados = 0
        encontrados = 0

        for port in range(inicio, fin + 1):
            escaneados += 1
            if port in ports_en_uso:
                continue

            # Verificar a nivel SO
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            try:
                sock.bind(("0.0.0.0", port))
                disponibles.append({
                    'wizard_id': self.id,
                    'puerto': port,
                    'disponible': True,
                    'nota': 'Libre',
                })
                encontrados += 1
            except (OSError, socket.error):
                # Puerto ocupado a nivel SO, saltar
                pass
            finally:
                sock.close()

            if encontrados >= max_res:
                break

        # 6. Crear líneas
        for data in disponibles:
            self.env['micro.saas.linea.puerto.disponible'].create(data)

        # 7. Resumen HTML
        resumen_html = (
            f"<p>✅ <strong>{encontrados}</strong> puertos disponibles encontrados "
            f"(escaneados: <strong>{escaneados}</strong> del rango "
            f"<strong>{inicio}–{fin}</strong>).</p>"
            f"<p>🚫 Puertos excluidos (en uso o reservados): "
            f"<strong>{len(ports_en_uso)}</strong></p>"
        )
        if encontrados == 0:
            resumen_html += (
                "<p class='text-danger'>⚠️ No se encontraron puertos libres en el rango. "
                "Considera ampliar el rango o liberar puertos desde <em>Puertos Usados</em>.</p>"
            )

        self.write({
            'total_encontrados': encontrados,
            'resumen': resumen_html,
        })

        # Reabrir el wizard
        return {
            'type': 'ir.actions.act_window',
            'name': '🔌 Puertos Disponibles',
            'res_model': 'micro.saas.wizard.puertos.disponibles',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }
