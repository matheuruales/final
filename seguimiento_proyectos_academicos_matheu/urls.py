from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from proyectos_matheu.views import MediaFileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core_matheu.urls')),
    path('proyectos/', include('proyectos_matheu.urls')),
    path('media/<path:path>', MediaFileView.as_view(), name='media_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
