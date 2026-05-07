from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.text import get_valid_filename


class DatabaseStorage(Storage):
    def _model(self):
        return apps.get_model('proyectos_matheu', 'DocumentoArchivo')

    def _normalize_name(self, name):
        parts = [get_valid_filename(part) for part in name.split('/') if part]
        return '/'.join(parts)

    def _open(self, name, mode='rb'):
        archivo = self._model().objects.get(name=name)
        return ContentFile(bytes(archivo.content), name=name)

    def _save(self, name, content):
        name = self._normalize_name(name)
        data = b''.join(chunk for chunk in content.chunks())
        content_type = getattr(content, 'content_type', '') or ''
        self._model().objects.update_or_create(
            name=name,
            defaults={
                'content': data,
                'content_type': content_type,
            },
        )
        return name

    def exists(self, name):
        return self._model().objects.filter(name=name).exists()

    def delete(self, name):
        self._model().objects.filter(name=name).delete()

    def size(self, name):
        archivo = self._model().objects.only('content').get(name=name)
        return len(archivo.content)

    def url(self, name):
        return f'/media/{name}'
