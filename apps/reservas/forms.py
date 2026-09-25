from django import forms
from .models import Reserva
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo

W = {'class': 'form-input'}

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'vehiculo', 'fecha_hora', 'servicio_solicitado', 'estado', 'notas']
        widgets = {
            'cliente': forms.Select(attrs=W),
            'vehiculo': forms.Select(attrs=W),
            'fecha_hora': forms.DateTimeInput(attrs={**W, 'type': 'datetime-local'}),
            'servicio_solicitado': forms.TextInput(attrs={**W, 'placeholder': 'Tipo de servicio solicitado'}),
            'estado': forms.Select(attrs=W),
            'notas': forms.Textarea(attrs={**W, 'rows': 2}),
        }
