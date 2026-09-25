from django.db import models
from core.models import ModeloBase
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo


class Reserva(ModeloBase):
    """Cita programada para un servicio."""
    class Estado(models.TextChoices):
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        PENDIENTE = 'PENDIENTE', 'Pendiente'

    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='reservas', verbose_name='Cliente')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, related_name='reservas', verbose_name='Vehiculo')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y hora')
    servicio_solicitado = models.CharField(max_length=200, verbose_name='Servicio solicitado')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    notas = models.TextField(blank=True, verbose_name='Notas adicionales')
    orden_generada = models.OneToOneField(
        'ordenes.OrdenTrabajo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reserva_origen', verbose_name='Orden de trabajo generada'
    )

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['fecha_hora']

    def __str__(self):
        return f'Reserva {self.cliente} - {self.fecha_hora.strftime("%d/%m/%Y %H:%M")} - {self.servicio_solicitado}'
