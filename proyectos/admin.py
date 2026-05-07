from django.contrib import admin

from .models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'estudiante',
        'estado',
        'fecha_envio',
        'fecha_revision',
        'calificacion',
    )
    list_filter = ('estado', 'fecha_envio', 'fecha_revision')
    search_fields = ('titulo', 'descripcion', 'estudiante__username', 'estudiante__email')
