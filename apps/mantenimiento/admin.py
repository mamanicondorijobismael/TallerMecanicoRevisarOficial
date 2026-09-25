from django.contrib import admin
from .models import TipoServicio, AlertaMantenimiento


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'intervalo_km', 'intervalo_meses', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


@admin.register(AlertaMantenimiento)
class AlertaMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'tipo_servicio', 'estado', 'km_estimado', 'fecha_estimada', 'fecha_creacion')
    list_filter = ('estado', 'fecha_estimada')
    search_fields = ('vehiculo__patente', 'vehiculo__cliente__nombre_razon_social', 'tipo_servicio__nombre')
    raw_id_fields = ('vehiculo', 'tipo_servicio')
