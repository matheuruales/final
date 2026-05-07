from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from .constants import DOCENTE_GROUP, ESTUDIANTE_GROUP


class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_groups = ()

    def test_func(self):
        user = self.request.user
        if DOCENTE_GROUP in self.allowed_groups and (user.is_staff or user.is_superuser):
            return True
        return user.groups.filter(name__in=self.allowed_groups).exists()

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('dashboard')


class StudentRequiredMixin(GroupRequiredMixin):
    allowed_groups = (ESTUDIANTE_GROUP,)


class TeacherRequiredMixin(GroupRequiredMixin):
    allowed_groups = (DOCENTE_GROUP,)
