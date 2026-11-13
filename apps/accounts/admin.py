from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


from .forms import UsuarioCreationForm, UsuarioChangeForm


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    list_display = ('username', 'nombre_completo', 'email', 'rol', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'nombre_completo', 'email', 'telefono')
    ordering = ('rol', 'username')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('nombre_completo', 'email', 'telefono', 'foto', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nombre_completo', 'email', 'rol', 'telefono', 'password1', 'password2'),
        }),
    )
