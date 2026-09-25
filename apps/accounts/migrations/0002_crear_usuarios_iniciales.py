from django.db import migrations

def crear_usuarios(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    from django.contrib.auth.hashers import make_password
    
    usuarios_data = [
        {
            'username': 'admin',
            'email': 'admin@tallerges.com',
            'nombre_completo': 'Super Administrador',
            'password': make_password('Admin2024!'),
            'rol': 'DUENO',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'dueno',
            'email': 'dueno@tallerges.com',
            'nombre_completo': 'Dueño del Taller',
            'password': make_password('Taller2024!'),
            'rol': 'DUENO',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'gerente',
            'email': 'gerente@tallerges.com',
            'nombre_completo': 'Gerente de Administración',
            'password': make_password('Gerente2024!'),
            'rol': 'ADMINISTRADOR',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'mecanico1',
            'email': 'mecanico1@tallerges.com',
            'nombre_completo': 'Carlos Gómez (Mecánico Jefe)',
            'password': make_password('Mec2024!'),
            'rol': 'MECANICO',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'mecanico2',
            'email': 'mecanico2@tallerges.com',
            'nombre_completo': 'Lucas Fernández (Especialista Gomero)',
            'password': make_password('Mec2024!'),
            'rol': 'MECANICO',
            'is_staff': False,
            'is_superuser': False,
        },
    ]
    
    for udata in usuarios_data:
        Usuario.objects.update_or_create(
            username=udata['username'],
            defaults=udata
        )

def revertir_usuarios(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_usuarios, revertir_usuarios),
    ]
