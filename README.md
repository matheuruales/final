# Sistema de Seguimiento de Proyectos Academicos - Matheu

Proyecto Django del parcial final de electiva. El paquete principal se llama
`seguimiento_proyectos_academicos_matheu` y las aplicaciones son `core_matheu`
y `proyectos_matheu`.

## Requisitos

- Python 3.11+
- Pip
- Base Supabase/Postgres configurada en `.env`

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

En Windows PowerShell usa:

```powershell
.venv\Scripts\Activate.ps1
```

## Ejecutar

```bash
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Base de datos Supabase

El proyecto lee `.env` automaticamente. Para Supabase se usa `DATABASE_URL`
con Session Pooler IPv4:

```env
DATABASE_URL=postgresql://postgres.iovdysmtsekdcnjtqzpb:...@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
```

No uses el host directo `db.iovdysmtsekdcnjtqzpb.supabase.co` en redes IPv4,
porque ese endpoint solo publica IPv6 para este proyecto.

Para aplicar migraciones en Supabase:

```bash
python manage.py migrate --noinput
python manage.py showmigrations
```

## Roles

Los grupos `Estudiante` y `Docente` se crean automaticamente con las migraciones.
Asigna usuarios a grupos desde el admin:

- Admin: `http://127.0.0.1:8000/admin/`
- Usuarios -> selecciona usuario -> Grupos -> agrega `Estudiante` o `Docente`

Los usuarios `is_staff` o `is_superuser` tambien pueden actuar como
Docente/Administrador para revisar, calificar, comentar, filtrar y exportar.

## Funcionalidades

- Login y logout.
- Estudiante: crea, actualiza y elimina solo sus propios proyectos.
- Docente/Administrador: revisa proyectos, cambia estado y asigna calificacion.
- Estados del proyecto: `enviado`, `revision`, `aprobado`.
- Comentarios: registran usuario, fecha y texto.
- Al crear un comentario se envia una notificacion por correo al estudiante.
- Cuando el estado es `aprobado`, se bloquea la adicion de nuevos comentarios.
- Filtros por estado, estudiante y busqueda de texto.
- Exportacion de listados a CSV y PDF respetando los filtros activos.

## Correo

En desarrollo se usa consola por defecto:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Para enviar correos reales configura variables de entorno:

```bash
export EMAIL_HOST=smtp.example.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=true
export EMAIL_HOST_USER=usuario@example.com
export EMAIL_HOST_PASSWORD=clave
export DEFAULT_FROM_EMAIL=no-reply@example.com
```

Si `EMAIL_HOST` esta presente, Django usa SMTP automaticamente.

## Flujo de prueba manual

1. Crea un usuario `estudiante1` con email y grupo `Estudiante`.
2. Crea un usuario `docente1` con grupo `Docente`, o usa un usuario admin.
3. Ingresa como estudiante y crea un proyecto con documento PDF/DOC/DOCX.
4. Ingresa como docente/admin, filtra por estudiante o estado y revisa el proyecto.
5. Agrega un comentario y verifica la notificacion en consola o SMTP.
6. Cambia el estado a `aprobado` y confirma que ya no permite comentarios.
7. Exporta el listado en CSV y PDF.

## Verificacion

```bash
python manage.py check
python manage.py test
```
