# microsaas_db_restore

Módulo complementario de `micro_saas` para copiar una BD plantilla (ZIP del Database Manager de Odoo) a una instancia Docker recién creada.

---

## Estructura

```
microsaas_db_restore/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── odoo_docker_instance_restore.py   # Herencia: campos + do_restore_db()
├── wizard/
│   ├── __init__.py
│   ├── wizard_restore_db.py              # Wizard de confirmación
│   └── wizard_restore_db_views.xml
├── views/
│   └── odoo_docker_instance_restore_views.xml  # Tab + botón en la instancia
├── security/
│   └── ir.model.access.csv
└── static/
    └── db_backups/        ← ⭐ AQUÍ copias tus ZIPs plantilla
```

---

## Flujo completo

```
1. Copia el ZIP a:
   microsaas_db_restore/static/db_backups/mi_plantilla.zip

2. En la instancia Docker:
   - Selecciona "ZIP Plantilla" → mi_plantilla.zip
   - Escribe "Nombre de la BD" → nombre_cliente
   - Escribe "Master Password Instancia" → admin (o la tuya)

3. Start Instance  →  estado Running

4. Clic en "🗄️ Restaurar BD Plantilla"
   │
   └── Abre wizard de confirmación
       └── Clic en "✅ Sí, Restaurar Ahora"
           │
           └── POST multipart a:
               http://<instancia_url>/web/database/restore
               ├── master_pwd = <master_password>
               ├── name      = <nombre_cliente>
               ├── backup_file = mi_plantilla.zip (stream)
               └── copy      = false

5. Odoo de la instancia procesa el ZIP internamente
   (descomprime, crea la BD, restaura filestore)

6. Estado → "Restaurada ✓"

7. Abre la URL de la instancia → Odoo ya configurado ✅
```

---

## Notas importantes

- El ZIP debe ser generado con el botón **Backup** del `/web/database/manager` de Odoo. Contiene internamente `dump.sql` + carpeta `filestore/`.
- El campo **Master Password Instancia** es el `admin_passwd` del `odoo.conf` de **la instancia nueva**, no del servidor principal.
- La restauración puede tardar varios minutos para ZIPs grandes (timeout configurado en 10 min).
- Si la instancia está en GitHub Codespaces, la URL se construye automáticamente con el formato `https://<codespace>-<port>.app.github.dev`.
- El botón desaparece del header una vez que la restauración fue exitosa (`db_restore_state == 'done'`).
