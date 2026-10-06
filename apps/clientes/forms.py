from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_razon_social', 'documento', 'telefono', 'email', 'direccion', 'foto']
        widgets = {
            'nombre_razon_social': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo o razon social'}),
            'documento': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'CI o DNI '}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+591 ........'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
        }
