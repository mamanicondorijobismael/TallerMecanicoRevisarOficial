from django import forms
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto
from apps.inventario.models import ProductoBase

W = {'class': 'form-input'}


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'mecanico', 'kilometraje', 'diagnostico', 'observaciones', 'fecha_prometida']
        widgets = {
            'vehiculo': forms.Select(attrs=W),
            'mecanico': forms.Select(attrs=W),
            'kilometraje': forms.NumberInput(attrs={**W, 'min': '0'}),
            'diagnostico': forms.Textarea(attrs={**W, 'rows': 3, 'placeholder': 'Descripcion del problema...'}),
            'observaciones': forms.Textarea(attrs={**W, 'rows': 2, 'placeholder': 'Observaciones adicionales...'}),
            'fecha_prometida': forms.DateTimeInput(attrs={**W, 'type': 'datetime-local'}),
        }


class DetalleServicioForm(forms.ModelForm):
    class Meta:
        model = DetalleServicio
        fields = ['descripcion', 'cantidad', 'precio_unitario']
        widgets = {
            'descripcion': forms.TextInput(attrs={**W, 'placeholder': 'Descripcion del servicio'}),
            'cantidad': forms.NumberInput(attrs={**W, 'step': '0.5', 'min': '0.5', 'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={**W, 'step': '0.01', 'min': '0'}),
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
