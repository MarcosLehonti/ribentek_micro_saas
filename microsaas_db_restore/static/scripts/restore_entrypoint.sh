#!/bin/bash
# =============================================================================
# restore_entrypoint.sh
# Script de entrypoint para contenedor Odoo con restauración automática de BD.
#
# VARIABLES DE ENTORNO REQUERIDAS (inyectadas por microsaas_db_restore):
#   RESTORE_DB=1                        -> Activa la restauración
#   RESTORE_DB_NAME=nombre_bd           -> Nombre de la BD a crear
#   RESTORE_ZIP_PATH=/mnt/restore/backup.zip  -> Ruta al ZIP dentro del contenedor
#   RESTORE_MASTER_PASSWORD=admin       -> Master password de Odoo
#
# CÓMO USAR EN TU DOCKERFILE:
#   COPY restore_entrypoint.sh /entrypoint_restore.sh
#   RUN chmod +x /entrypoint_restore.sh
#   ENTRYPOINT ["/entrypoint_restore.sh"]
#
# O en docker-compose como command:
#   command: /entrypoint_restore.sh
# =============================================================================

set -e

RESTORE_DB="${RESTORE_DB:-0}"
RESTORE_DB_NAME="${RESTORE_DB_NAME:-odoo}"
RESTORE_ZIP_PATH="${RESTORE_ZIP_PATH:-/mnt/restore/backup.zip}"
RESTORE_MASTER_PASSWORD="${RESTORE_MASTER_PASSWORD:-admin}"
ODOO_HOST="localhost"
ODOO_PORT="${HTTP_PORT:-8069}"
MAX_WAIT=120   # segundos máximos esperando que Odoo arranque

# ── Colores para el log ──────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[RESTORE][INFO]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[RESTORE][WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[RESTORE][ERROR]${NC} $1"; }

# ── Función: esperar que Odoo esté disponible ────────────────────────────────
wait_for_odoo() {
    log_info "Esperando que Odoo esté disponible en ${ODOO_HOST}:${ODOO_PORT}..."
    local elapsed=0
    until curl -sf "http://${ODOO_HOST}:${ODOO_PORT}/web/database/selector" > /dev/null 2>&1; do
        if [ "$elapsed" -ge "$MAX_WAIT" ]; then
            log_error "Timeout: Odoo no respondió en ${MAX_WAIT} segundos."
            exit 1
        fi
        sleep 3
        elapsed=$((elapsed + 3))
        log_info "Esperando... (${elapsed}s / ${MAX_WAIT}s)"
    done
    log_info "Odoo disponible."
}

# ── Función: verificar si la BD ya existe ────────────────────────────────────
db_exists() {
    local result
    result=$(curl -sf \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"jsonrpc\":\"2.0\",\"method\":\"call\",\"params\":{}}" \
        "http://${ODOO_HOST}:${ODOO_PORT}/web/database/list" 2>/dev/null || echo "")

    if echo "$result" | grep -q "\"${RESTORE_DB_NAME}\""; then
        return 0  # existe
    fi
    return 1  # no existe
}

# ── Función principal de restauración ────────────────────────────────────────
restore_database() {
    log_info "========================================================"
    log_info " INICIANDO RESTAURACIÓN AUTOMÁTICA DE BASE DE DATOS"
    log_info "  BD objetivo : ${RESTORE_DB_NAME}"
    log_info "  Archivo ZIP : ${RESTORE_ZIP_PATH}"
    log_info "========================================================"

    # Verificar que el ZIP existe
    if [ ! -f "${RESTORE_ZIP_PATH}" ]; then
        log_error "No se encontró el archivo ZIP en: ${RESTORE_ZIP_PATH}"
        log_error "Verifica que el volumen esté correctamente montado en docker-compose."
        exit 1
    fi

    log_info "Archivo ZIP encontrado: $(du -h ${RESTORE_ZIP_PATH} | cut -f1)"

    # Verificar si la BD ya existe para no restaurar dos veces
    if db_exists; then
        log_warn "La base de datos '${RESTORE_DB_NAME}' ya existe. Saltando restauración."
        return 0
    fi

    # Llamar al endpoint de restauración de Odoo
    log_info "Enviando ZIP al endpoint /web/database/restore..."

    HTTP_STATUS=$(curl -s -o /tmp/restore_response.txt -w "%{http_code}" \
        -X POST \
        -F "master_pwd=${RESTORE_MASTER_PASSWORD}" \
        -F "name=${RESTORE_DB_NAME}" \
        -F "backup_file=@${RESTORE_ZIP_PATH}" \
        -F "copy=false" \
        "http://${ODOO_HOST}:${ODOO_PORT}/web/database/restore")

    RESPONSE=$(cat /tmp/restore_response.txt 2>/dev/null || echo "")

    if [ "$HTTP_STATUS" = "200" ] || echo "$RESPONSE" | grep -qi "ok\|success\|/web"; then
        log_info "✅ BASE DE DATOS '${RESTORE_DB_NAME}' RESTAURADA EXITOSAMENTE"
        # Crear archivo de bandera para no restaurar en reinicios futuros
        touch /tmp/.db_restored_${RESTORE_DB_NAME}
    else
        log_error "Error en la restauración. HTTP Status: ${HTTP_STATUS}"
        log_error "Respuesta del servidor:"
        cat /tmp/restore_response.txt
        exit 1
    fi
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
if [ "${RESTORE_DB}" = "1" ]; then
    # Verificar si ya fue restaurada en este contenedor (evitar doble restauración)
    if [ -f "/tmp/.db_restored_${RESTORE_DB_NAME}" ]; then
        log_warn "La BD ya fue restaurada en esta sesión del contenedor. Saltando."
    else
        # Primero arrancamos Odoo en background
        log_info "Arrancando Odoo en background para poder restaurar..."
        /entrypoint.sh odoo &
        ODOO_PID=$!

        # Esperamos a que esté listo
        wait_for_odoo

        # Ejecutamos la restauración
        restore_database

        # Detenemos Odoo para reiniciarlo limpiamente con la BD ya disponible
        log_info "Reiniciando Odoo con la base de datos restaurada..."
        kill $ODOO_PID 2>/dev/null || true
        wait $ODOO_PID 2>/dev/null || true
        sleep 2
    fi
fi

# Arranque normal de Odoo (pasa todos los argumentos originales)
log_info "Iniciando Odoo normalmente..."
exec /entrypoint.sh "$@"
