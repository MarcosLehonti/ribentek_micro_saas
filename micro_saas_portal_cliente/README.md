# MicroSaaS - Portal Cliente

Módulo que extiende el **portal web de Odoo** para permitir que los clientes visualicen sus **suscripciones SaaS** y accedan a sus **instancias de Odoo** desde el portal.

Proporciona:

- Listado de suscripciones del cliente
- Vista de detalle de cada suscripción
- Acceso directo a la instancia SaaS
- Visualización de usuarios activos y facturas asociadas

---

# Dependencias

Este módulo depende de los siguientes módulos:

- `portal`
- `subscription_package`
- `subscription_mejora_cupones`

---

# Estructura del módulo

```
micro_saas_portal_cliente/
├── controllers/
│   ├── __init__.py
│   └── portal.py
├── security/
│   ├── ir.model.access.csv
│   └── subscription_portal_security.xml
├── views/
│   └── subscription_portal_templates.xml
├── __init__.py
├── __manifest__.py
└── README.md
```

---

# Controladores

### `controllers/portal.py`

Extiende el controlador `CustomerPortal` para agregar funcionalidades al portal del cliente.

Rutas implementadas:

| Ruta | Descripción |
|-----|-------------|
| `/my/subscriptions` | Listado de suscripciones del cliente |
| `/my/subscriptions/page/<page>` | Paginación del listado |
| `/my/subscriptions/<id>` | Vista de detalle de una suscripción |

También agrega un **contador de suscripciones** en la página principal del portal (`/my/home`).

---

# Seguridad

### `subscription_portal_security.xml`

Define reglas de seguridad para permitir que los clientes del portal accedan únicamente a sus propias suscripciones.

### `ir.model.access.csv`

Define permisos de acceso al modelo de suscripciones para usuarios del portal.

---

# Vistas

### `views/subscription_portal_templates.xml`

Contiene las plantillas **QWeb** utilizadas por el portal:

| Template | Descripción |
|--------|-------------|
| `portal_my_home_subscription` | Agrega el acceso a suscripciones en el dashboard del portal |
| `portal_my_subscriptions_list` | Tabla con listado de suscripciones |
| `portal_subscription_detail_view` | Vista de detalle de suscripción |
| `portal_my_home_menu_subscription` | Breadcrumbs del portal |

---

# Modelos utilizados

| Modelo | Descripción |
|------|-------------|
| `subscription.package` | Suscripción SaaS del cliente |
| `subscription.coupon` | Periodos de capacidad de usuarios |
| `account.move` | Facturas asociadas |

---

# Funcionalidades del portal

El cliente puede:

- Ver todas sus suscripciones
- Consultar el estado del servicio
- Ver el número de usuarios activos
- Revisar la factura asociada
- Acceder directamente a su instancia de Odoo

---

# Flujo básico

```
Cliente inicia sesión en el portal
        ↓
Accede a "Mis Suscripciones"
        ↓
Visualiza sus servicios activos
        ↓
Consulta el detalle de la suscripción
        ↓
Accede a su instancia Odoo
```