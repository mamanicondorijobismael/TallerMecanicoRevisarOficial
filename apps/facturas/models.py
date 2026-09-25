from django.db import models
from django.core.validators import MinValueValidator
from core.models import ModeloBase
from apps.ordenes.models import OrdenTrabajo
from apps.clientes.models import Cliente


class Factura(ModeloBase):
    """Factura generada desde una orden de trabajo completada."""
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PARCIAL = 'PARCIAL', 'Pago parcial'
        PAGADA = 'PAGADA', 'Pagada'
        ANULADA = 'ANULADA', 'Anulada'

    numero_factura = models.CharField(max_length=20, unique=True, verbose_name='N° Factura')
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.RESTRICT, related_name='factura', verbose_name='Orden de trabajo')
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='facturas', verbose_name='Cliente')
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de emision')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Subtotal')
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=21, verbose_name='IVA %')
    iva_monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='IVA monto')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total')
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE, verbose_name='Estado de pago')
    notas = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f'FAC#{self.numero_factura} - {self.cliente} - ${self.total}'

    def save(self, *args, **kwargs):
        if not self.numero_factura:
            import datetime
            prefix = datetime.date.today().strftime('F%Y%m')
            last = Factura.objects.filter(numero_factura__startswith=prefix).count()
            self.numero_factura = f'{prefix}{str(last + 1).zfill(4)}'
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
    """Pago parcial o total de una factura."""
    METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de debito'),
        ('TARJETA_CREDITO', 'Tarjeta de credito'),
        ('TRANSFERENCIA', 'Transferencia bancaria'),
        ('CHEQUE', 'Cheque'),
        ('MERCADO_PAGO', 'Mercado Pago'),
    ]

    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos', verbose_name='Factura')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name='Monto')
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES, default='EFECTIVO', verbose_name='Metodo de pago')
    referencia = models.CharField(max_length=100, blank=True, verbose_name='Referencia / Comprobante')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de pago')
    usuario = models.CharField(max_length=150, blank=True, verbose_name='Registrado por')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']

    def __str__(self):
        return f'Pago ${self.monto} - FAC#{self.factura.numero_factura} [{self.get_metodo_pago_display()}]'
