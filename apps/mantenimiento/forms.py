from django import forms
from .models import AlertaMantenimiento, TipoServicio
from apps.vehiculos.models import Vehiculo

WIDGET_DEFAULTS = {'class': 'form-input'}

class AlertaForm(forms.ModelForm):
    class Meta:
        model = AlertaMantenimiento
        fields = ['vehiculo', 'tipo_servicio', 'km_estimado', 'fecha_estimada', 'notas']
        widgets = {
            'vehiculo': forms.Select(attrs=WIDGET_DEFAULTS),
            'tipo_servicio': forms.Select(attrs=WIDGET_DEFAULTS),
            'km_estimado': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Ej: 50000'}),
            'fecha_estimada': forms.DateInput(attrs={**WIDGET_DEFAULTS, 'type': 'date'}),
            'notas': forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2, 'placeholder': 'Notas adicionales...'}),
        }

class TipoServicioForm(forms.ModelForm):
    class Meta:
        model = TipoServicio
        fields = ['nombre', 'descripcion', 'precio_base', 'intervalo_km', 'intervalo_meses']
        widgets = {
            'nombre': forms.TextInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Ej: Cambio de Aceite'}),
            'descripcion': forms.Textarea(attrs={**WIDGET_DEFAULTS, 'rows': 2}),
            'precio_base': forms.NumberInput(attrs=WIDGET_DEFAULTS),
            'intervalo_km': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Ej: 10000'}),
            'intervalo_meses': forms.NumberInput(attrs={**WIDGET_DEFAULTS, 'placeholder': 'Ej: 6'}),
        }
