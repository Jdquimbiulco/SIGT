from django import forms

from .models import Equipo, Ubicacion


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        exclude = ['historical', 'fecha_registro']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_otro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: cámara, pizarra interactiva, router...',
            }),
            'aula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 01, 05, 13',
            }),
            'procesador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Intel Core i5',
            }),
            'ram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 8 GB',
            }),
            'so': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Windows 11',
            }),
            'almacenamiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: SSD 256 GB',
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
            }),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_tipo_otro(self):
        tipo = self.cleaned_data.get('tipo')
        tipo_otro = self.cleaned_data.get('tipo_otro', '')
        if tipo == 'otro' and not tipo_otro.strip():
            raise forms.ValidationError('Debe especificar el tipo cuando selecciona "Otro".')
        return tipo_otro


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'padre': forms.Select(attrs={'class': 'form-select'}),
            'edificio': forms.TextInput(attrs={'class': 'form-control'}),
            'salon': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            excluidos = [self.instance.pk]
            for u in self.instance.sububicaciones.all():
                excluidos.append(u.pk)
            self.fields['padre'].queryset = Ubicacion.objects.exclude(pk__in=excluidos)