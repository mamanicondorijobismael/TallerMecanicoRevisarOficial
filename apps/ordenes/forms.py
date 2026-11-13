from django import forms
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto, RepuestoExterno
from apps.inventario.models import ProductoBase
from apps.vehiculos.models import Vehiculo

W = {'class': 'form-input'}


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'mecanico', 'kilometraje', 'diagnostico', 'observaciones', 'fecha_prometida']
        widgets = {
            'vehiculo': forms.Select(attrs=W),
            'mecanico': forms.Select(attrs=W),
            'kilometraje': forms.NumberInput(attrs={**W, 'min': '0'}),
            'diagnostico': forms.Textarea(attrs={**W, 'rows': 4, 'placeholder': 'Describí detalladamente el diagnóstico y observaciones técnicas preliminares...'}),
            'observaciones': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Observaciones internas adicionales...'}),
            'fecha_prometida': forms.DateTimeInput(attrs={**W, 'type': 'datetime-local'}),
        }
        labels = {
            'diagnostico': 'Diagnóstico / Observaciones Técnicas',
            'observaciones': 'Observaciones Internas Adicionales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(activo=True, cliente__activo=True).select_related('cliente').order_by('placa')

    def clean_vehiculo(self):
        vehiculo = self.cleaned_data.get('vehiculo')
        if not vehiculo:
            raise forms.ValidationError('Debe seleccionar un vehículo.')
        if not vehiculo.activo:
            raise forms.ValidationError('El vehículo seleccionado está deshabilitado. No se puede crear una orden de trabajo.')
        if not vehiculo.cliente or not vehiculo.cliente.activo:
            raise forms.ValidationError('El cliente propietario del vehículo se encuentra deshabilitado. No se pueden generar órdenes de trabajo.')
        return vehiculo


class DetalleServicioForm(forms.ModelForm):
    class Meta:
        model = DetalleServicio
        fields = ['descripcion', 'cantidad', 'precio_unitario']
        widgets = {
            'descripcion': forms.TextInput(attrs={**W, 'placeholder': 'Descripcion del servicio (ej. Cambio de aceite, Revisión de frenos)'}),
            'cantidad': forms.HiddenInput(attrs={'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={**W, 'step': '100', 'min': '0', 'placeholder': 'Monto en Bs'}),
        }
        labels = {
            'precio_unitario': 'Monto (Bs)',
        }


class DetalleProductoForm(forms.ModelForm):
    class Meta:
        model = DetalleProducto
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs=W),
            'cantidad': forms.NumberInput(attrs={**W, 'min': '1', 'value': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = ProductoBase.objects.filter(activo=True, stock_actual__gt=0).order_by('nombre')


class RepuestoExternoForm(forms.ModelForm):
    class Meta:
        model = RepuestoExterno
        fields = ['descripcion', 'cantidad', 'precio_unitario']
        widgets = {
            'descripcion': forms.TextInput(attrs={**W, 'placeholder': 'Ej. Bomba de agua alternativa, Correa gates...'}),
            'cantidad': forms.NumberInput(attrs={**W, 'min': '1', 'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={**W, 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
        }

