from django.contrib import admin
from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'anio', 'cliente', 'color', 'kilometraje_actual', 'activo')
    list_filter = ('marca', 'color', 'activo')
    search_fields = ('placa', 'marca', 'modelo', 'vin', 'cliente__nombre_razon_social')
    ordering = ('placa',)
    raw_id_fields = ('cliente',)
