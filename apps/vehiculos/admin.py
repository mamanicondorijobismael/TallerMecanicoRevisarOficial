from django.contrib import admin
from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'anio', 'cliente', 'color', 'kilometraje_actual', 'activo')
    list_filter = ('marca', 'color', 'activo')
    search_fields = ('patente', 'marca', 'modelo', 'vin', 'cliente__nombre_razon_social')
    ordering = ('patente',)
    raw_id_fields = ('cliente',)
