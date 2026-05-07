from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .constants import DOCENTE_GROUP, ESTUDIANTE_GROUP


def group_required(*group_names):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)

            messages.error(request, 'No tienes permisos para acceder a esta seccion.')
            return redirect('dashboard')

        return _wrapped_view

    return decorator


def student_required(view_func):
    return group_required(ESTUDIANTE_GROUP)(view_func)


def teacher_required(view_func):
    return group_required(DOCENTE_GROUP)(view_func)
