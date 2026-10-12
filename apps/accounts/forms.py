from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol


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
            'puede_gestionar_usuarios', 'puede_gestionar_roles', 'puede_ver_auditoria',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jefe de Taller'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: JEFE_TALLER'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción de funciones...'}),
        }
