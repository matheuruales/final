from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .constants import DOCENTE_GROUP, ESTUDIANTE_GROUP


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='estudiante1',
            password='ClaveSegura123',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_user_can_login_and_access_dashboard(self):
        logged_in = self.client.login(username='estudiante1', password='ClaveSegura123')
        self.assertTrue(logged_in)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenido')


class RoleBootstrapTests(TestCase):
    def test_expected_groups_exist_after_migrate(self):
        self.assertTrue(Group.objects.filter(name=ESTUDIANTE_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=DOCENTE_GROUP).exists())

# Create your tests here.
