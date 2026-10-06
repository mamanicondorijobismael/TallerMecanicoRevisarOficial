from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm
from core.models import Auditoria


@login_required
def cliente_list(request):
    query = request.GET.get('q', '')
    # Auto-recuperar clientes sin vehículos que quedaron inactivos por el formulario anterior
    Cliente.objects.filter(activo=False, vehiculos__isnull=True).update(activo=True)
    qs = Cliente.objects.filter(activo=True)
    if query:
        qs = qs.filter(Q(nombre_razon_social__icontains=query) | Q(documento__icontains=query) | Q(email__icontains=query))
    return render(request, 'clientes/lista.html', {'clientes': qs, 'query': query})


@login_required
def cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    vehiculos = cliente.vehiculos.all().order_by('-fecha_creacion')
    
    from apps.ordenes.models import OrdenTrabajo
    from apps.facturas.models import Factura
    
    ordenes = OrdenTrabajo.objects.filter(vehiculo__cliente=cliente).select_related('vehiculo').order_by('-fecha_creacion')
    facturas = Factura.objects.filter(cliente=cliente).order_by('-fecha_emision')
    
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente, 
        'vehiculos': vehiculos,
        'ordenes': ordenes,
        'facturas': facturas
    })


@login_required
def cliente_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para crear clientes.')
        return redirect('clientes:lista')
    form = ClienteForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        cliente = form.save(commit=False)
        cliente.activo = True
        cliente.save()
        Auditoria.objects.create(tabla='cliente', registro_id=cliente.pk, accion='CREAR',
                                 usuario=request.user.username, valores_nuevos={'nombre': cliente.nombre_razon_social})
        messages.success(request, f'Cliente {cliente.nombre_razon_social} creado exitosamente.')
        return redirect('clientes:detalle', pk=cliente.pk)
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Nuevo Cliente'})


@login_required
def cliente_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para editar clientes.')
        return redirect('clientes:lista')
    cliente = get_object_or_404(Cliente, pk=pk)
    valores_anteriores = {'nombre': cliente.nombre_razon_social, 'documento': cliente.documento}
    form = ClienteForm(request.POST or None, request.FILES or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        Auditoria.objects.create(tabla='cliente', registro_id=cliente.pk, accion='MODIFICAR',
                                 usuario=request.user.username, valores_anteriores=valores_anteriores)
        messages.success(request, f'Cliente {cliente.nombre_razon_social} actualizado.')
        return redirect('clientes:detalle', pk=cliente.pk)
    return render(request, 'clientes/form.html', {'form': form, 'title': f'Editar: {cliente.nombre_razon_social}', 'cliente': cliente})


from django.db.models import RestrictedError, ProtectedError

@login_required
def cliente_eliminar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar o desactivar clientes.')
        return redirect('clientes:lista')

    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para esta acción.')
        return redirect('clientes:lista')

    cliente = get_object_or_404(Cliente, pk=pk)
    nombre = cliente.nombre_razon_social
    documento = cliente.documento

    tiene_vehiculos = cliente.vehiculos.exists()
    tiene_facturas = hasattr(cliente, 'facturas') and cliente.facturas.exists()
    tiene_reservas = hasattr(cliente, 'reservas') and cliente.reservas.exists()

    try:
        if tiene_vehiculos or tiene_facturas or tiene_reservas:
            cliente.activo = False
            cliente.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'El cliente "{nombre}" posee historial (vehículos/facturas/reservas), por lo que fue desactivado del sistema.'
        else:
            cliente.delete()
            accion_audit = 'ELIMINAR'
            mensaje = f'El cliente "{nombre}" fue eliminado exitosamente.'

        Auditoria.objects.create(
            tabla='Cliente',
            registro_id=pk,
            accion=accion_audit,
            usuario=request.user.username,
            valores_anteriores={'nombre': nombre, 'documento': documento},
        )
        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        cliente.activo = False
        cliente.save()
        messages.warning(
            request,
            f'El cliente "{nombre}" no pudo eliminarse por registros asociados, pero fue desactivado.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('clientes:lista')
