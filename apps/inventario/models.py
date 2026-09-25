from django.db import models
from django.core.validators import MinValueValidator
from core.models import ModeloBase


class CategoriaProducto(ModeloBase):
    TIPO_CHOICES = [('REPUESTO', 'Repuesto'), ('NEUMATICO', 'Neumático')]
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='REPUESTO', verbose_name='Tipo de categoría')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    icono = models.CharField(max_length=50, blank=True, default='box', verbose_name='Icono')

    class Meta:
        verbose_name = 'Categoria de Producto'
        verbose_name_plural = 'Categorias de Productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProductoBase(ModeloBase):
    """Producto base del inventario (repuesto o neumatico)."""
    TIPO_CHOICES = [('REPUESTO', 'Repuesto'), ('NEUMATICO', 'Neumatico')]

    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.RESTRICT, related_name='productos', verbose_name='Categoria')
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name='Codigo SKU')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Precio de costo')
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Precio de venta')
    stock_actual = models.PositiveIntegerField(default=0, verbose_name='Stock actual')
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name='Stock minimo')
    tipo_producto = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name='Imagen')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo_sku']),
            models.Index(fields=['tipo_producto']),
        ]

    def save(self, *args, **kwargs):
        if not self.codigo_sku:
            prefix = 'REP-' if self.tipo_producto == 'REPUESTO' else 'NEU-'
            last = ProductoBase.objects.filter(codigo_sku__startswith=prefix).count()
            self.codigo_sku = f"{prefix}{str(last + 1).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.codigo_sku}] {self.nombre}'

    @property
    def margen_ganancia(self):
        if self.precio_venta > 0:
            return round(((self.precio_venta - self.precio_costo) / self.precio_venta) * 100, 2)
        return 0

    @property
    def stock_critico(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def ganancia_unitaria(self):
        return self.precio_venta - self.precio_costo


class RepuestoGenerico(models.Model):
    """Repuesto con informacion tecnica especifica."""
    producto = models.OneToOneField(ProductoBase, on_delete=models.CASCADE, primary_key=True, related_name='repuesto')
    marca_repuesto = models.CharField(max_length=50, blank=True, verbose_name='Marca del repuesto')
    numero_parte = models.CharField(max_length=100, blank=True, verbose_name='Numero de parte')
    compatible_con = models.TextField(blank=True, verbose_name='Compatible con (marca/modelo/anio)')

    class Meta:
        verbose_name = 'Repuesto Generico'
        verbose_name_plural = 'Repuestos Genericos'

    def __str__(self):
        return str(self.producto)


class Neumatico(models.Model):
    """Neumatico con especificaciones tecnicas."""
    TIPO_CHOICES = [('VERANO', 'Verano'), ('INVIERNO', 'Invierno'), ('ALL_SEASON', 'All Season'), ('OFF_ROAD', 'Off Road')]
    ESTADO_CHOICES = [('NUEVO', 'Nuevo'), ('USADO', 'Usado')]

    producto = models.OneToOneField(ProductoBase, on_delete=models.CASCADE, primary_key=True, related_name='neumatico')
    marca_neumatico = models.CharField(max_length=50, verbose_name='Marca del neumatico')
    modelo_neumatico = models.CharField(max_length=50, blank=True, verbose_name='Modelo')
    ancho = models.PositiveIntegerField(verbose_name='Ancho (mm)')
    perfil = models.PositiveIntegerField(verbose_name='Perfil (%)')
    diametro = models.PositiveIntegerField(verbose_name='Diametro (R)')
    indice_carga = models.CharField(max_length=10, blank=True, verbose_name='Indice de carga')
    indice_velocidad = models.CharField(max_length=5, blank=True, verbose_name='Indice de velocidad')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='ALL_SEASON', verbose_name='Tipo')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='NUEVO', verbose_name='Estado')
    profundidad_restante = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name='Profundidad restante (mm)')

    class Meta:
        verbose_name = 'Neumatico'
        verbose_name_plural = 'Neumaticos'

    def __str__(self):
        return f'{self.marca_neumatico} {self.ancho}/{self.perfil}R{self.diametro}'

    @property
    def medida(self):
        return f'{self.ancho}/{self.perfil}R{self.diametro}'


class MovimientoStock(models.Model):
    """Registro de movimientos de inventario."""
    TIPO_CHOICES = [('ENTRADA', 'Entrada'), ('SALIDA', 'Salida'), ('AJUSTE', 'Ajuste'), ('VENTA_DIRECTA', 'Venta directa')]

    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE, related_name='movimientos', verbose_name='Producto')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de movimiento')
    cantidad = models.IntegerField(verbose_name='Cantidad')
    stock_resultante = models.IntegerField(verbose_name='Stock resultante')
    motivo = models.CharField(max_length=200, verbose_name='Motivo')
    orden = models.ForeignKey('ordenes.OrdenTrabajo', on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_stock', verbose_name='Orden de trabajo')
    usuario = models.CharField(max_length=150, blank=True, verbose_name='Usuario')
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Precio unitario')
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha_movimiento']

    def __str__(self):
        return f'{self.tipo_movimiento} - {self.producto.nombre} x{self.cantidad}'

    @property
    def valor_total(self):
        if self.precio_unitario:
            return abs(self.cantidad) * self.precio_unitario
        return 0
