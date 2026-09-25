from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


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
        extra_fields.setdefault('rol', 'DUENO')
        return self.create_user(username, email, nombre_completo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    class Rol(models.TextChoices):
        DUENO = 'DUENO', 'Dueno'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        MECANICO = 'MECANICO', 'Mecanico'

    username = models.CharField(max_length=50, unique=True, verbose_name='Usuario')
    email = models.EmailField(unique=True, verbose_name='Email')
    nombre_completo = models.CharField(max_length=150, verbose_name='Nombre completo')
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.MECANICO, verbose_name='Rol')
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
        return f'{self.nombre_completo} ({self.get_rol_display()})'

    @property
    def es_dueno(self):
        return self.rol == 'DUENO' or self.is_superuser

    @property
    def es_administrador(self):
        return self.rol in ('ADMINISTRADOR', 'DUENO') or self.is_superuser

    @property
    def es_mecanico(self):
        return True  # All roles can do mechanic tasks
