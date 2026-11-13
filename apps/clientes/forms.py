from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_razon_social', 'documento', 'telefono', 'email', 'direccion', 'foto', 'activo']
        widgets = {
            'nombre_razon_social': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo o razon social'}),
            'documento': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'CI o DNI '}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+591 ........'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'activo': 'Cliente Habilitado / Activo',
        }
        
    def clean_nombre_razon_social(self):
        nombre = self.cleaned_data.get('nombre_razon_social', '')
        return nombre.strip() if nombre else nombre
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento', '')
        return documento.strip() if documento else documento

    def save(self, commit=True):
        cliente = super().save(commit=commit)
        # Si se desactiva el cliente, desactivar también sus vehículos
        if commit and not cliente.activo:
            cliente.vehiculos.all().update(activo=False)
        return cliente
        
