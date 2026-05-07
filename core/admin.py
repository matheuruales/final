from django.contrib import admin
from django.contrib.auth.models import Group


admin.site.site_header = 'Administracion de Proyectos Academicos'
admin.site.site_title = 'Proyectos Academicos'
admin.site.index_title = 'Panel administrativo'

Group._meta.verbose_name = 'Grupo'
Group._meta.verbose_name_plural = 'Grupos'
