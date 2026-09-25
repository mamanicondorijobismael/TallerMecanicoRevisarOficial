from django.contrib import admin
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto


class DetalleServicioInline(admin.TabularInline):
    model = DetalleServicio
    extra = 1


class DetalleProductoInline(admin.TabularInline):
    model = DetalleProducto
    extra = 1
    raw_id_fields = ('producto',)


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'vehiculo', 'get_cliente', 'mecanico', 'estado', 'kilometraje', 'fecha_creacion', 'get_total')
    list_filter = ('estado', 'mecanico', 'fecha_creacion')
    search_fields = ('numero_orden', 'vehiculo__patente', 'vehiculo__cliente__nombre_razon_social', 'diagnostico')
    ordering = ('-fecha_creacion',)
    raw_id_fields = ('vehiculo', 'mecanico', 'creado_por')
    inlines = [DetalleServicioInline, DetalleProductoInline]

    @admin.display(description='Cliente')
    def get_cliente(self, obj):
        return obj.vehiculo.cliente.nombre_razon_social if obj.vehiculo else '-'

    @admin.display(description='Total')
    def get_total(self, obj):
        return f"${obj.total:,.2f}"


@admin.register(DetalleServicio)
class DetalleServicioAdmin(admin.ModelAdmin):
    list_display = ('orden', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('orden__numero_orden', 'descripcion')


@admin.register(DetalleProducto)
class DetalleProductoAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('orden__numero_orden', 'producto__nombre', 'producto__codigo_sku')
    raw_id_fields = ('producto',)
