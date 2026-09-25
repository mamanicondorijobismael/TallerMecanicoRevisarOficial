import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

from apps.accounts.models import Usuario

print("--- Usuarios Registrados ---")
for u in Usuario.objects.all():
    print(f"Username: {u.username} | Email: {u.email} | Rol: {u.rol} | Activo: {u.is_active} | Staff: {u.is_staff}")
