from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'cliente', 'vehiculo', 'servicio_solicitado', 'estado', 'orden_generada')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('cliente__nombre_razon_social', 'vehiculo__placa', 'servicio_solicitado')
    ordering = ('-fecha_hora',)
    raw_id_fields = ('cliente', 'vehiculo', 'orden_generada')
