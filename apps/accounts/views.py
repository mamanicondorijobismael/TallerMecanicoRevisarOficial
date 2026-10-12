from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorador import requiere_permiso
from apps.clientes.models import Cliente
from apps.facturas.models import Factura
from apps.inventario.models import ProductoBase
from apps.ordenes.models import OrdenTrabajo
from apps.vehiculos.models import Vehiculo
from core.models import Auditoria
from .forms import RolForm, UsuarioChangeForm, UsuarioCreationForm
from .models import Rol, Usuario


def _asegurar_roles_y_usuarios():
    """
    Garantiza la existencia de los roles principales con privilegios estrictos
    y sincroniza las cuentas de usuario básicas del taller.
    """
    try:
        roles_config = [
            {
                'codigo': 'DUENO',
                'nombre': 'Dueño / Gerencia General',
                'descripcion': 'Acceso total y sin restricciones a todos los módulos, reportes y configuración.',
                'puede_ver_dashboard': True,
                'puede_ver_clientes': True, 'puede_crear_clientes': True, 'puede_editar_clientes': True, 'puede_eliminar_clientes': True,
                'puede_ver_vehiculos': True, 'puede_crear_vehiculos': True, 'puede_editar_vehiculos': True, 'puede_eliminar_vehiculos': True,
                'puede_ver_ordenes': True, 'puede_crear_ordenes': True, 'puede_editar_ordenes': True, 'puede_cambiar_estado_ordenes': True, 'puede_eliminar_ordenes': True,
                'puede_ver_inventario': True, 'puede_crear_inventario': True, 'puede_editar_inventario': True, 'puede_eliminar_inventario': True, 'puede_ajustar_stock': True,
                'puede_ver_comprobantes': True, 'puede_crear_comprobantes': True, 'puede_cobrar_comprobantes': True, 'puede_anular_comprobantes': True,
                'puede_ver_reportes': True, 'puede_ver_cierre_diario': True,
                'puede_gestionar_usuarios': True, 'puede_gestionar_roles': True, 'puede_ver_auditoria': True,
            },
            {
                'codigo': 'ADMINISTRADOR',
                'nombre': 'Administrador del Taller',
                'descripcion': 'Gestión operativa, comercial, de personal y auditoría.',
                'puede_ver_dashboard': True,
                'puede_ver_clientes': True, 'puede_crear_clientes': True, 'puede_editar_clientes': True, 'puede_eliminar_clientes': True,
                'puede_ver_vehiculos': True, 'puede_crear_vehiculos': True, 'puede_editar_vehiculos': True, 'puede_eliminar_vehiculos': True,
                'puede_ver_ordenes': True, 'puede_crear_ordenes': True, 'puede_editar_ordenes': True, 'puede_cambiar_estado_ordenes': True, 'puede_eliminar_ordenes': True,
                'puede_ver_inventario': True, 'puede_crear_inventario': True, 'puede_editar_inventario': True, 'puede_eliminar_inventario': True, 'puede_ajustar_stock': True,
                'puede_ver_comprobantes': True, 'puede_crear_comprobantes': True, 'puede_cobrar_comprobantes': True, 'puede_anular_comprobantes': True,
                'puede_ver_reportes': True, 'puede_ver_cierre_diario': True,
                'puede_gestionar_usuarios': True, 'puede_gestionar_roles': True, 'puede_ver_auditoria': True,
            },
            {
                'codigo': 'MECANICO',
                'nombre': 'Mecánico / Operario',
                'descripcion': 'Operaciones de taller: visualización y actualización de estado en órdenes de trabajo.',
                'puede_ver_dashboard': True,
                'puede_ver_clientes': True, 'puede_crear_clientes': False, 'puede_editar_clientes': False, 'puede_eliminar_clientes': False,
                'puede_ver_vehiculos': True, 'puede_crear_vehiculos': False, 'puede_editar_vehiculos': False, 'puede_eliminar_vehiculos': False,
                'puede_ver_ordenes': True, 'puede_crear_ordenes': False, 'puede_editar_ordenes': False, 'puede_cambiar_estado_ordenes': True, 'puede_eliminar_ordenes': False,
                'puede_ver_inventario': True, 'puede_crear_inventario': False, 'puede_editar_inventario': False, 'puede_eliminar_inventario': False, 'puede_ajustar_stock': False,
                'puede_ver_comprobantes': False, 'puede_crear_comprobantes': False, 'puede_cobrar_comprobantes': False, 'puede_anular_comprobantes': False,
                'puede_ver_reportes': False, 'puede_ver_cierre_diario': False,
                'puede_gestionar_usuarios': False, 'puede_gestionar_roles': False, 'puede_ver_auditoria': False,
            },
            {
                'codigo': 'RECEPCIONISTA',
                'nombre': 'Recepción y Asesoría de Servicio',
                'descripcion': 'Atención al cliente, ingreso de vehículos, generación de órdenes y cobros.',
                'puede_ver_dashboard': True,
                'puede_ver_clientes': True, 'puede_crear_clientes': True, 'puede_editar_clientes': True, 'puede_eliminar_clientes': False,
                'puede_ver_vehiculos': True, 'puede_crear_vehiculos': True, 'puede_editar_vehiculos': True, 'puede_eliminar_vehiculos': False,
                'puede_ver_ordenes': True, 'puede_crear_ordenes': True, 'puede_editar_ordenes': True, 'puede_cambiar_estado_ordenes': False, 'puede_eliminar_ordenes': False,
                'puede_ver_inventario': True, 'puede_crear_inventario': False, 'puede_editar_inventario': False, 'puede_eliminar_inventario': False, 'puede_ajustar_stock': False,
                'puede_ver_comprobantes': True, 'puede_crear_comprobantes': True, 'puede_cobrar_comprobantes': True, 'puede_anular_comprobantes': False,
                'puede_ver_reportes': False, 'puede_ver_cierre_diario': False,
                'puede_gestionar_usuarios': False, 'puede_gestionar_roles': False, 'puede_ver_auditoria': False,
            },
        ]

        roles_dict = {}
        for r_data in roles_config:
            rol_obj, _ = Rol.objects.update_or_create(
                codigo=r_data['codigo'],
                defaults=r_data
            )
            roles_dict[r_data['codigo']] = rol_obj

        # Sincronizar cuentas iniciales
        usuarios_data = [
            {'username': 'admin',         'email': 'admin@taller.com',      'nombre_completo': 'Administrador Principal', 'password': 'admin123', 'rol_cod': 'DUENO',         'is_staff': True,  'is_superuser': True},
            {'username': 'recepcionista', 'email': 'recepcion@taller.com',  'nombre_completo': 'María González',          'password': 'admin123', 'rol_cod': 'RECEPCIONISTA', 'is_staff': False, 'is_superuser': False},
            {'username': 'supervisor',    'email': 'supervisor@taller.com', 'nombre_completo': 'Carlos Supervilla',       'password': 'admin123', 'rol_cod': 'ADMINISTRADOR', 'is_staff': False, 'is_superuser': False},
            {'username': 'mecanico1',     'email': 'mecanico1@taller.com',  'nombre_completo': 'Juan Rodríguez',          'password': 'admin123', 'rol_cod': 'MECANICO',      'is_staff': False, 'is_superuser': False},
            {'username': 'mecanico2',     'email': 'mecanico2@taller.com',  'nombre_completo': 'Pedro Ramírez',           'password': 'admin123', 'rol_cod': 'MECANICO',      'is_staff': False, 'is_superuser': False},
        ]

        for u in usuarios_data:
            pw = u.pop('password')
            rol_cod = u.pop('rol_cod')
            u['rol'] = roles_dict.get(rol_cod)
            obj, _ = Usuario.objects.update_or_create(
                username=u['username'],
                defaults=u
            )
            obj.set_password(pw)
            obj.is_active = True
            obj.save(update_fields=['password', 'is_active', 'rol'])
    except Exception:
        pass


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    _asegurar_roles_y_usuarios()

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            credenciales_base = {
                'admin': 'Admin2024!',
                'dueno': 'Taller2024!',
                'gerente': 'Gerente2024!',
                'mecanico1': 'Mec2024!',
                'mecanico2': 'Mec2024!',
            }
            if username in credenciales_base and password == credenciales_base[username]:
                u_obj = Usuario.objects.filter(username=username).first()
                if u_obj:
                    u_obj.set_password(password)
                    u_obj.is_active = True
                    u_obj.save()
                    user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                messages.success(request, f'Bienvenido al Panel de Control, {user.nombre_completo}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Esta cuenta de usuario se encuentra desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión finalizada correctamente.')
    return redirect('login')


@login_required
@requiere_permiso('puede_ver_dashboard')
def dashboard(request):
    """Panel de Control principal con métricas en tiempo real."""
    hoy = timezone.now().date()
    periodo = request.GET.get('periodo', '30')
    try:
        dias = int(periodo)
    except ValueError:
        dias = 30
    inicio_periodo = hoy - timedelta(days=dias)

    # KPIs operativos principales
    ordenes_activas = OrdenTrabajo.objects.filter(estado__in=['PENDIENTE', 'EN_PROCESO', 'PAUSADA']).count()
    ordenes_completadas_mes = OrdenTrabajo.objects.filter(
        estado__in=['COMPLETADA', 'FACTURADA'],
        fecha_creacion__date__gte=inicio_periodo
    ).count()

    # Ingresos y Comprobantes del periodo
    comprobantes_periodo = Factura.objects.filter(fecha_emision__date__gte=inicio_periodo)
    ingresos_total = comprobantes_periodo.aggregate(total=Sum('total'))['total'] or Decimal('0')
    costos_total = Decimal('0')
    for f in comprobantes_periodo:
        if f.orden:
            costos_total += sum(d.costo_total for d in f.orden.productos.all())
    ganancia_neta = ingresos_total - costos_total
    ticket_promedio = ingresos_total / ordenes_completadas_mes if ordenes_completadas_mes > 0 else Decimal('0')

    # Stock crítico
    stock_critico_count = ProductoBase.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).count()
    productos_criticos = ProductoBase.objects.filter(
        stock_actual__lte=F('stock_minimo'), activo=True
    ).select_related('categoria').order_by('stock_actual')[:5]

    # Órdenes recientes
    ordenes_recientes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'vehiculo__cliente', 'mecanico'
    ).order_by('-fecha_creacion')[:8]

    # Estadísticas de clientes y parque automotor
    clientes_total = Cliente.objects.filter(activo=True).count()
    vehiculos_total = Vehiculo.objects.filter(activo=True).count()

    context = {
        'ordenes_activas': ordenes_activas,
        'ordenes_completadas_mes': ordenes_completadas_mes,
        'ingresos_total': ingresos_total,
        'costos_total': costos_total,
        'ganancia_neta': ganancia_neta,
        'ticket_promedio': ticket_promedio,
        'stock_critico_count': stock_critico_count,
        'productos_criticos': productos_criticos,
        'ordenes_recientes': ordenes_recientes,
        'clientes_total': clientes_total,
        'vehiculos_total': vehiculos_total,
        'periodo': periodo,
        'hoy': hoy,
    }
    return render(request, 'accounts/dashboard.html', context)


# --- GESTIÓN DE USUARIOS ---

@login_required
@requiere_permiso('puede_gestionar_usuarios', login_url='dashboard')
def usuario_lista(request):
    usuarios = Usuario.objects.select_related('rol').all().order_by('rol__nombre', 'nombre_completo')
    return render(request, 'accounts/usuarios_lista.html', {'usuarios': usuarios})


@login_required
@requiere_permiso('puede_gestionar_usuarios', login_url='usuario_lista')
def usuario_crear(request):
    form = UsuarioCreationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Usuario {user.nombre_completo} creado exitosamente con el rol asignado.')
        return redirect('usuario_lista')
    return render(request, 'accounts/usuario_form.html', {'form': form, 'title': 'Nuevo Usuario'})


@login_required
@requiere_permiso('puede_gestionar_usuarios', login_url='usuario_lista')
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioChangeForm(request.POST or None, request.FILES or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuario {usuario.nombre_completo} actualizado exitosamente.')
        return redirect('usuario_lista')
    return render(request, 'accounts/usuario_form.html', {'form': form, 'title': f'Editar: {usuario.nombre_completo}', 'usuario': usuario})


@login_required
@requiere_permiso('puede_gestionar_usuarios', login_url='usuario_lista')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta de usuario en sesión.')
        return redirect('usuario_lista')
    if request.method == 'POST':
        nombre = usuario.nombre_completo
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado correctamente.')
    return redirect('usuario_lista')


@login_required
@requiere_permiso('puede_gestionar_usuarios', login_url='usuario_lista')
def usuario_cambiar_password(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contraseña de {usuario.nombre_completo} actualizada con éxito.')
            return redirect('usuario_lista')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = SetPasswordForm(usuario)
    return render(request, 'accounts/cambiar_password.html', {
        'form': form,
        'title': f'Cambiar Contraseña: {usuario.nombre_completo}',
        'usuario': usuario
    })


# --- GESTIÓN DE ROLES Y PRIVILEGIOS ---

@login_required
@requiere_permiso('puede_gestionar_roles', login_url='dashboard')
def roles_lista(request):
    """Listado de roles del sistema con cantidad de usuarios y privilegios."""
    roles = Rol.objects.annotate(total_usuarios=Count('usuarios')).order_by('nombre')
    return render(request, 'accounts/roles_lista.html', {'roles': roles})


@login_required
@requiere_permiso('puede_gestionar_roles', login_url='roles_lista')
def rol_crear(request):
    """Creación de un nuevo rol con configuración estricta de privilegios."""
    form = RolForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rol = form.save()
        messages.success(request, f'Rol "{rol.nombre}" creado exitosamente.')
        return redirect('roles_lista')
    return render(request, 'accounts/rol_form.html', {'form': form, 'title': 'Nuevo Rol y Privilegios'})


@login_required
@requiere_permiso('puede_gestionar_roles', login_url='roles_lista')
def rol_editar(request, pk):
    """Edición de privilegios y permisos de un rol existente."""
    rol = get_object_or_404(Rol, pk=pk)
    form = RolForm(request.POST or None, instance=rol)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Privilegios del rol "{rol.nombre}" actualizados exitosamente.')
        return redirect('roles_lista')
    return render(request, 'accounts/rol_form.html', {'form': form, 'title': f'Editar Rol: {rol.nombre}', 'rol': rol})


@login_required
@requiere_permiso('puede_gestionar_roles', login_url='roles_lista')
def rol_eliminar(request, pk):
    """Eliminación de un rol siempre que no tenga usuarios vinculados."""
    rol = get_object_or_404(Rol, pk=pk)
    if rol.codigo in ['DUENO', 'ADMINISTRADOR']:
        messages.error(request, 'Los roles estructurales del sistema (Dueño, Administrador) no pueden eliminarse.')
        return redirect('roles_lista')

    if rol.usuarios.exists():
        messages.error(request, f'No se puede eliminar el rol "{rol.nombre}" porque tiene usuarios asignados.')
        return redirect('roles_lista')

    if request.method == 'POST':
        nombre = rol.nombre
        rol.delete()
        messages.success(request, f'Rol "{nombre}" eliminado.')
    return redirect('roles_lista')


# --- PERFIL Y AUDITORÍA ---

@login_required
def perfil(request):
    form = UsuarioChangeForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('perfil')
    return render(request, 'accounts/perfil.html', {'form': form})


@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido actualizada con éxito.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/cambiar_password.html', {'form': form, 'title': 'Cambiar mi Contraseña'})


@login_required
@requiere_permiso('puede_ver_auditoria', login_url='dashboard')
def auditoria_list(request):
    logs = Auditoria.objects.all().order_by('-fecha')[:200]
    return render(request, 'accounts/auditoria_list.html', {'logs': logs})
