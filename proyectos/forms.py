from crispy_forms.helper import FormHelper
from django import forms

from .models import Proyecto


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ('titulo', 'descripcion', 'documento')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documento'].help_text = 'Adjunta el documento principal del proyecto.'
        self.helper = FormHelper()
        self.helper.form_tag = False


class ProyectoRevisionForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ('estado', 'calificacion')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
