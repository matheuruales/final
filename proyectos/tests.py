from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core.constants import DOCENTE_GROUP, ESTUDIANTE_GROUP

from .models import Comentario, Proyecto


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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ProyectoViewsTests(TestCase):
    def setUp(self):
        self.student_group, _ = Group.objects.get_or_create(name=ESTUDIANTE_GROUP)
        self.teacher_group, _ = Group.objects.get_or_create(name=DOCENTE_GROUP)

        self.student = User.objects.create_user(
            username='estudiante1',
            password='ClaveSegura123',
            email='estudiante1@example.com',
        )
        self.student.groups.add(self.student_group)

        self.other_student = User.objects.create_user(
            username='estudiante2',
            password='ClaveSegura123',
            email='estudiante2@example.com',
        )
        self.other_student.groups.add(self.student_group)

        self.teacher = User.objects.create_user(
            username='docente1',
            password='ClaveSegura123',
            email='docente1@example.com',
        )
        self.teacher.groups.add(self.teacher_group)

        self.project = Proyecto.objects.create(
            titulo='Proyecto de grado',
            descripcion='Descripcion inicial del proyecto',
            estudiante=self.student,
            documento=self.make_file('propuesta.pdf'),
        )

    def make_file(self, name='archivo.pdf', content=b'contenido'):
        return SimpleUploadedFile(name, content)

    def test_student_can_create_project(self):
        self.client.login(username='estudiante1', password='ClaveSegura123')

        response = self.client.post(
            reverse('proyecto_crear'),
            {
                'titulo': 'Nuevo proyecto',
                'descripcion': 'Contenido del proyecto',
                'documento': self.make_file('entrega.docx'),
            },
        )

        new_project = Proyecto.objects.exclude(pk=self.project.pk).get()
        self.assertRedirects(
            response,
            reverse('proyecto_detalle', kwargs={'pk': new_project.pk}),
        )
        self.assertEqual(new_project.estudiante, self.student)

    def test_project_list_requires_login(self):
        response = self.client.get(reverse('proyecto_lista'))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('proyecto_lista')}")

    def test_student_cannot_edit_other_students_project(self):
        self.client.login(username='estudiante2', password='ClaveSegura123')

        response = self.client.get(
            reverse('proyecto_editar', kwargs={'pk': self.project.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_teacher_can_update_revision(self):
        self.client.login(username='docente1', password='ClaveSegura123')

        response = self.client.post(
            reverse('proyecto_revision', kwargs={'pk': self.project.pk}),
            {
                'estado': Proyecto.Estado.APROBADO,
                'calificacion': '4.50',
            },
        )

        self.assertRedirects(
            response,
            reverse('proyecto_detalle', kwargs={'pk': self.project.pk}),
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.estado, Proyecto.Estado.APROBADO)
        self.assertEqual(str(self.project.calificacion), '4.50')
        self.assertIsNotNone(self.project.fecha_revision)

    def test_approved_project_blocks_new_comments(self):
        self.project.estado = Proyecto.Estado.APROBADO
        self.project.save(update_fields=['estado'])
        self.client.login(username='docente1', password='ClaveSegura123')

        response = self.client.post(
            reverse('proyecto_comentar', kwargs={'pk': self.project.pk}),
            {'texto': 'Comentario bloqueado'},
        )

        self.assertRedirects(
            response,
            reverse('proyecto_detalle', kwargs={'pk': self.project.pk}),
        )
        self.assertEqual(Comentario.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_comment_sends_email_to_student(self):
        self.client.login(username='docente1', password='ClaveSegura123')

        response = self.client.post(
            reverse('proyecto_comentar', kwargs={'pk': self.project.pk}),
            {'texto': 'Recuerda complementar el marco teorico.'},
        )

        self.assertRedirects(
            response,
            reverse('proyecto_detalle', kwargs={'pk': self.project.pk}),
        )
        self.assertEqual(Comentario.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['estudiante1@example.com'])

    def test_invalid_file_extension_is_rejected(self):
        self.client.login(username='estudiante1', password='ClaveSegura123')

        response = self.client.post(
            reverse('proyecto_crear'),
            {
                'titulo': 'Proyecto invalido',
                'descripcion': 'Tiene un archivo no permitido',
                'documento': self.make_file('script.exe'),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'documento',
            'Solo se permiten archivos PDF, DOC o DOCX.',
        )
