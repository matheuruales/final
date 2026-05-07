from django.contrib import admin

from .models import Comentario, Proyecto


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


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'usuario', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('proyecto__titulo', 'usuario__username', 'texto')
