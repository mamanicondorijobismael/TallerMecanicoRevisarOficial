from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rol_alter_usuario_rol'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rol',
            name='puede_ver_auditoria',
        ),
    ]
