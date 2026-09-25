from django.contrib import admin
from .models import Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'tabla', 'registro_id', 'ip_address')
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = ('usuario', 'tabla', 'ip_address')
    ordering = ('-fecha',)
    readonly_fields = ('fecha', 'usuario', 'accion', 'tabla', 'registro_id', 'valores_anteriores', 'valores_nuevos', 'ip_address')
