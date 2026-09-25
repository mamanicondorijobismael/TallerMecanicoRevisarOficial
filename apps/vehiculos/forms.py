from django import forms
from .models import Vehiculo
from apps.clientes.models import Cliente


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio', 'vin', 'color', 'kilometraje_actual', 'foto', 'activo']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-input'}),
            'patente': forms.TextInput(attrs={'class': 'form-input uppercase', 'placeholder': 'AB123CD'}),
            'marca': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Toyota, Ford, Renault...'}),
            'modelo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Corolla, Falcon...'}),
            'anio': forms.NumberInput(attrs={'class': 'form-input', 'min': 1900, 'max': 2030}),
            'vin': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'VIN / Nro. de chasis'}),
            'color': forms.Select(attrs={'class': 'form-input'}),
            'kilometraje_actual': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
        }
