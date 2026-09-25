from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'telefono', 'foto')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre completo'}),
            'rol': forms.Select(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+54 9 ...'}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telefono = self.cleaned_data["telefono"]
        user.rol = self.cleaned_data["rol"]
        if self.cleaned_data["foto"]:
            user.foto = self.cleaned_data["foto"]
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'telefono', 'foto', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-input'}),
            'rol': forms.Select(attrs={'class': 'form-input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input'}),
            'foto': forms.FileInput(attrs={'class': 'form-input'}),
        }
