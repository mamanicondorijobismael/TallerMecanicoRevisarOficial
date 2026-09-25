from django.db import models
from core.models import ModeloBase
from apps.vehiculos.models import Vehiculo


class TipoServicio(ModeloBase):
    """Tipos de servicio disponibles en el taller."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre del servicio')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Precio base')
    intervalo_km = models.PositiveIntegerField(null=True, blank=True, verbose_name='Intervalo en km')
    intervalo_meses = models.PositiveIntegerField(null=True, blank=True, verbose_name='Intervalo en meses')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Tipo de Servicio'
        verbose_name_plural = 'Tipos de Servicio'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class AlertaMantenimiento(ModeloBase):
    """Alerta de mantenimiento preventivo para un vehiculo."""
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        NOTIFICADA = 'NOTIFICADA', 'Notificada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        IGNORADA = 'IGNORADA', 'Ignorada'

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='alertas_mantenimiento', verbose_name='Vehiculo')
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE, related_name='alertas', verbose_name='Tipo de servicio')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    km_estimado = models.PositiveIntegerField(null=True, blank=True, verbose_name='Km estimado para servicio')
    fecha_estimada = models.DateField(null=True, blank=True, verbose_name='Fecha estimada')
    notas = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Alerta de Mantenimiento'
        verbose_name_plural = 'Alertas de Mantenimiento'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Alerta: {self.tipo_servicio} - {self.vehiculo.patente} [{self.get_estado_display()}]'
