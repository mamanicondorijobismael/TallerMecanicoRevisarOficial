from django.core.management.base import BaseCommand
from apps.accounts.models import Usuario

class Command(BaseCommand):
    help = 'Crea o actualiza los usuarios del sistema El Taller del Maestro'

    def handle(self, *args, **options):
        usuarios_data = [
            {
                'username': 'admin',
                'email': 'admin@taller.com',
                'nombre_completo': 'Administrador Principal',
                'password': 'admin123',
                'rol': 'DUENO',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'recepcionista',
                'email': 'recepcion@taller.com',
                'nombre_completo': 'María González',
                'password': 'admin123',
                'rol': 'ADMINISTRADOR',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'supervisor',
                'email': 'supervisor@taller.com',
                'nombre_completo': 'Carlos Supervilla',
                'password': 'admin123',
                'rol': 'ADMINISTRADOR',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'mecanico1',
                'email': 'mecanico1@taller.com',
                'nombre_completo': 'Juan Rodríguez',
                'password': 'admin123',
                'rol': 'MECANICO',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'mecanico2',
                'email': 'mecanico2@taller.com',
                'nombre_completo': 'Pedro Ramírez',
                'password': 'admin123',
                'rol': 'MECANICO',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        self.stdout.write(self.style.HTTP_INFO('\n═══════════════════════════════════════════════'))
        self.stdout.write(self.style.HTTP_INFO('  El Taller del Maestro - Gestión de Usuarios'))
        self.stdout.write(self.style.HTTP_INFO('═══════════════════════════════════════════════'))

        for udata in usuarios_data:
            user, created = Usuario.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'nombre_completo': udata['nombre_completo'],
                    'rol': udata['rol'],
                    'is_staff': udata['is_staff'],
                    'is_superuser': udata['is_superuser'],
                }
            )
            user.set_password(udata['password'])
            user.email = udata['email']
            user.nombre_completo = udata['nombre_completo']
            user.rol = udata['rol']
            user.is_staff = udata['is_staff']
            user.is_superuser = udata['is_superuser']
            user.is_active = True
            user.save()

            estado = "CREADO   " if created else "ACTUALIZADO"
            self.stdout.write(self.style.SUCCESS(f"  [{estado}] {udata['username']:<20} ({user.get_rol_display()})  →  {udata['password']}"))

        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('  TABLA DE ACCESOS:'))
        self.stdout.write(self.style.HTTP_INFO('  ─────────────────────────────────────────────'))
        self.stdout.write(f"  {'Usuario':<20} {'Rol':<20} Contraseña")
        self.stdout.write(self.style.HTTP_INFO('  ─────────────────────────────────────────────'))
        for u in usuarios_data:
            self.stdout.write(f"  {u['username']:<20} {u['rol']:<20} {u['password']}")
        self.stdout.write(self.style.HTTP_INFO('  ─────────────────────────────────────────────'))
        self.stdout.write(self.style.SUCCESS('\n  ¡Todos los usuarios configurados con éxito!\n'))

