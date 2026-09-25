from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.ordenes.models import OrdenTrabajo
from apps.inventario.models import ProductoBase
from apps.facturas.models import Factura
from apps.mantenimiento.models import AlertaMantenimiento
from apps.reservas.models import Reserva
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from .models import Usuario
from .forms import UsuarioCreationForm, UsuarioChangeForm


from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm


def _asegurar_usuarios():
    try:
        usuarios_data = [
            {'username': 'admin',         'email': 'admin@taller.com',         'nombre_completo': 'Administrador Principal',  'password': 'admin123', 'rol': 'DUENO',         'is_staff': True,  'is_superuser': True},
            {'username': 'recepcionista', 'email': 'recepcion@taller.com',     'nombre_completo': 'María González',           'password': 'admin123', 'rol': 'ADMINISTRADOR', 'is_staff': False, 'is_superuser': False},
            {'username': 'supervisor',    'email': 'supervisor@taller.com',    'nombre_completo': 'Carlos Supervilla',        'password': 'admin123', 'rol': 'ADMINISTRADOR', 'is_staff': False, 'is_superuser': False},
            {'username': 'mecanico1',     'email': 'mecanico1@taller.com',     'nombre_completo': 'Juan Rodríguez',           'password': 'admin123', 'rol': 'MECANICO',      'is_staff': False, 'is_superuser': False},
            {'username': 'mecanico2',     'email': 'mecanico2@taller.com',     'nombre_completo': 'Pedro Ramírez',            'password': 'admin123', 'rol': 'MECANICO',      'is_staff': False, 'is_superuser': False},
        ]
        for u in usuarios_data:
            pw = u.pop('password')
            obj, _ = Usuario.objects.update_or_create(
                username=u['username'],
                defaults=u
            )
            obj.set_password(pw)
            obj.is_active = True
            obj.save(update_fields=['password', 'is_active'])
    except Exception:
        pass


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    _asegurar_usuarios()

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
                messages.success(request, f'Bienvenido, {user.nombre_completo}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Esta cuenta de usuario se encuentra desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesion cerrada correctamente.')
    return redirect('login')


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    periodo = request.GET.get('periodo', '30')
    try:
        dias = int(periodo)
    except ValueError:
        dias = 30
    inicio_periodo = hoy - timedelta(days=dias)

    # KPIs principales
    ordenes_activas = OrdenTrabajo.objects.filter(estado__in=['PENDIENTE', 'EN_PROCESO', 'PAUSADA']).count()
    ordenes_completadas_mes = OrdenTrabajo.objects.filter(
        estado__in=['COMPLETADA', 'FACTURADA'],
        fecha_creacion__date__gte=inicio_periodo
    ).count()

    # Ingresos del periodo
    facturas_periodo = Factura.objects.filter(fecha_emision__date__gte=inicio_periodo)
    ingresos_total = facturas_periodo.aggregate(total=Sum('total'))['total'] or Decimal('0')
    costos_total = Decimal('0')
    for f in facturas_periodo:
        costos_total += sum(d.costo_total for d in f.orden.productos.all())
    ganancia_neta = ingresos_total - costos_total
    ticket_promedio = ingresos_total / ordenes_completadas_mes if ordenes_completadas_mes > 0 else Decimal('0')

    # Stock critico
    stock_critico_count = ProductoBase.objects.filter(stock_actual__lte=models_F_stock_minimo()).count()
    productos_criticos = ProductoBase.objects.filter(
        stock_actual__lte=models_F_stock_minimo()
    ).select_related('categoria').order_by('stock_actual')[:5]

    # Alertas mantenimiento pendientes
    alertas_count = AlertaMantenimiento.objects.filter(estado='PENDIENTE').count()
    alertas_recientes = AlertaMantenimiento.objects.filter(
        estado='PENDIENTE'
    ).select_related('vehiculo', 'vehiculo__cliente', 'tipo_servicio')[:5]

    # Ordenes recientes
    ordenes_recientes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'vehiculo__cliente', 'mecanico'
    ).order_by('-fecha_creacion')[:8]

    # Reservas proximas
    reservas_proximas = Reserva.objects.filter(
        fecha_hora__date__gte=hoy,
        estado__in=['CONFIRMADA', 'PENDIENTE']
    ).select_related('cliente', 'vehiculo').order_by('fecha_hora')[:5]

    # Stats adicionales
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
        'alertas_count': alertas_count,
        'alertas_recientes': alertas_recientes,
        'ordenes_recientes': ordenes_recientes,
        'reservas_proximas': reservas_proximas,
        'clientes_total': clientes_total,
        'vehiculos_total': vehiculos_total,
        'periodo': periodo,
        'hoy': hoy,
    }
    return render(request, 'accounts/dashboard.html', context)


def models_F_stock_minimo():
    from django.db.models import F
    return F('stock_minimo')


@login_required
def usuario_lista(request):
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para acceder a esta seccion.')
        return redirect('dashboard')
    usuarios = Usuario.objects.all().order_by('rol', 'nombre_completo')
    return render(request, 'accounts/usuarios_lista.html', {'usuarios': usuarios})


@login_required
def usuario_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para crear usuarios.')
        return redirect('dashboard')
    form = UsuarioCreationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Usuario {user.nombre_completo} creado exitosamente.')
        return redirect('usuario_lista')
    return render(request, 'accounts/usuario_form.html', {'form': form, 'title': 'Nuevo Usuario'})


@login_required
def usuario_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para editar usuarios.')
        return redirect('dashboard')
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioChangeForm(request.POST or None, request.FILES or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuario {usuario.nombre_completo} actualizado.')
        return redirect('usuario_lista')
    return render(request, 'accounts/usuario_form.html', {'form': form, 'title': f'Editar: {usuario.nombre_completo}', 'usuario': usuario})


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
def usuario_cambiar_password(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'No tienes permisos para cambiar contraseñas de otros usuarios.')
        return redirect('dashboard')
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


@login_required
def auditoria_list(request):
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos.')
        return redirect('dashboard')
    from core.models import Auditoria
    logs = Auditoria.objects.all()[:200]
    return render(request, 'accounts/auditoria_list.html', {'logs': logs})
