# Sistema de Seguimiento de Proyectos Académicos (Django)

Aplicación Django para registrar proyectos académicos, gestionarlos por estados, permitir comentarios entre docentes/estudiantes y exportar listados.

## Requisitos

- Python 3.11+ (recomendado)
- Pip

## Instalación

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

## Ejecutar

```bash
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/`.

## Roles (Estudiante / Docente)

Los grupos `Estudiante` y `Docente` se crean automáticamente al ejecutar `migrate` (signal `post_migrate`).

Asigna el grupo desde el panel admin:

- Admin: `http://127.0.0.1:8000/admin/`
- Usuarios → selecciona usuario → “Grupos” → agrega `Estudiante` o `Docente`

## Funcionalidades principales

- Login/Logout con protección de rutas.
- Estudiante:
  - Crea/edita/elimina sus propios proyectos.
- Docente:
  - Revisa proyectos, cambia estado y asigna calificación.
- Comentarios:
  - Se bloquean nuevos comentarios cuando el estado es **Aprobado**.
  - Al crear comentario, se notifica por correo al estudiante.
- Listado:
  - Filtro por estado.
  - Filtro por estudiante (solo docente).
  - Búsqueda por texto (título/descripcion y, para docente, también estudiante).
- Exportación:
  - CSV y PDF del listado (respeta los filtros actuales).

## Exportación (CSV/PDF)

En el listado de proyectos (`/proyectos/`) se muestran los botones:

- “Exportar CSV”
- “Exportar PDF”

Ambos usan los filtros actuales por querystring.

## Emails (modo desarrollo)

Por defecto el proyecto usa:

- `EMAIL_BACKEND = django.core.mail.backends.console.EmailBackend`

Esto imprime el contenido del correo en la consola al guardar un comentario.

Para usar SMTP real, cambia `EMAIL_BACKEND` y configura credenciales en `proyectos_academicos/settings.py`.

## Usuarios de prueba (ejemplo)

1) Crea dos usuarios desde admin (o con `createsuperuser` + admin):

- `estudiante1` (con email configurado) → grupo `Estudiante`
- `docente1` → grupo `Docente`

2) Ingresa con cada rol y valida:

- Estudiante crea un proyecto y lo ve en su listado.
- Docente filtra por estudiante/estado, revisa y califica.
- Exporta el listado a CSV/PDF.

