from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Rol(models.Model):
    """
    Tabla de Roles y Privilegios del sistema.
    Control granular y estricto de accesos y permisos por módulo y acción.
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Nombre del Rol')
    codigo = models.CharField(max_length=30, unique=True, verbose_name='Código identificador')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    # --- Privilegios Panel de Control ---
    puede_ver_dashboard = models.BooleanField(default=True, verbose_name='Ver Panel de Control')

    # --- Privilegios Clientes ---
    puede_ver_clientes = models.BooleanField(default=True, verbose_name='Ver Clientes')
    puede_crear_clientes = models.BooleanField(default=False, verbose_name='Crear Clientes')
    puede_editar_clientes = models.BooleanField(default=False, verbose_name='Editar Clientes')
    puede_eliminar_clientes = models.BooleanField(default=False, verbose_name='Eliminar Clientes')

    # --- Privilegios Vehículos ---
    puede_ver_vehiculos = models.BooleanField(default=True, verbose_name='Ver Vehículos')
    puede_crear_vehiculos = models.BooleanField(default=False, verbose_name='Crear Vehículos')
    puede_editar_vehiculos = models.BooleanField(default=False, verbose_name='Editar Vehículos')
    puede_eliminar_vehiculos = models.BooleanField(default=False, verbose_name='Eliminar Vehículos')

    # --- Privilegios Órdenes de Trabajo ---
    puede_ver_ordenes = models.BooleanField(default=True, verbose_name='Ver Órdenes de Trabajo')
    puede_crear_ordenes = models.BooleanField(default=False, verbose_name='Crear Órdenes de Trabajo')
    puede_editar_ordenes = models.BooleanField(default=False, verbose_name='Editar Órdenes de Trabajo')
    puede_cambiar_estado_ordenes = models.BooleanField(default=False, verbose_name='Cambiar Estado de Órdenes')
    puede_eliminar_ordenes = models.BooleanField(default=False, verbose_name='Eliminar Órdenes de Trabajo')

    # --- Privilegios Inventario & Repuestos ---
    puede_ver_inventario = models.BooleanField(default=True, verbose_name='Ver Inventario & Repuestos')
    puede_crear_inventario = models.BooleanField(default=False, verbose_name='Crear Repuestos/Productos')
    puede_editar_inventario = models.BooleanField(default=False, verbose_name='Editar Repuestos/Productos')
    puede_eliminar_inventario = models.BooleanField(default=False, verbose_name='Eliminar Repuestos/Productos')
    puede_ajustar_stock = models.BooleanField(default=False, verbose_name='Ajustar / Registrar Entradas de Stock')

    # --- Privilegios Ventas & Comprobantes ---
    puede_ver_comprobantes = models.BooleanField(default=False, verbose_name='Ver Comprobantes')
    puede_crear_comprobantes = models.BooleanField(default=False, verbose_name='Emitir Comprobantes')
    puede_cobrar_comprobantes = models.BooleanField(default=False, verbose_name='Registrar Cobros / Pagos')
    puede_anular_comprobantes = models.BooleanField(default=False, verbose_name='Anular Comprobantes')

    # --- Privilegios Reportes & Métricas ---
    puede_ver_reportes = models.BooleanField(default=False, verbose_name='Ver Reportes & Analítica')
    puede_ver_cierre_diario = models.BooleanField(default=False, verbose_name='Ver Cierre Diario')

    # --- Privilegios Gestión y Seguridad ---
    puede_gestionar_usuarios = models.BooleanField(default=False, verbose_name='Gestionar Usuarios')
    puede_gestionar_roles = models.BooleanField(default=False, verbose_name='Gestionar Roles y Privilegios')
    puede_ver_auditoria = models.BooleanField(default=False, verbose_name='Ver Auditoría del Sistema')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuario'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, nombre_completo, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, nombre_completo=nombre_completo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, nombre_completo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        rol_dueno = Rol.objects.filter(codigo='DUENO').first()
        if rol_dueno:
            extra_fields.setdefault('rol', rol_dueno)
        return self.create_user(username, email, nombre_completo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, verbose_name='Usuario')
    email = models.EmailField(unique=True, verbose_name='Email')
    nombre_completo = models.CharField(max_length=150, verbose_name='Nombre completo')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios', verbose_name='Rol')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True, verbose_name='Foto')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_staff = models.BooleanField(default=False, verbose_name='Staff')
    date_joined = models.DateTimeField(default=timezone.now)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre_completo']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre_completo']

    def __str__(self):
        rol_nombre = self.rol.nombre if self.rol else 'Sin Rol'
        return f'{self.nombre_completo} ({rol_nombre})'

    def get_rol_display(self):
        return self.rol.nombre if self.rol else 'Sin Rol'

    def tiene_permiso(self, permiso_nombre):
        """Verifica de forma estricta si el usuario tiene asignado el privilegio requerido."""
        if self.is_superuser:
            return True
        if not self.rol:
            return False
        return getattr(self.rol, permiso_nombre, False)

    @property
    def es_dueno(self):
        if self.is_superuser:
            return True
        return bool(self.rol and self.rol.codigo == 'DUENO')

    @property
    def es_administrador(self):
        if self.is_superuser:
            return True
        return bool(self.rol and self.rol.codigo in ('ADMINISTRADOR', 'DUENO'))

    @property
    def es_mecanico(self):
        if self.is_superuser:
            return True
        return bool(self.rol and self.rol.codigo in ('MECANICO', 'ADMINISTRADOR', 'DUENO'))
