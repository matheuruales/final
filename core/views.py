from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        group_names = set(user.groups.values_list('name', flat=True))
        context['is_estudiante'] = 'Estudiante' in group_names
        context['is_docente'] = 'Docente' in group_names
        return context
