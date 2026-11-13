import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0001_initial'),
        ('ordenes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recibo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')),
                ('numero_recibo', models.CharField(max_length=20, unique=True, verbose_name='N° de Recibo')),
                ('fecha_emision', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de emisión')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Subtotal')),
                ('iva_porcentaje', models.DecimalField(decimal_places=2, default=21, max_digits=5, verbose_name='IVA %')),
                ('iva_monto', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='IVA monto')),
                ('total', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Total')),
                ('estado_pago', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PARCIAL', 'Pago parcial'), ('PAGADA', 'Pagado / Cobrado'), ('ANULADA', 'Anulado')], default='PENDIENTE', max_length=20, verbose_name='Estado de pago')),
                ('notas', models.TextField(blank=True, verbose_name='Notas')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='recibos', to='clientes.cliente', verbose_name='Cliente')),
                ('orden', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='recibo', to='ordenes.ordentrabajo', verbose_name='Orden de trabajo')),
            ],
            options={
                'verbose_name': 'Recibo',
                'verbose_name_plural': 'Recibos',
                'ordering': ['-fecha_emision'],
            },
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)], verbose_name='Monto')),
                ('metodo_pago', models.CharField(choices=[('EFECTIVO', 'Efectivo')], default='EFECTIVO', max_length=30, verbose_name='Método de pago')),
                ('referencia', models.CharField(blank=True, max_length=100, verbose_name='Referencia')),
                ('fecha', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de pago')),
                ('usuario', models.CharField(blank=True, max_length=150, verbose_name='Registrado por')),
                ('recibo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='recibos.recibo', verbose_name='Recibo')),
            ],
            options={
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
                'ordering': ['-fecha'],
            },
        ),
    ]
