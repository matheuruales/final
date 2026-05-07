from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.constants import DOCENTE_GROUP, ESTUDIANTE_GROUP
from core.mixins import StudentRequiredMixin, TeacherRequiredMixin

from .forms import ProyectoForm, ProyectoRevisionForm
from .models import Proyecto


class ProyectoRoleMixin(LoginRequiredMixin):
    def get_group_names(self):
        if not hasattr(self, '_group_names'):
            self._group_names = set(
                self.request.user.groups.values_list('name', flat=True)
            )
        return self._group_names

    def is_estudiante(self):
        return ESTUDIANTE_GROUP in self.get_group_names()

    def is_docente(self):
        return DOCENTE_GROUP in self.get_group_names()

    def has_project_role(self):
        return self.is_estudiante() or self.is_docente()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not self.has_project_role():
            messages.error(
                request,
                'Debes pertenecer al grupo Estudiante o Docente para gestionar proyectos.',
            )
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_project_queryset(self):
        queryset = Proyecto.objects.select_related('estudiante')
        if self.is_docente():
            return queryset
        if self.is_estudiante():
            return queryset.filter(estudiante=self.request.user)
        return queryset.none()

    def build_detail_context(self, proyecto):
        return {
            'can_edit': self.is_estudiante() and proyecto.estudiante_id == self.request.user.id,
            'can_review': self.is_docente(),
        }


class ProyectoListView(ProyectoRoleMixin, ListView):
    model = Proyecto
    template_name = 'proyectos/proyecto_list.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        return self.get_project_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_estudiante'] = self.is_estudiante()
        context['is_docente'] = self.is_docente()
        return context


class ProyectoDetailView(ProyectoRoleMixin, DetailView):
    model = Proyecto
    template_name = 'proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        return self.get_project_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.build_detail_context(self.object))
        return context


class ProyectoCreateView(StudentRequiredMixin, CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'

    def form_valid(self, form):
        form.instance.estudiante = self.request.user
        messages.success(self.request, 'El proyecto fue creado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('proyecto_detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear proyecto'
        context['submit_label'] = 'Guardar proyecto'
        return context


class ProyectoOwnerMixin(StudentRequiredMixin):
    model = Proyecto

    def get_queryset(self):
        return Proyecto.objects.filter(estudiante=self.request.user)


class ProyectoUpdateView(ProyectoOwnerMixin, UpdateView):
    form_class = ProyectoForm
    template_name = 'proyectos/proyecto_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'El proyecto fue actualizado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('proyecto_detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Editar proyecto'
        context['submit_label'] = 'Actualizar proyecto'
        return context


class ProyectoDeleteView(ProyectoOwnerMixin, DeleteView):
    template_name = 'proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_lista')

    def form_valid(self, form):
        messages.success(self.request, 'El proyecto fue eliminado correctamente.')
        return super().form_valid(form)


class ProyectoRevisionView(TeacherRequiredMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoRevisionForm
    template_name = 'proyectos/proyecto_revision_form.html'
    context_object_name = 'proyecto'

    def form_valid(self, form):
        form.instance.fecha_revision = timezone.now()
        messages.success(self.request, 'La revision del proyecto fue actualizada.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('proyecto_detalle', kwargs={'pk': self.object.pk})
