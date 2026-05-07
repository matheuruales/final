from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from pathlib import Path


ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024


def validate_project_document(value):
    extension = Path(value.name).suffix.lower()
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            'Solo se permiten archivos PDF, DOC o DOCX.'
        )

    if value.size > MAX_DOCUMENT_SIZE:
        raise ValidationError('El archivo no puede superar los 5 MB.')


class Proyecto(models.Model):
    class Estado(models.TextChoices):
        ENVIADO = 'enviado', 'Enviado'
        REVISION = 'revision', 'En Revisión'
        APROBADO = 'aprobado', 'Aprobado'

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proyectos',
    )
    documento = models.FileField(
        upload_to='proyectos/documentos/',
        validators=[validate_project_document],
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ENVIADO,
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(blank=True, null=True)
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return f'{self.titulo} - {self.estudiante}'

    @property
    def comentarios_bloqueados(self):
        return self.estado == self.Estado.APROBADO


class Comentario(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_proyecto',
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='comentarios',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()

    class Meta:
        ordering = ['fecha']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f'Comentario de {self.usuario} en {self.proyecto}'
