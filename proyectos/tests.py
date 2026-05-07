from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Proyecto


class ProyectoModelTests(TestCase):
    def test_proyecto_can_be_created(self):
        estudiante = User.objects.create_user(username='autor', password='ClaveSegura123')
        documento = SimpleUploadedFile('propuesta.pdf', b'archivo de prueba')

        proyecto = Proyecto.objects.create(
            titulo='Sistema de gestion',
            descripcion='Descripcion del proyecto',
            estudiante=estudiante,
            documento=documento,
        )

        self.assertEqual(proyecto.estado, Proyecto.Estado.PENDIENTE)
        self.assertEqual(proyecto.estudiante, estudiante)

# Create your tests here.
