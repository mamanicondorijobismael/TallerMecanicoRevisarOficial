import datetime
from django.db import models
from django.core.validators import MinValueValidator
from core.models import ModeloBase
from apps.ordenes.models import OrdenTrabajo
from apps.clientes.models import Cliente


class Recibo(ModeloBase):
    """Recibo oficial de servicio y cobro generado desde una orden de trabajo completada."""
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PARCIAL = 'PARCIAL', 'Pago parcial'
        PAGADA = 'PAGADA', 'Pagado / Cobrado'
        ANULADA = 'ANULADA', 'Anulado'

    numero_recibo = models.CharField(max_length=20, unique=True, verbose_name='N° de Recibo')
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.RESTRICT, related_name='recibo', verbose_name='Orden de trabajo')
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='recibos', verbose_name='Cliente')
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de emisión')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal')
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=21, verbose_name='IVA %')
    iva_monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='IVA monto')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total')
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE, verbose_name='Estado de pago')
    notas = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f'REC#{self.numero_recibo} - {self.cliente} - Bs {self.total}'

    def save(self, *args, **kwargs):
        if not self.numero_recibo:
            prefix = datetime.date.today().strftime('REC%Y%m')
            last_rec = Recibo.objects.filter(numero_recibo__startswith=prefix).order_by('-numero_recibo').first()
            if last_rec and last_rec.numero_recibo[len(prefix):].isdigit():
                seq = int(last_rec.numero_recibo[len(prefix):]) + 1
            else:
                seq = 1
            self.numero_recibo = f'{prefix}{str(seq).zfill(4)}'
        super().save(*args, **kwargs)

    @property
    def total_pagado(self):
        return sum(p.monto for p in self.pagos.all())

    @property
    def saldo_pendiente(self):
        return self.total - self.total_pagado

    def actualizar_estado(self):
        pagado = self.total_pagado
        if pagado >= self.total:
            self.estado_pago = 'PAGADA'
        elif pagado > 0:
            self.estado_pago = 'PARCIAL'
        else:
            self.estado_pago = 'PENDIENTE'
        self.save()


class Pago(models.Model):
    """Pago parcial o total de un recibo."""
    METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
    ]

    recibo = models.ForeignKey(Recibo, on_delete=models.CASCADE, related_name='pagos', verbose_name='Recibo')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name='Monto')
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES, default='EFECTIVO', verbose_name='Método de pago')
    referencia = models.CharField(max_length=100, blank=True, verbose_name='Referencia')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de pago')
    usuario = models.CharField(max_length=150, blank=True, verbose_name='Registrado por')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']

    def __str__(self):
        return f'Pago Bs {self.monto} - Recibo #{self.recibo.numero_recibo} [{self.get_metodo_pago_display()}]'
