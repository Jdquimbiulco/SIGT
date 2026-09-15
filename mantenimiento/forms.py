from django import forms
from .models import Mantenimiento


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = ['equipo', 'tipo', 'fecha_programada', 'tecnico', 'observaciones', 'estado']
        widgets = {
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'tecnico': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'equipo': 'Equipo',
            'tipo': 'Tipo de Mantenimiento',
            'fecha_programada': 'Fecha Programada',
            'tecnico': 'Técnico Asignado',
            'observaciones': 'Observaciones',
            'estado': 'Estado',
        }


class MantenimientoCompletarForm(forms.Form):
    fecha_realizada = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de Realización',
    )
    observaciones_final = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Observaciones Finales',
        required=False,
    )
