from django import forms
from .models import Incidencia, Comentario


class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['titulo', 'descripcion', 'equipo', 'prioridad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }


class IncidenciaEstadoForm(forms.Form):
    estado = forms.ChoiceField(
        choices=Incidencia.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Nuevo Estado',
    )


class IncidenciaPublicaForm(forms.ModelForm):
    titulo = forms.CharField(label='¿Qué falla ocurre?', max_length=200,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: El proyector no enciende'}))

    class Meta:
        model = Incidencia
        fields = ['nombre_reportero', 'area', 'contacto', 'equipo', 'titulo', 'descripcion']
        labels = {
            'nombre_reportero': 'Su nombre',
            'area': 'Salón / Área',
            'contacto': 'Email o teléfono (opcional)',
            'equipo': 'Equipo relacionado (si lo conoce)',
            'descripcion': 'Detalle de la falla',
        }
        widgets = {
            'nombre_reportero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Prof. María Pérez'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Salón 204 o Biblioteca'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'correo@liceo.edu.ve'}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                 'placeholder': '¿Qué pasó? ¿Qué intentó hacer?'}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escriba su comentario...'}),
        }
        labels = {
            'texto': 'Comentario',
        }
