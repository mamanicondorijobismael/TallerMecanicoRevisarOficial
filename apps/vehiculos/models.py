from django.db import models
from django.core.validators import MinValueValidator
from core.models import ModeloBase
from apps.clientes.models import Cliente


class Vehiculo(ModeloBase):
    """Vehiculo asociado a un cliente."""
    COLORES = [
        ('BLANCO', 'Blanco'), ('NEGRO', 'Negro'), ('GRIS', 'Gris'), ('PLATA', 'Plata'),
        ('ROJO', 'Rojo'), ('AZUL', 'Azul'), ('VERDE', 'Verde'), ('AMARILLO', 'Amarillo'),
        ('NARANJA', 'Naranja'), ('MARRON', 'Marron'), ('OTRO', 'Otro'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='vehiculos', verbose_name='Cliente')
    patente = models.CharField(max_length=10, unique=True, verbose_name='Patente')
    marca = models.CharField(max_length=30, verbose_name='Marca')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    anio = models.IntegerField(validators=[MinValueValidator(1900)], null=True, blank=True, verbose_name='Anio')
    vin = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='VIN / Nro. Chasis')
    color = models.CharField(max_length=20, choices=COLORES, default='BLANCO', verbose_name='Color')
    kilometraje_actual = models.PositiveIntegerField(default=0, verbose_name='Kilometraje actual')
    foto = models.ImageField(upload_to='vehiculos/', null=True, blank=True, verbose_name='Foto')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Vehiculo'
        verbose_name_plural = 'Vehiculos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['patente']),
            models.Index(fields=['cliente']),
        ]

    def __str__(self):
        return f'{self.patente} - {self.marca} {self.modelo} ({self.anio})'

    @property
    def ultimo_servicio(self):
        return self.ordenes.filter(estado__in=['COMPLETADA', 'FACTURADA']).order_by('-fecha_creacion').first()
