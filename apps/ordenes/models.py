from django.db import models
from django.core.validators import MinValueValidator
from core.models import ModeloBase
from apps.vehiculos.models import Vehiculo


class OrdenTrabajo(ModeloBase):
    """Orden de trabajo del taller."""
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        PAUSADA = 'PAUSADA', 'Pausada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        FACTURADA = 'FACTURADA', 'Cobrada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    TRANSICIONES_VALIDAS = {
        'PENDIENTE': ['EN_PROCESO', 'COMPLETADA', 'PAUSADA', 'CANCELADA'],
        'EN_PROCESO': ['COMPLETADA', 'PAUSADA', 'PENDIENTE', 'CANCELADA'],
        'PAUSADA': ['EN_PROCESO', 'COMPLETADA', 'PENDIENTE', 'CANCELADA'],
        'COMPLETADA': ['EN_PROCESO', 'PAUSADA'],  # Puede reabrirse si no ha sido cobrada
        'FACTURADA': [],  # Cobrada y cerrada
        'CANCELADA': ['PENDIENTE', 'EN_PROCESO'],  # Reactivar si fue cancelada por error
    }

    numero_orden = models.CharField(max_length=20, unique=True, verbose_name='N° de orden')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, related_name='ordenes', verbose_name='Vehiculo')
    mecanico = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ordenes_asignadas', limit_choices_to={'rol__in': ['MECANICO', 'ADMINISTRADOR', 'DUENO']},
        verbose_name='Mecanico asignado'
    )
    creado_por = models.ForeignKey(
        'accounts.Usuario', on_delete=models.SET_NULL, null=True,
        related_name='ordenes_creadas', verbose_name='Creado por'
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    kilometraje = models.PositiveIntegerField(default=0, verbose_name='Kilometraje al ingreso')
    diagnostico = models.TextField(blank=True, verbose_name='Diagnostico')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    fecha_prometida = models.DateTimeField(null=True, blank=True, verbose_name='Fecha prometida')
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cierre')

    class Meta:
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Ordenes de Trabajo'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['numero_orden']),
            models.Index(fields=['estado']),
            models.Index(fields=['vehiculo']),
        ]

    def __str__(self):
        return f'OT#{self.numero_orden} - {self.vehiculo.patente} [{self.get_estado_display()}]'

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            import datetime
            prefix = datetime.date.today().strftime('%Y%m')
            last = OrdenTrabajo.objects.filter(numero_orden__startswith=prefix).count()
            self.numero_orden = f'{prefix}{str(last + 1).zfill(4)}'
        super().save(*args, **kwargs)

    @property
    def cliente(self):
        return self.vehiculo.cliente

    @property
    def subtotal_servicios(self):
        return sum(d.subtotal for d in self.servicios.all())

    @property
    def subtotal_productos(self):
        return sum(d.subtotal for d in self.productos.all())

    @property
    def subtotal(self):
        return self.subtotal_servicios + self.subtotal_productos

    @property
    def iva_monto(self):
        from django.conf import settings
        iva = getattr(settings, 'IVA_PORCENTAJE', 21)
        return round(self.subtotal * iva / 100, 2)

    @property
    def total(self):
        return self.subtotal + self.iva_monto

    @property
    def costo_total(self):
        return sum(d.costo_total for d in self.productos.all())

    @property
    def ganancia_bruta(self):
        return self.total - self.costo_total

    def puede_transicionar(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES_VALIDAS.get(self.estado, [])


class DetalleServicio(models.Model):
    """Servicio/mano de obra incluida en la orden."""
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='servicios', verbose_name='Orden')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion del servicio')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1, validators=[MinValueValidator(0)], verbose_name='Cantidad/Horas')
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Precio unitario')

    class Meta:
        verbose_name = 'Detalle de Servicio'
        verbose_name_plural = 'Detalles de Servicio'

    def __str__(self):
        return f'{self.descripcion} x{self.cantidad}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class DetalleProducto(models.Model):
    """Producto/repuesto incluido en la orden."""
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='productos', verbose_name='Orden')
    producto = models.ForeignKey('inventario.ProductoBase', on_delete=models.RESTRICT, related_name='usos', verbose_name='Producto')
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario aplicado')

    class Meta:
        verbose_name = 'Detalle de Producto'
        verbose_name_plural = 'Detalles de Producto'

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def costo_total(self):
        return self.cantidad * self.producto.precio_costo
