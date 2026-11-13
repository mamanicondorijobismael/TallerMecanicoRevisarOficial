from django.contrib import admin
from .models import Recibo, Pago


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('numero_recibo', 'orden', 'cliente', 'fecha_emision', 'total', 'saldo_pendiente', 'estado_pago')
    list_filter = ('estado_pago', 'fecha_emision')
    search_fields = ('numero_recibo', 'cliente__nombre_razon_social', 'orden__numero_orden')
    ordering = ('-fecha_emision',)
    raw_id_fields = ('orden', 'cliente')
    inlines = [PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('recibo', 'fecha', 'metodo_pago', 'monto', 'referencia', 'usuario')
    list_filter = ('metodo_pago', 'fecha')
    search_fields = ('recibo__numero_recibo', 'referencia', 'usuario')
    raw_id_fields = ('recibo',)
