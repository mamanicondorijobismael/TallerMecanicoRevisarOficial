# Generated manually for RepuestoExterno

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepuestoExterno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=200, verbose_name='Descripción del repuesto')),
                ('proveedor', models.CharField(blank=True, max_length=100, verbose_name='Proveedor / Origen')),
                ('cantidad', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Cantidad')),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precio unitario')),
                ('orden', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repuestos_externos', to='ordenes.ordentrabajo', verbose_name='Orden')),
            ],
            options={
                'verbose_name': 'Repuesto Externo',
                'verbose_name_plural': 'Repuestos Externos',
            },
        ),
    ]
