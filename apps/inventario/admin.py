from django.contrib import admin
from .models import CategoriaProducto, ProductoBase, RepuestoGenerico, Neumatico, MovimientoStock


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'icono')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'descripcion')


@admin.register(ProductoBase)
class ProductoBaseAdmin(admin.ModelAdmin):
    list_display = ('codigo_sku', 'nombre', 'categoria', 'tipo_producto', 'stock_actual', 'stock_minimo', 'precio_costo', 'precio_venta', 'activo')
    list_filter = ('tipo_producto', 'categoria', 'activo')
    search_fields = ('codigo_sku', 'nombre', 'descripcion')
    ordering = ('nombre',)


@admin.register(RepuestoGenerico)
class RepuestoGenericoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'marca_repuesto', 'numero_parte', 'compatible_con')
    search_fields = ('producto__nombre', 'marca_repuesto', 'numero_parte')


@admin.register(Neumatico)
class NeumaticoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'marca_neumatico', 'modelo_neumatico', 'ancho', 'perfil', 'diametro', 'tipo', 'estado')
    list_filter = ('marca_neumatico', 'tipo', 'estado')
    search_fields = ('producto__nombre', 'marca_neumatico', 'modelo_neumatico')


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('fecha_movimiento', 'producto', 'tipo_movimiento', 'cantidad', 'stock_resultante', 'motivo', 'usuario')
    list_filter = ('tipo_movimiento', 'fecha_movimiento')
    search_fields = ('producto__nombre', 'producto__codigo_sku', 'motivo', 'usuario')
    ordering = ('-fecha_movimiento',)
    raw_id_fields = ('producto', 'orden')
