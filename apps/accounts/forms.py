from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'telefono', 'foto')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: jperez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-pro', 'placeholder': 'correo@ejemplo.com'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: Juan Pérez'}),
            'rol': forms.Select(attrs={'class': 'form-control-pro'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': '+591 70000000'}),
            'foto': forms.FileInput(attrs={'class': 'd-none', 'id': 'usuario-foto-input', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control-pro', 'placeholder': '••••••••'})
            self.fields['password1'].label = 'Contraseña'
            self.fields['password1'].help_text = 'Mínimo 8 caracteres, combina números y letras.'
        if 'password2' in self.fields:
            self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control-pro', 'placeholder': '••••••••'})
            self.fields['password2'].label = 'Confirmar Contraseña'
            self.fields['password2'].help_text = 'Repetí la contraseña ingresada arriba.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.telefono = self.cleaned_data.get("telefono", "")
        user.rol = self.cleaned_data.get("rol")
        if self.cleaned_data.get("foto"):
            user.foto = self.cleaned_data["foto"]
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rol', 'telefono', 'foto', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: jperez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control-pro', 'placeholder': 'correo@ejemplo.com'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: Juan Pérez'}),
            'rol': forms.Select(attrs={'class': 'form-control-pro'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': '+591 70000000'}),
            'foto': forms.FileInput(attrs={'class': 'd-none', 'id': 'usuario-foto-input', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }
        labels = {
            'is_active': 'Usuario Activo / Habilitado',
        }
        help_texts = {
            'is_active': 'Desmarcar para deshabilitar el acceso del usuario al sistema sin borrar su historial ni registros.',
        }


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = [
            'nombre', 'codigo', 'descripcion',
            'puede_ver_dashboard',
            'puede_ver_clientes', 'puede_crear_clientes', 'puede_editar_clientes', 'puede_eliminar_clientes',
            'puede_ver_vehiculos', 'puede_crear_vehiculos', 'puede_editar_vehiculos', 'puede_eliminar_vehiculos',
            'puede_ver_ordenes', 'puede_crear_ordenes', 'puede_editar_ordenes', 'puede_cambiar_estado_ordenes', 'puede_eliminar_ordenes',
            'puede_ver_inventario', 'puede_crear_inventario', 'puede_editar_inventario', 'puede_eliminar_inventario', 'puede_ajustar_stock',
            'puede_ver_comprobantes', 'puede_crear_comprobantes', 'puede_cobrar_comprobantes', 'puede_anular_comprobantes',
            'puede_ver_reportes', 'puede_ver_cierre_diario',
            'puede_gestionar_usuarios', 'puede_gestionar_roles',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: Jefe de Taller'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control-pro', 'placeholder': 'Ej: JEFE_TALLER'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control-pro', 'rows': 2, 'placeholder': 'Descripción de funciones...'}),
        }