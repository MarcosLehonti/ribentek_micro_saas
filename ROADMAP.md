# 🚀 ROADMAP - Portal SaaS de Odoo

## 📋 Información del Proyecto

**Proyecto:** Sistema Automatizado de Venta y Provisión de Instancias Odoo  
**Metodología:** Scrum Adaptado  
**Duración Estimada:** 8-12 semanas  
**Equipo:** 2 desarrolladores (Backend/DevOps + Frontend/Odoo)  
**Versión del Documento:** 1.0  

---

## 🎯 Visión General

Un sistema de venta automatizada de instancias Odoo que funciona como un servicio SaaS. El cliente entra a una página web, compra una suscripción, y automáticamente recibe su propia instalación completa de Odoo.

### Modelo de Negocio
- Cliente paga $10/mes → Recibe su Odoo completo
- Si no paga el segundo mes → Sistema se suspende automáticamente
- Paga de nuevo → Sistema se reactiva inmediatamente

---

## 📊 Estado General del Proyecto

### Progreso por Épicas
- [ ] **ÉPICA 1:** Infraestructura Base (8/10)
- [ ] **ÉPICA 2:** Portal Web y eCommerce (7/14)
- [ ] **ÉPICA 3:** Sistema de Provisión Automática (0/19)
- [ ] **ÉPICA 4:** Gestión de Ciclo de Vida (0/15)
- [ ] **ÉPICA 5:** Portal del Cliente (0/11)
- [ ] **ÉPICA 6:** Sistema de Notificaciones (0/11)
- [ ] **ÉPICA 7:** Integración de Pagos (0/9)
- [ ] **ÉPICA 8:** Despliegue a Producción (0/15)

### Progreso por Sprints
- [X] **Sprint 1:** Fundamentos (Semana 1)
- [X] **Sprint 2:** Portal Web (Semana 2)
- [X] **Sprint 3:** Fundamentos del Módulo (Semana 3)
- [X] **Sprint 4:** Captura de Ventas (Semana 4)
- [ ] **Sprint 5:** Creación de Instancias (Semana 5)
- [ ] **Sprint 6:** Suspensión Automática (Semana 6)
- [ ] **Sprint 7:** Reactivación (Semana 7)
- [ ] **Sprint 8:** Portal del Cliente (Semana 8)
- [ ] **Sprint 9:** Notificaciones (Semana 9)
- [ ] **Sprint 10:** Pagos Reales (Semana 10)
- [ ] **Sprint 11:** Infraestructura Cloud (Semana 11)
- [ ] **Sprint 12:** Producción Final (Semana 12)

---

## 🏗️ ÉPICA 1: Infraestructura Base

**Objetivo:** Configurar servidor y entorno de desarrollo  
**Sprint:** 1 (Semana 1)  
**Criterios de Aceptación:**
- ✅ Puedo entrar a http://IP_UBUNTU:8069 desde Windows
- ✅ Puedo crear una base de datos
- ✅ Puedo activar modo desarrollador
- ✅ Puedo ver la carpeta de addons vacía

### Tareas

#### E1-001: [SPIKE] Investigar Docker y contenedores
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Descripción:** Entender qué es Docker, cómo funcionan los contenedores, diferencia entre imagen y contenedor
- **Comandos/Notas:**
```bash
# Comandos útiles aprendidos:

```

---

#### E1-002: Instalar Ubuntu Server en VirtualBox (Realizado)
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Descripción:** Descargar Ubuntu Server 22.04 LTS e instalarlo en VirtualBox
- **Comandos/Notas:**
```bash
# Versión instalada:

# Configuración de VM:
# - RAM:
# - CPU:
# - Disco:
```

---

#### E1-003: Configurar red bridged para acceso desde host (Realizado)
- [x] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Descripción:** Configurar red en modo bridge para que Windows pueda acceder al Ubuntu
- **Comandos/Notas:**
```bash
# IP asignada a Ubuntu:

# Comando para verificar:
ip addr show
```

---

#### E1-004: Instalar Docker Engine en Ubuntu
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Descripción:** Instalar Docker siguiendo documentación oficial
- **Comandos/Notas:**
```bash
# Comandos de instalación:
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Verificar instalación:
docker --version

# Agregar usuario al grupo docker:
sudo usermod -aG docker $USER
```

---

#### E1-005: Instalar Docker Compose
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Descripción:** Instalar Docker Compose para orquestar contenedores
- **Comandos/Notas:**
```bash
# Comandos de instalación:
sudo apt install -y docker-compose

# Verificar instalación:
docker-compose --version
```

---

#### E1-006: Crear estructura de proyecto
- [x] Completada
- **Prioridad:** High
- **Estimación:** 1 punto
- **Descripción:** Crear carpetas para el proyecto
- **Comandos/Notas:**
```bash
# Estructura creada:
mkdir -p ~/odoo-saas-project/{addons,config}
cd ~/odoo-saas-project

# Árbol de directorios:
# odoo-saas-project/
# ├── addons/           # Módulos personalizados
# ├── config/           # Configuraciones
# └── docker-compose.yml
```

---

#### E1-007: Configurar docker-compose.yml para Odoo Maestro
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Descripción:** Crear archivo docker-compose.yml con servicios de PostgreSQL y Odoo
- **Comandos/Notas:**
```yaml
# Archivo docker-compose.yml:


```

---

#### E1-008: Levantar Odoo Maestro + PostgreSQL
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Descripción:** Ejecutar docker-compose up y verificar que los servicios arrancan
- **Comandos/Notas:**
```bash
# Comando para levantar:
docker-compose up -d

# Verificar contenedores:
docker ps

# Ver logs:
docker logs odoo_maestro
```

---

#### E1-009: Verificar acceso desde navegador Windows
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Descripción:** Abrir navegador en Windows y acceder a http://IP_UBUNTU:8069
- **Comandos/Notas:**
```bash
# URL de acceso:
http://[IP_UBUNTU]:8069

# Crear primera base de datos con:
# - Nombre: odoo_maestro
# - Usuario admin: admin
# - Contraseña: [anotar aquí]
```

---

#### E1-010: Configurar volumen para addons personalizados
- [x] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Descripción:** Montar carpeta de addons en el contenedor de Odoo
- **Comandos/Notas:**
```bash
# Modificación en docker-compose.yml:
# volumes:
#   - ./addons:/mnt/extra-addons

# Reiniciar servicios:
docker-compose restart

# Verificar dentro del contenedor:
docker exec -it odoo_maestro ls /mnt/extra-addons
```

---

## 🌐 ÉPICA 2: Portal Web y eCommerce

**Objetivo:** Crear la tienda online funcional  
**Sprint:** 2 (Semana 2)  
**Criterios de Aceptación:**
- ✅ Un visitante puede ver los planes
- ✅ Puede registrarse
- ✅ Puede agregar un plan al carrito
- ✅ Puede llegar hasta el checkout (sin pagar aún)

### Tareas

#### E2-001: Landing page atractiva
- [x] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Historia de Usuario:** Como visitante, quiero ver una landing page atractiva que explique el servicio
- **Comandos/Notas:**
```bash
# Módulos instalados:
# - Website

# URL de la página:

# Elementos incluidos:
# - Hero section con propuesta de valor
# - Sección "Cómo funciona"
# - Call to action
```

---

#### E2-002: Página de precios
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Historia de Usuario:** Como visitante, quiero ver los planes disponibles con sus precios
- **Comandos/Notas:**
```bash
# Planes configurados:
# - Plan Básico: $10/mes
# - Plan Pro: $[precio]/mes (si aplica)
# - Plan Enterprise: $[precio]/mes (si aplica)
```

---

#### E2-003: Instalar módulo Website en Odoo
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Comandos/Notas:**
```bash
# Instalado desde: Apps > Website
# Versión:
```

---

#### E2-004: Instalar módulo eCommerce en Odoo
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Comandos/Notas:**
```bash
# Instalado desde: Apps > eCommerce (website_sale)
# Versión:
```

---

#### E2-005: Diseñar página de inicio con Website Builder
- [X] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Comandos/Notas:**
```bash
# Editor usado: Website > Edit
# Bloques utilizados:
# - 
# - 
```

---

#### E2-006: Crear página "Cómo Funciona"
- [X] Completada
- **Prioridad:** Medium
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# URL: /como-funciona
# Secciones incluidas:
# 1. Registrarse
# 2. Elegir plan
# 3. Pagar
# 4. Recibir Odoo
```

---

#### E2-007: Crear página "Precios"
- [X] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# URL: /precios
# Diseño: Tarjetas comparativas
```

---

#### E2-008: Configurar productos: Plan Básico, Plan Pro
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# Productos creados en: Sales > Products
# Plan Básico:
#   - Precio: $10
#   - Tipo: Service
#   - Categoria: Suscripciones

# Plan Pro (si aplica):
#   - Precio: $
#   - Tipo: Service
```

---

#### E2-009: Configurar precios y descripciones
- [X] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Descripción incluida para cada producto
# Características destacadas
```

---

#### E2-010: Personalizar tema visual (colores, logo)
- [X] Completada
- **Prioridad:** Medium
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# Tema seleccionado:
# Colores principales:
#   - Primario: #
#   - Secundario: #
# Logo subido: [nombre archivo]
```

---

#### E2-011: Sistema de registro
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Historia de Usuario:** Como cliente, quiero poder registrarme en el sitio
- **Comandos/Notas:**
```bash
# Formulario de registro habilitado en:
# /web/signup
```

---

#### E2-012: Sistema de login
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Historia de Usuario:** Como cliente, quiero poder hacer login
- **Comandos/Notas:**
```bash
# URL login: /web/login
```

---

#### E2-013: Configurar formulario de registro
- [X] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Campos del formulario:
# - Nombre
# - Email
# - Empresa (opcional)
# - Contraseña
```

---

#### E2-014: Probar flujo completo de registro
- [X] Completada
- **Prioridad:** High
- **Estimación:** 1 punto
- **Comandos/Notas:**
```bash
# Usuario de prueba creado:
# Email:
# Contraseña:

# Verificado:
# ✓ Registro exitoso
# ✓ Email de confirmación (si aplica)
# ✓ Puede hacer login
```

---

## ⚙️ ÉPICA 3: Sistema de Provisión Automática

**Objetivo:** Automatizar creación de instancias  
**Sprints:** 3, 4, 5 (Semanas 3-5)  
**Criterios de Aceptación (Sprint 5):**
- ✅ Hago una venta de prueba
- ✅ Automáticamente se crean 2 contenedores (PostgreSQL + Odoo)
- ✅ Puedo acceder a http://IP:PUERTO_ASIGNADO
- ✅ Veo pantalla de Odoo del cliente
- ✅ Los datos están aislados del maestro

### Tareas - Sprint 3: Fundamentos del Módulo

#### E3-001: [SPIKE] Investigar Odoo ORM y herencia de modelos
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```python
# Conceptos clave aprendidos:
# - models.Model
# - Herencia: _inherit
# - Campos: fields.Char, fields.Integer, etc.
# - Métodos: @api.model, @api.depends
```

---

#### E3-002: [SPIKE] Investigar subprocess y comandos Docker desde Python
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```python
# Ejemplos probados:
import subprocess

# Ejemplo 1: Ejecutar comando simple


# Ejemplo 2: Capturar salida


# Ejemplo 3: Manejo de errores

```

---

#### E3-003: Crear estructura del módulo saas_docker_manager
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```bash
# Estructura creada en: ~/odoo-saas-project/addons/

mkdir -p saas_docker_manager
cd saas_docker_manager
touch __init__.py __manifest__.py
mkdir models security views
touch models/__init__.py
touch models/saas_instance.py

# Árbol de directorios:
# saas_docker_manager/
# ├── __init__.py
# ├── __manifest__.py
# ├── models/
# │   ├── __init__.py
# │   └── saas_instance.py
# ├── views/
# │   └── saas_instance_views.xml
# └── security/
#     └── ir.model.access.csv
```

---

#### E3-004: Configurar __manifest__.py con dependencias
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Sprint:** 3
- **Comandos/Notas:**
```python
# Contenido de __manifest__.py:


```

---

#### E3-005: Crear modelo saas.instance para control de instancias
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```python
# Modelo creado en: models/saas_instance.py


```

---

#### E3-006: Definir campos del modelo
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```python
# Campos definidos:
# - name (cliente)
# - container_name
# - port
# - database_name
# - admin_password
# - state (draft/active/suspended/deleted)
# - expiration_date
# - last_payment_date
# - sale_order_id (relación)
```

---

#### E3-007: Crear vistas XML para gestión de instancias
- [X] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Sprint:** 3
- **Comandos/Notas:**
```xml
<!-- Vistas creadas en: views/saas_instance_views.xml -->

<!-- Vista de árbol (list) -->

<!-- Vista de formulario (form) -->

<!-- Menú -->

```

---

### Tareas - Sprint 4: Captura de Ventas

#### E3-008: Implementar método para calcular siguiente puerto disponible
- [X] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Método implementado:


# Lógica:
# - Buscar el puerto más alto en uso
# - Retornar puerto_max + 1
# - Si no hay ninguno, empezar en 8071
```

---

#### E3-009: Heredar modelo sale.order para detectar ventas
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Herencia creada en: models/sale_order_inherit.py


```

---

#### E3-010: Sobrescribir método action_confirm()
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Método sobrescrito:


```

---

#### E3-011: Implementar validación de producto 
- [X] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Validación implementada:
# - Buscar en order_line si algún producto es de tipo "Plan Odoo"
# - Puede ser por categoría o por nombre
```

---

#### E3-012: Crear función para generar contraseña
- [X] Completada
- **Prioridad:** Medium
- **Estimación:** 2 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Función implementada:


# Genera contraseñas de 12 caracteres con:
# - Letras mayúsculas
# - Letras minúsculas
# - Números
# - Símbolos
```

---

#### E3-013: Implementar creación de registro en saas.instance
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 4
- **Comandos/Notas:**
```python
# Código implementado:


# Datos guardados:
# - Cliente (partner_id de la venta)
# - Puerto calculado
# - Contraseña generada
# - Fecha expiración: hoy + 30 días
# - Estado: 'draft'
```

---

### Tareas - Sprint 5: Creación de Instancias

#### E3-014: Implementar comando Docker para crear PostgreSQL del cliente
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 8 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```python
# Función implementada: _create_postgres_container()

# Comando Docker ejecutado:
# docker run -d \
#   --name db_cliente_X \
#   --network odoo_network \
#   -e POSTGRES_USER=odoo \
#   -e POSTGRES_PASSWORD=odoo \
#   -e POSTGRES_DB=postgres \
#   postgres:15
```

---

#### E3-015: Implementar comando Docker para crear Odoo del cliente
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 8 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```python
# Función implementada: _create_odoo_container()


# Comando Docker ejecutado:
# docker run -d \
#   --name odoo_cliente_X \
#   --network odoo_network \
#   -p 8071:8069 \
#   -e HOST=db_cliente_X \
#   -e USER=odoo \
#   -e PASSWORD=odoo \
#   odoo:17
```

---

#### E3-016: Implementar gestión de red Docker
- [X] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```bash
# Crear red Docker (una vez):
docker network create odoo_network

# Verificar red:
docker network ls
docker network inspect odoo_network
```

---

#### E3-017: Implementar manejo de errores en creación
- [X] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```python
# Errores manejados:
# - Puerto ya en uso
# - Nombre de contenedor duplicado
# - Docker no disponible
# - Timeout en creación

# En caso de error:
# - Actualizar estado a 'error'
# - Registrar mensaje de error
# - Notificar al admin
```

---

#### E3-018: Probar creación manual de instancia
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```bash
# Prueba manual:
# 1. Ir a SaaS > Instancias
# 2. Crear nueva instancia
# 3. Hacer clic en botón "Provisionar"

# Verificar:
# - Contenedores creados
# - Acceso a http://IP:PUERTO
# - Base de datos creada
```

---

#### E3-019: Probar creación automática tras venta
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 5
- **Comandos/Notas:**
```bash
# Prueba end-to-end:
# 1. Crear venta manual de "Plan Básico"
# 2. Confirmar la venta
# 3. Esperar ~30 segundos
# 4. Verificar que se creó instancia
# 5. Verificar acceso a la instancia

# Resultado:
# ✓ Instancia creada automáticamente
# ✓ Puerto asignado: 
# ✓ URL de acceso: http://IP:
# ✓ Credenciales funcionan
```

---

## 🔄 ÉPICA 4: Gestión de Ciclo de Vida

**Objetivo:** Automatizar suspensión/reactivación  
**Sprints:** 6, 7 (Semanas 6-7)  
**Criterios de Aceptación (Sprint 7):**
- ✅ Instancia está suspendida
- ✅ Hago una "renovación" (venta del mismo producto)
- ✅ La instancia se reactiva automáticamente
- ✅ Puedo acceder de nuevo
- ✅ Los datos están intactos

### Tareas - Sprint 6: Suspensión Automática

#### E4-001: [SPIKE] Investigar Cron Jobs en Odoo
- [X] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Conceptos aprendidos:
# - ir.cron model
# - Interval types: days, hours, minutes
# - nextcall
# - Como crear cron desde XML
```

---

#### E4-002: Scheduled Action para verificación diaria
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 6
- **Historia de Usuario:** Como sistema, quiero verificar diariamente las suscripciones expiradas
- **Comandos/Notas:**
```xml
<!-- Cron creado en: data/cron_data.xml -->


<!-- Configuración:
- Intervalo: 1 día
- Hora de ejecución: 00:00
- Modelo: saas.instance
- Método: _cron_check_expired_subscriptions
-->
```

---

#### E4-003: Crear Scheduled Action
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```bash
# Verificar cron creado:
# Settings > Technical > Automation > Scheduled Actions

# Nombre: Check Expired Subscriptions
```

---

#### E4-004: Implementar método _cron_check_expired_subscriptions()
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Método implementado:


```

---

#### E4-005: Implementar lógica de búsqueda de instancias expiradas
- [x] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Búsqueda implementada:
# domain = [
#     ('state', '=', 'active'),
#     ('expiration_date', '<', fields.Date.today())
# ]
```

---

#### E4-006: Implementar función action_stop_container()
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Método implementado:


```

---

#### E4-007: Implementar comando docker stop
- [x] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Comandos ejecutados:
# subprocess.run(['docker', 'stop', container_name])
# subprocess.run(['docker', 'stop', db_container_name])
```

---

#### E4-008: Actualizar estado en BD a 'suspendido'
- [x] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 6
- **Comandos/Notas:**
```python
# Actualización implementada:
# self.write({
#     'state': 'suspended',
#     'suspension_date': fields.Date.today()
# })
```

---

### Tareas - Sprint 7: Reactivación

#### E4-009: Implementar función action_start_container()
- [] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Método implementado:


```

---

#### E4-010: Implementar comando docker start
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Comandos ejecutados:
# subprocess.run(['docker', 'start', db_container_name])
# time.sleep(3)  # Esperar que BD esté lista
# subprocess.run(['docker', 'start', container_name])
```

---

#### E4-011: Actualizar estado en BD a 'activo'
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Actualización implementada:
# self.write({
#     'state': 'active',
#     'expiration_date': fields.Date.today() + timedelta(days=30)
# })
```

---

#### E4-012: Implementar trigger de reactivación al pagar
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Lógica implementada en sale.order:
# - Detectar si es renovación
# - Buscar instancia del cliente
# - Si está suspendida, reactivar
```

---

#### E4-013: Detectar pago de renovación
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Validación implementada:
# - Buscar si ya existe instancia para este cliente
# - Verificar que el producto sea el mismo plan
```

---

#### E4-014: Actualizar fecha de expiración
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 7
- **Comandos/Notas:**
```python
# Actualización de fecha:
# expiration_date = today + 30 días
# last_payment_date = today
```

---

#### E4-015: Probar ciclo completo
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 7
- **Historia de Usuario:** Probar ciclo completo: expiración → suspensión → pago → reactivación
- **Comandos/Notas:**
```bash
# Pasos de prueba:
# 1. Cambiar fecha de expiración a ayer manualmente
# 2. Ejecutar cron manualmente (debug button)
# 3. Verificar que contenedor se detuvo
# 4. Crear nueva venta de renovación
# 5. Confirmar venta
# 6. Verificar que contenedor arrancó
# 7. Acceder a la instancia y verificar datos

# Resultado:
# ✓ Suspensión automática funciona
# ✓ Reactivación automática funciona
# ✓ Datos intactos
```

---

## 👤 ÉPICA 5: Portal del Cliente

**Objetivo:** Interfaz para gestión de suscripción  
**Sprint:** 8 (Semana 8)  
**Criterios de Aceptación:**
- ✅ Hago login como cliente
- ✅ Veo menú "Mi Cuenta"
- ✅ Dentro veo "Mis Instancias"
- ✅ Veo mi instancia con estado
- ✅ Hay un botón que me lleva a mi Odoo

### Tareas

#### E5-001: Vista de instancias en "Mi Cuenta"
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Historia de Usuario:** Como cliente, quiero ver mis instancias en "Mi Cuenta"
- **Comandos/Notas:**
```xml
<!-- Template creado en: views/portal_templates.xml -->


```

---

#### E5-002: Botón de acceso a Odoo
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Historia de Usuario:** Como cliente, quiero acceder a mi Odoo con un botón
- **Comandos/Notas:**
```html
<!-- Botón implementado: -->
<a href="http://[IP]:[PUERTO]" target="_blank" class="btn btn-primary">
    Acceder a mi Odoo
</a>
```

---

#### E5-003: Vista de estado de suscripción
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Historia de Usuario:** Como cliente, quiero ver el estado de mi suscripción
- **Comandos/Notas:**
```html
<!-- Estados mostrados: -->
<!-- Activo: badge verde -->
<!-- Suspendido: badge rojo -->
<!-- Draft: badge gris -->
```

---

#### E5-004: Crear template XML para portal
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Comandos/Notas:**
```xml
<!-- Archivo creado: views/portal_templates.xml -->


```

---

#### E5-005: Extender portal_my_home
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```xml
<!-- Herencia del template portal.portal_my_home -->
<!-- Agregar link a "Mis Instancias" -->
```

---

#### E5-006: Crear controlador para /my/instances
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Comandos/Notas:**
```python
# Controlador creado en: controllers/portal.py


```

---

#### E5-007: Diseñar tarjetas de instancia
- [ ] Completada
- **Prioridad:** Medium
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```html
<!-- Diseño de tarjeta: -->
<!-- - Logo Odoo -->
<!-- - Nombre de instancia -->
<!-- - Estado (badge) -->
<!-- - Fecha de expiración -->
<!-- - Botón de acceso -->
```

---

#### E5-008: Implementar botón "Acceder a mi Odoo"
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```html
<!-- URL construida dinámicamente -->
<!-- Solo visible si estado == 'active' -->
```

---

#### E5-009: Mostrar fecha de expiración
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```html
<!-- Formato: "Expira el: 15 de Marzo, 2026" -->
<!-- Mostrar días restantes -->
<!-- Alerta si quedan menos de 7 días -->
```

---

#### E5-010: Mostrar estado visual
- [ ] Completada
- **Prioridad:** Medium
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```html
<!-- Badges: -->
<!-- Activo: <span class="badge bg-success">Activo</span> -->
<!-- Suspendido: <span class="badge bg-danger">Suspendido</span> -->
```

---

#### E5-011: Implementar mensaje si no hay instancias
- [ ] Completada
- **Prioridad:** Low
- **Estimación:** 1 punto
- **Comandos/Notas:**
```html
<!-- Mensaje: "Aún no tienes instancias. ¡Compra tu primer plan!" -->
<!-- Botón: Ir a tienda -->
```

---

## 📧 ÉPICA 6: Sistema de Notificaciones

**Objetivo:** Emails automáticos funcionando  
**Sprint:** 9 (Semana 9)  
**Criterios de Aceptación:**
- ✅ Al crear instancia, recibo email con credenciales
- ✅ 7 días antes de expirar, recibo recordatorio
- ✅ Al suspenderse, recibo notificación
- ✅ Al reactivar, recibo confirmación

### Tareas

#### E6-001: Email con credenciales al crear instancia
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Historia de Usuario:** Como cliente, quiero recibir mis credenciales por email al crear instancia
- **Comandos/Notas:**
```xml
<!-- Template creado en: data/mail_templates.xml -->


```

---

#### E6-002: Email de recordatorio antes de expiración
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Historia de Usuario:** Como cliente, quiero recibir recordatorio antes de expiración
- **Comandos/Notas:**
```xml
<!-- Template: mail_template_reminder -->
<!-- Enviado: 7 días antes de expiration_date -->
```

---

#### E6-003: Email de notificación de suspensión
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Historia de Usuario:** Como cliente, quiero recibir notificación de suspensión
- **Comandos/Notas:**
```xml
<!-- Template: mail_template_suspension -->
<!-- Incluir link para renovar -->
```

---

#### E6-004: Configurar servidor SMTP en Odoo
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Configuración en: Settings > Technical > Outgoing Mail Servers

# Para desarrollo (Gmail):
# SMTP Server: smtp.gmail.com
# SMTP Port: 587
# Security: TLS
# Username: [email]
# Password: [app password]

# Probar conexión
```

---

#### E6-005: Crear plantilla de email de bienvenida
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```xml
<!-- Plantilla incluye: -->
<!-- - URL de acceso -->
<!-- - Usuario: admin -->
<!-- - Contraseña temporal -->
<!-- - Recomendación de cambiar contraseña -->
```

---

#### E6-006: Crear plantilla de email de recordatorio
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```xml
<!-- Plantilla incluye: -->
<!-- - Fecha de expiración -->
<!-- - Mensaje amigable -->
<!-- - Link para renovar -->
```

---

#### E6-007: Crear plantilla de email de suspensión
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```xml
<!-- Plantilla incluye: -->
<!-- - Fecha de suspensión -->
<!-- - Mensaje explicativo -->
<!-- - Botón "Renovar Ahora" -->
```

---

#### E6-008: Crear plantilla de email de reactivación
- [ ] Completada
- **Prioridad:** Medium
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```xml
<!-- Plantilla incluye: -->
<!-- - Confirmación de reactivación -->
<!-- - URL de acceso -->
<!-- - Próxima fecha de renovación -->
```

---

#### E6-009: Implementar envío automático tras crear instancia
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```python
# Código implementado:


```

---

#### E6-010: Implementar envío en cron de recordatorio
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```python
# Lógica en cron:
# - Buscar instancias que expiran en 7 días
# - Por cada una, enviar email de recordatorio
```

---

#### E6-011: Probar recepción de todos los emails
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Pruebas realizadas:
# ✓ Email de bienvenida recibido
# ✓ Email de recordatorio recibido
# ✓ Email de suspensión recibido
# ✓ Email de reactivación recibido

# Email de prueba: [email usado]
```

---

## 💳 ÉPICA 7: Integración de Pagos

**Objetivo:** QR funcionando (o pasarela de pago alternativa)  
**Sprint:** 10 (Semana 10)  
**Criterios de Aceptación:**
- ✅ Hago una compra con QR de prueba
- ✅ El pago se procesa
- ✅ Se crea la instancia automáticamente
- ✅ Recibo el email

### Tareas

#### E7-001: [SPIKE] Investigar integración de QR con Odoo
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Comandos/Notas:**
```bash
# Documentación revisada:
# - QR Checkout
# - Webhooks
# - Modo test vs producción
```

---

#### E7-002: Sistema de pago con QR
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 8 puntos
- **Historia de Usuario:** Como cliente, quiero pagar con QR de forma segura
- **Comandos/Notas:**
```bash
# Payment provider configurado: QR (o alternativa)
```

---

#### E7-003: Crear cuenta de QR (modo test)
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Comandos/Notas:**
```bash
# 
# Email de cuenta: 
```

---

#### E7-004: Instalar Payment Provider en Odoo
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Instalado: Payment Provider: Stripe
# O módulo: website_sale_stripe

# Verificado en: Apps > Stripe
```

---

#### E7-005: Configurar claves API de la entidad financiera o pasarela de pago (pendiente)
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```bash
# Configuración en: Website > Configuration > Payment Providers > Stripe

# Publishable Key: pk_test_...
# Secret Key: sk_test_...
# Estado: Test Mode
```

---

#### E7-006: Configurar Webhook de Pasarela de Pago (QR)
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Comandos/Notas:**
```bash
# 
#
# Eventos suscritos:
# - payment_intent.succeeded
# - payment_intent.payment_failed

# ...
```

---

#### E7-007: Probar pago de prueba
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# Tarjeta de prueba usada: 4242 4242 4242 4242
# Fecha: cualquiera futura
# CVV: cualquier 3 dígitos

# Resultado:
# ✓ Pago procesado
# ✓ Orden confirmada
```

---

#### E7-008: Verificar que webhook activa creación de instancia
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Comandos/Notas:**
```bash
# Flujo probado:
# 1. Hacer compra con tarjeta test
# 2. Esperar webhook
# 3. Verificar logs de Stripe
# 4. Verificar que instancia se creó

# Resultado:
# ✓ Webhook recibido
# ✓ Instancia creada automáticamente
# ✓ Email enviado
```

---

#### E7-009: Documentar proceso de configuración
- [ ] Completada
- **Prioridad:** Medium
- **Estimación:** 2 puntos
- **Comandos/Notas:**
```markdown
# Documentación creada en: docs/stripe-setup.md

# Incluye:
# - Paso a paso de configuración
# - Screenshots
# - Troubleshooting común
```

---

## 🚀 ÉPICA 8: Despliegue a Producción

**Objetivo:** Sistema funcionando en servidor real  
**Sprints:** 11, 12 (Semanas 11-12)  
**Criterios de Aceptación (Sprint 12):**
- ✅ Entro a www.tuempresa.com (sin HTTP, sin puerto)
- ✅ Veo el candado verde (HTTPS)
- ✅ Hago una compra real
- ✅ Mi instancia se crea
- ✅ Todo funciona end-to-end

### Tareas - Sprint 11: Infraestructura Cloud

#### E8-001: [SPIKE] Investigar proveedores VPS (Pendiente)
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Proveedores comparados:
# - DigitalOcean: $6/mes (1GB RAM)
# - Linode: $5/mes (1GB RAM)
# - Vultr: $6/mes (1GB RAM)
# - Hetzner: €4.5/mes (2GB RAM)

# Proveedor seleccionado:
# Razón:
```

---

#### E8-002: Contratar VPS (Pendiente)
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 1 punto
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Proveedor:
# Plan:
# IP pública asignada:
# Credenciales root guardadas en: [ubicación segura]
```

---

#### E8-003: Configurar Ubuntu en VPS (Pendiente)
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Conectar por SSH:
ssh root@[IP]

# Actualizar sistema:
sudo apt update && sudo apt upgrade -y

# Crear usuario no-root:
adduser odoo
usermod -aG sudo odoo
```

---

#### E8-004: Configurar firewall (UFW)
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Instalar UFW:
sudo apt install ufw

# Configurar reglas:
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Activar:
sudo ufw enable

# Verificar:
sudo ufw status
```

---

#### E8-005: Instalar Docker en VPS
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Instalar Docker:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose:
sudo apt install docker-compose -y

# Agregar usuario al grupo docker:
sudo usermod -aG docker odoo

# Verificar:
docker --version
docker-compose --version
```

---

#### E8-006: Transferir código con Git
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Clonar repositorio en VPS:
cd /home/odoo
git clone [URL_REPOSITORIO]
cd odoo-saas-project

# Configurar git:
git config --global user.name "[nombre]"
git config --global user.email "[email]"
```

---

#### E8-007: Levantar servicios en VPS
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 3 puntos
- **Sprint:** 11
- **Comandos/Notas:**
```bash
# Levantar con Docker Compose:
docker-compose up -d

# Verificar:
docker ps

# Ver logs:
docker logs odoo_maestro

# Acceder temporalmente por IP:
# http://[IP]:8069
```

---

### Tareas - Sprint 12: Producción Final

#### E8-008: Comprar dominio
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 1 punto
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Proveedor: Namecheap / GoDaddy / Google Domains
# Dominio comprado: www.[nombre].com
# Costo anual: $
```

---

#### E8-009: Configurar DNS
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Registros DNS configurados:

# Registro A:
# Nombre: @
# Tipo: A
# Valor: [IP_VPS]
# TTL: 3600

# Registro A (www):
# Nombre: www
# Tipo: A
# Valor: [IP_VPS]
# TTL: 3600

# Verificar propagación:
# https://www.whatsmydns.net/
```

---

#### E8-010: Instalar Nginx
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Instalar Nginx:
sudo apt install nginx -y

# Verificar:
sudo systemctl status nginx
```

---

#### E8-011: Configurar Nginx como reverse proxy
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 5 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```nginx
# Archivo creado: /etc/nginx/sites-available/odoo-saas

# Contenido:
server {
    listen 80;
    server_name [dominio].com www.[dominio].com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Habilitar sitio:
sudo ln -s /etc/nginx/sites-available/odoo-saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

#### E8-012: Instalar certificado SSL (Let's Encrypt)
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 3 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Instalar Certbot:
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado:
sudo certbot --nginx -d [dominio].com -d www.[dominio].com

# Email para notificaciones: [email]

# Verificar renovación automática:
sudo certbot renew --dry-run
```

---

#### E8-013: Configurar Pasarela de pago (QR) en modo producción
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 2 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Cambiar en Odoo:
# Payment Provider > QR > State: Enabled (Production)

```

---

#### E8-014: Configurar email SMTP producción
- [ ] Completada
- **Prioridad:** High
- **Estimación:** 2 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Cambiar a servicio profesional:
# Opción 1: SendGrid
# Opción 2: Mailgun
# Opción 3: Amazon SES

# Servicio seleccionado:
# Configuración SMTP:
# Server:
# Port:
# Username:
# Password:
```

---

#### E8-015: Pruebas end-to-end en producción
- [ ] Completada
- **Prioridad:** Critical
- **Estimación:** 5 puntos
- **Sprint:** 12
- **Comandos/Notas:**
```bash
# Checklist de pruebas:

# ✓ Acceso a https://[dominio].com (candado verde)
# ✓ Navegación por el sitio web
# ✓ Registro de usuario nuevo
# ✓ Login exitoso
# ✓ Agregar plan al carrito
# ✓ Proceso de pago (tarjeta real)
# ✓ Confirmación de orden
# ✓ Creación de instancia (esperar ~30 seg)
# ✓ Recepción de email con credenciales
# ✓ Acceso a instancia del cliente
# ✓ Datos en la instancia
# ✓ Portal del cliente funcionando
# ✓ Suspensión automática (probar manualmente)
# ✓ Reactivación al pagar
```

---

## 📈 Seguimiento y Métricas

### KPIs Técnicos
- [ ] Tiempo de provisión: < 30 segundos
- [ ] Uptime: > 99.5%
- [ ] Tasa de error en creación: < 1%
- [ ] Tiempo de respuesta web: < 2 segundos

### KPIs de Negocio
- [ ] Conversión visita → compra: > 2%
- [ ] Tasa de renovación: > 80%
- [ ] Churn mensual: < 5%
- [ ] MRR (Monthly Recurring Revenue): Creciente

### Monitoreo Configurado
- [ ] UptimeRobot configurado para monitorear disponibilidad
- [ ] Logs centralizados configurados
- [ ] Alertas por email configuradas
- [ ] Script de backup diario configurado

---

## 🛡️ Gestión de Riesgos

### Riesgos Identificados y Mitigados

#### Riesgo: Contenedores no se crean correctamente
- **Probabilidad:** Alta
- **Impacto:** Crítico
- **Mitigación implementada:**
  - [ ] Logs detallados
  - [ ] Retry automático
  - [ ] Notificación al admin

#### Riesgo: Conflicto de puertos
- **Probabilidad:** Media
- **Impacto:** Alto
- **Mitigación implementada:**
  - [ ] Algoritmo de asignación robusto
  - [ ] Validación antes de crear

#### Riesgo: Servidor se queda sin recursos
- **Probabilidad:** Alta
- **Impacto:** Crítico
- **Mitigación implementada:**
  - [ ] Límites por contenedor
  - [ ] Monitoreo de RAM/CPU
  - [ ] Plan de escalamiento

---

## 📝 Notas de Implementación

### Comandos Docker Útiles

```bash
# Ver todos los contenedores (incluidos detenidos):
docker ps -a

# Ver logs de un contenedor:
docker logs [nombre_contenedor]

# Ejecutar comando dentro de un contenedor:
docker exec -it [nombre_contenedor] bash

# Eliminar contenedor:
docker rm [nombre_contenedor]

# Eliminar contenedor forzado:
docker rm -f [nombre_contenedor]

# Ver uso de recursos:
docker stats

# Limpiar contenedores detenidos:
docker container prune
```

### Comandos Git Útiles

```bash
# Ver estado:
git status

# Agregar cambios:
git add .

# Commit con mensaje descriptivo:
git commit -m "feat: [descripción] #E3-014"

# Push a repositorio:
git push origin main

# Pull cambios:
git pull origin main

# Ver branches:
git branch

# Crear branch:
git checkout -b feature/nombre-feature
```

### Comandos Odoo Útiles

```bash
# Reiniciar Odoo:
docker restart odoo_maestro

# Ver logs en tiempo real:
docker logs -f odoo_maestro

# Actualizar módulo:
docker exec -it odoo_maestro odoo -u saas_docker_manager -d odoo_maestro

# Modo debug:
# Agregar ?debug=1 a la URL
```

---

## 🎓 Recursos de Aprendizaje

### Docker
- [ ] Tutorial oficial: https://docs.docker.com/get-started/
- [ ] Docker Compose: https://docs.docker.com/compose/

### Odoo Development
- [ ] Documentación oficial: https://www.odoo.com/documentation/17.0/
- [ ] ORM Guide: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html

### Python subprocess
- [ ] Documentación: https://docs.python.org/3/library/subprocess.html

### Nginx
- [ ] Configuración de reverse proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/

---

## 🔗 Enlaces Importantes

- **Repositorio:** [URL del repositorio en GitHub]
- **Servidor de Desarrollo:** http://[IP_UBUNTU]:8069
- **Servidor de Producción:** https://[dominio].com
- **UptimeRobot:** https://uptimerobot.com

---

## 👥 Equipo

- **Developer 1:** [Adolfo Mendoza Ribera] 
- **Developer 2:** [Marco Lehonti Guzman Montalvan] 

---

## 📅 Retrospectivas

### Sprint 1
- **Fecha:**
- **Lo que funcionó bien:**
- **Lo que mejorar:**
- **Acciones:**

### Sprint 2
- **Fecha:**
- **Lo que funcionó bien:**
- **Lo que mejorar:**
- **Acciones:**

---

## ✅ Definition of Done

Para considerar una tarea completada, debe cumplir:
- [ ] Código escrito y probado
- [ ] Documentación actualizada (en este ROADMAP)
- [ ] Sin errores críticos
- [ ] Merge a rama main (o develop)
- [ ] Demo funcional realizada

---

**Última actualización:** [Fecha]  
**Versión del ROADMAP:** 1.0
