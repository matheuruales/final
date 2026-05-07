from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contrasena'
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': 'Ingresa tu usuario',
                'autofocus': True,
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'placeholder': 'Ingresa tu contrasena',
            }
        )
