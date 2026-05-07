from django.urls import path

from .views import (
    ComentarioCreateView,
    ProyectoCreateView,
    ProyectoDeleteView,
    ProyectoDetailView,
    ProyectoListView,
    ProyectoRevisionView,
    ProyectoUpdateView,
)

urlpatterns = [
    path('', ProyectoListView.as_view(), name='proyecto_lista'),
    path('crear/', ProyectoCreateView.as_view(), name='proyecto_crear'),
    path('<int:pk>/', ProyectoDetailView.as_view(), name='proyecto_detalle'),
    path('<int:pk>/editar/', ProyectoUpdateView.as_view(), name='proyecto_editar'),
    path('<int:pk>/eliminar/', ProyectoDeleteView.as_view(), name='proyecto_eliminar'),
    path('<int:pk>/revision/', ProyectoRevisionView.as_view(), name='proyecto_revision'),
    path('<int:pk>/comentarios/', ComentarioCreateView.as_view(), name='proyecto_comentar'),
]
