from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_razon_social', 'documento', 'telefono', 'email', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre_razon_social', 'documento', 'telefono', 'email')
    ordering = ('nombre_razon_social',)
