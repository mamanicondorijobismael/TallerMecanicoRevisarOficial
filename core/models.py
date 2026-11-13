from django.db import models


class ModeloBase(models.Model):
    """Modelo abstracto base con timestamps."""
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')

    class Meta:
        abstract = True
