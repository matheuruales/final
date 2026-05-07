from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from core.constants import DOCENTE_GROUP, ESTUDIANTE_GROUP
from core.mixins import StudentRequiredMixin, TeacherRequiredMixin

from .forms import ComentarioForm, ProyectoForm, ProyectoRevisionForm
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
        queryset = Proyecto.objects.select_related('estudiante').prefetch_related(
            'comentarios__usuario'
        )
        if self.is_docente():
            return queryset
        if self.is_estudiante():
            return queryset.filter(estudiante=self.request.user)
        return queryset.none()

    def can_comment_project(self, proyecto):
        if proyecto.comentarios_bloqueados:
            return False
        if self.is_docente():
            return True
        return self.is_estudiante() and proyecto.estudiante_id == self.request.user.id

    def build_detail_context(self, proyecto, comentario_form=None):
        return {
            'comentario_form': comentario_form
            if comentario_form is not None
            else ComentarioForm(proyecto=proyecto),
            'can_comment': self.can_comment_project(proyecto),
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
        context.update(
            self.build_detail_context(
                self.object,
                comentario_form=kwargs.get('comentario_form'),
            )
        )
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


class ComentarioCreateView(ProyectoRoleMixin, SingleObjectMixin, FormView):
    model = Proyecto
    form_class = ComentarioForm
    template_name = 'proyectos/proyecto_detail.html'

    def get_queryset(self):
        return self.get_project_queryset()

    def get(self, request, *args, **kwargs):
        return redirect('proyecto_detalle', pk=kwargs['pk'])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.can_comment_project(self.object):
            messages.error(
                request,
                'No se pueden agregar comentarios a un proyecto aprobado.',
            )
            return redirect('proyecto_detalle', pk=self.object.pk)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['proyecto'] = self.object
        return kwargs

    def form_valid(self, form):
        comentario = form.save(commit=False)
        comentario.usuario = self.request.user
        comentario.proyecto = self.object
        comentario.save()

        notification_sent = self.send_comment_notification(comentario)
        if notification_sent:
            messages.success(
                self.request,
                'Comentario registrado y notificacion enviada al estudiante.',
            )
        else:
            messages.warning(
                self.request,
                'Comentario registrado, pero el estudiante no tiene un correo configurado.',
            )
        return redirect('proyecto_detalle', pk=self.object.pk)

    def form_invalid(self, form):
        context = self.get_context_data(form=form, object=self.object)
        context.update(self.build_detail_context(self.object, comentario_form=form))
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = self.object
        context.update(
            self.build_detail_context(
                self.object,
                comentario_form=kwargs.get('form'),
            )
        )
        return context

    def send_comment_notification(self, comentario):
        email = comentario.proyecto.estudiante.email
        if not email:
            return False

        send_mail(
            subject=f'Nuevo comentario en tu proyecto: {comentario.proyecto.titulo}',
            message=(
                f'Se registro un nuevo comentario en tu proyecto "{comentario.proyecto.titulo}".\n\n'
                f'Usuario: {comentario.usuario.get_full_name() or comentario.usuario.username}\n'
                f'Fecha: {timezone.localtime(comentario.fecha).strftime("%d/%m/%Y %H:%M")}\n\n'
                f'Comentario:\n{comentario.texto}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return True
