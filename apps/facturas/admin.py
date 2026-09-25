from django.contrib import admin
from .models import Factura, Pago


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'orden', 'cliente', 'fecha_emision', 'total', 'saldo_pendiente', 'estado_pago')
    list_filter = ('estado_pago', 'fecha_emision')
    search_fields = ('numero_factura', 'cliente__nombre_razon_social', 'orden__numero_orden')
    ordering = ('-fecha_emision',)
    raw_id_fields = ('orden', 'cliente')
    inlines = [PagoInline]


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('factura', 'fecha', 'metodo_pago', 'monto', 'referencia', 'usuario')
    list_filter = ('metodo_pago', 'fecha')
    search_fields = ('factura__numero_factura', 'referencia', 'usuario')
    raw_id_fields = ('factura',)
