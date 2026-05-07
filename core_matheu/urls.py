from django.contrib.auth.views import LogoutView
from django.urls import path

from .forms import CustomAuthenticationForm
from .views import DashboardView, UserLoginView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path(
        'login/',
        UserLoginView.as_view(authentication_form=CustomAuthenticationForm),
        name='login',
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
]
