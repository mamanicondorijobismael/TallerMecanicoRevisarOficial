from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ordenes', '0003_alter_ordentrabajo_mecanico'),
    ]
    operations = [
        migrations.AlterField(
            model_name='ordentrabajo',
            name='estado',
            field=models.CharField(
                choices=[
                    ('PENDIENTE', 'Pendiente'),
                    ('EN_PROCESO', 'En proceso'),
                    ('ESPERA_REPUESTOS', 'Espera Repuestos'),
                    ('COMPLETADA', 'Completada'),
                    ('ENTREGADA', 'Entregada'),
                    ('COBRADA', 'Cobrada'),
                    ('CANCELADA', 'Cancelada'),
                ],
                default='PENDIENTE',
                max_length=20,
                verbose_name='Estado',
            ),
        ),
    ]
