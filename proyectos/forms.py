from crispy_forms.helper import FormHelper
from django import forms

from .models import Comentario, Proyecto


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ('titulo', 'descripcion', 'documento')
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['documento'].help_text = 'Formatos permitidos: PDF, DOC, DOCX. Tamano maximo: 5 MB.'
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


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('texto',)
        widgets = {
            'texto': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Escribe un comentario para el seguimiento del proyecto.',
                }
            ),
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        self.proyecto = proyecto
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean(self):
        cleaned_data = super().clean()
        if self.proyecto and self.proyecto.comentarios_bloqueados:
            raise forms.ValidationError(
                'No se pueden registrar comentarios cuando el proyecto esta aprobado.'
            )
        return cleaned_data
