from django.db import models
from django.core.validators import RegexValidator
from core.models import ModeloBase


class Cliente(ModeloBase):
    """Clientes del taller mecanico."""
    nombre_razon_social = models.CharField(max_length=100, verbose_name='Nombre / Razon Social')
    documento = models.CharField(max_length=20, unique=True, verbose_name='DNI / CUIT')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    email = models.EmailField(blank=True, verbose_name='Email')
    direccion = models.TextField(blank=True, verbose_name='Direccion')
    foto = models.ImageField(upload_to='clientes/', null=True, blank=True, verbose_name='Foto')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_razon_social']
        indexes = [
            models.Index(fields=['documento']),
            models.Index(fields=['nombre_razon_social']),
        ]

    def __str__(self):
        return self.nombre_razon_social

    @property
    def cantidad_vehiculos(self):
        return self.vehiculos.count()
