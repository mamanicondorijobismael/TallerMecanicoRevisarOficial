import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

from apps.accounts.models import Usuario

try:
    mecanico = Usuario.objects.get(username='mecanico')
    mecanico.is_active = True
    mecanico.set_password('mecanico123')
    mecanico.save()
    print("Mecánico activado y contraseña reseteada a: mecanico123")
except Usuario.DoesNotExist:
    print("El usuario 'mecanico' no existe.")
