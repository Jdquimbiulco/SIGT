# SIGT - Sistema Integrado de Gestión Tecnológica

Aplicación web para el Departamento de TI del **Liceo Campo Verde**.
Proyecto de pasantías preprofesionales de Ingeniería de Software.

## Stack Tecnológico

- **Backend:** Django 6.1 (Python 3.12)
- **Base de datos:** PostgreSQL (SQLite en desarrollo por defecto)
- **Frontend:** Django Templates + Bootstrap 5 (CDN)
- **Gráficos:** Chart.js (CDN)
- **Autenticación:** Usuarios, grupos y permisos nativos de Django
- **Historial:** django-simple-history (Equipos) + modelo `HistorialCambio`

## Módulos

| Módulo | App | Descripción |
|---|---|---|
| Inventario | `inventario` | Equipos, ubicaciones e historial de cambios |
| Mesa de Ayuda | `mesa_ayuda` | Incidencias con prioridad, estado y comentarios |
| Mantenimiento | `mantenimiento` | Preventivo/correctivo con alertas de vencimiento |
| Reportes | `reportes` | 6 gráficos vía API JSON + Chart.js |
| Usuarios | `usuarios` | Roles (Administrador, Técnico) con permisos |

## Mesa de ayuda abierta a la comunidad

Los profesores y personal del liceo **no necesitan cuenta** para reportar fallas:

- **Formulario público** en `/reportar/` (enlazado desde `/usuarios/login/`).
- Al enviarlo se crea una incidencia en estado `abierta` con prioridad `media` y los
  datos del reportero (`nombre_reportero`, `area`, `contacto`), sin `creado_por`.
- El reportero recibe el número de ticket (`/reportar/ok/<pk>/`) para hacer seguimiento.
- La incidencia aparece en Mesa de Ayuda, dashboard y reportes como cualquier otra.

## Configuración inicial

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate      # Linux/macOS

# 2. Instalar dependencias
pip install django django-simple-history psycopg2-binary

# 3. Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser
python manage.py configurar_roles

# 4. Ejecutar el servidor
python manage.py runserver
```

Acceso: http://127.0.0.1:8000 — usuario admin creado por defecto
(`admin` / `admin123`). El panel `/admin/` de Django existe para gestión
interna del sistema, pero la interfaz principal es de uso diario.

### Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador (acceso total, incluye usuarios) |
| `tecnico1` | `tecnico123` | Técnico (todo excepto gestión de usuarios) |

## PostgreSQL (producción)

1. Instalar `psycopg2-binary`.
2. Definir las variables `SIGT_DB_NAME`, `SIGT_DB_USER`, `SIGT_DB_PASSWORD`,
   `SIGT_DB_HOST`, `SIGT_DB_PORT`.
3. Cambiar el `ENGINE` en `sigt/settings.py` (ver bloque comentado).

## Roles y permisos

- **Administrador:** acceso total a todos los módulos, incluida la gestión de usuarios.
- **Técnico:** acceso completo a Inventario, Mesa de Ayuda, Mantenimiento y Reportes.
  No puede gestionar usuarios (ver/crear/editar/eliminar).

Los permisos se asignan automáticamente según el rol al crear/editar un usuario,
y el comando `configurar_roles` sincroniza los grupos.