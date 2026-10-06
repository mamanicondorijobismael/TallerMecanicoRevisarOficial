import datetime
from django import forms
from django.core.validators import RegexValidator
from .models import Vehiculo
from apps.clientes.models import Cliente


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'placa', 'marca', 'modelo', 'anio', 'vin', 'color', 'kilometraje_actual', 'foto']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-input'}),
            'placa': forms.TextInput(attrs={'class': 'form-input uppercase', 'placeholder': 'AB123CD'}),
            'marca': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Toyota...'}),
            'modelo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Corolla...'}),
            'anio': forms.NumberInput(attrs={'class': 'form-input', 'min': 1900}),
            'vin': forms.TextInput(attrs={'class': 'form-input uppercase', 'placeholder': 'Nro. de chasis (Opcional)'}),
            'color': forms.Select(attrs={'class': 'form-input'}),
            'kilometraje_actual': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'placeholder': '0'}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('nombre_razon_social')
        
        anio_maximo = datetime.date.today().year + 1 
        self.fields['anio'].widget.attrs['max'] = anio_maximo
    
    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '')
        if placa:
            placa = placa.strip().upper()
        return placa
    
    def clean_vin(self):
        vin = self.cleaned_data.get('vin', '')
        if vin:
            return vin.strip().upper()
        return None
    
    def clean_anio(self):
        anio = self.cleaned_data.get('anio')
        if anio:
            anio_maximo = datetime.date.today().year + 1
            if anio > anio_maximo:
                raise forms.ValidationError(f'El año no puede ser mayor a {anio_maximo}')
            return anio
        return None