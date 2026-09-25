from django.db import models
from django.utils import timezone


class ModeloBase(models.Model):
    """Modelo abstracto base con timestamps."""
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')

    class Meta:
        abstract = True


class Auditoria(models.Model):
    """Registro de cambios en entidades criticas del sistema."""
    tabla = models.CharField(max_length=50, verbose_name='Tabla')
    registro_id = models.IntegerField(verbose_name='ID del registro')
    accion = models.CharField(max_length=20, choices=[
        ('CREAR', 'Crear'),
        ('MODIFICAR', 'Modificar'),
        ('ELIMINAR', 'Eliminar'),
    ], verbose_name='Accion')
    usuario = models.CharField(max_length=150, verbose_name='Usuario')
    valores_anteriores = models.JSONField(null=True, blank=True, verbose_name='Valores anteriores')
    valores_nuevos = models.JSONField(null=True, blank=True, verbose_name='Valores nuevos')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.accion} en {self.tabla} #{self.registro_id} por {self.usuario}'
