from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, RestrictedError, ProtectedError
from .models import Cliente
from .forms import ClienteForm
from apps.accounts.decorador import requiere_permiso


@login_required
@requiere_permiso('puede_ver_clientes')
def cliente_list(request):
    query = request.GET.get('q', '').strip()
    qs = Cliente.objects.filter(activo=True)
    if query:
        qs = qs.filter(Q(nombre_razon_social__icontains=query) | Q(documento__icontains=query) | Q(email__icontains=query))
    return render(request, 'clientes/lista.html', {'clientes': qs, 'query': query})


@login_required
@requiere_permiso('puede_ver_clientes')
def cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    vehiculos = cliente.vehiculos.all().order_by('-fecha_creacion')
    
    from apps.ordenes.models import OrdenTrabajo
    from apps.recibos.models import Recibo
    
    ordenes = OrdenTrabajo.objects.filter(vehiculo__cliente=cliente).select_related('vehiculo').order_by('-fecha_creacion')
    recibos = Recibo.objects.filter(cliente=cliente).order_by('-fecha_emision')
    
    return render(request, 'clientes/detalle.html', {
        'cliente': cliente, 
        'vehiculos': vehiculos,
        'ordenes': ordenes,
        'recibos': recibos
    })


@login_required
@requiere_permiso('puede_crear_clientes', login_url='clientes:lista')
def cliente_crear(request):
    form = ClienteForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        cliente = form.save(commit=False)
        cliente.activo = True
        cliente.save()
        messages.success(request, f'Cliente {cliente.nombre_razon_social} creado exitosamente.')
        return redirect('clientes:detalle', pk=cliente.pk)
    return render(request, 'clientes/form.html', {'form': form, 'title': 'Nuevo Cliente'})


@login_required
@requiere_permiso('puede_editar_clientes', login_url='clientes:lista')
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    valores_anteriores = {'nombre': cliente.nombre_razon_social, 'documento': cliente.documento}
    form = ClienteForm(request.POST or None, request.FILES or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Cliente {cliente.nombre_razon_social} actualizado.')
        return redirect('clientes:detalle', pk=cliente.pk)
    return render(request, 'clientes/form.html', {'form': form, 'title': f'Editar: {cliente.nombre_razon_social}', 'cliente': cliente})


@login_required
@requiere_permiso('puede_eliminar_clientes', login_url='clientes:lista')
def cliente_eliminar(request, pk):
    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para esta acción.')
        return redirect('clientes:lista')

    cliente = get_object_or_404(Cliente, pk=pk)
    nombre = cliente.nombre_razon_social
    tiene_vehiculos = cliente.vehiculos.exists()
    tiene_recibos = hasattr(cliente, 'recibos') and cliente.recibos.exists()

    try:
        if tiene_vehiculos or tiene_recibos:
            cliente.activo = False
            cliente.save(update_fields=['activo'])
            cliente.vehiculos.all().update(activo=False)
            mensaje = f'El cliente "{nombre}" posee historial (vehículos/recibos), por lo que fue desactivado junto con sus vehículos vinculados.'
        else:
            cliente.delete()
            mensaje = f'El cliente "{nombre}" fue eliminado exitosamente.'

        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        cliente.activo = False
        cliente.save(update_fields=['activo'])
        cliente.vehiculos.all().update(activo=False)
        messages.warning(
            request,
            f'El cliente "{nombre}" no pudo eliminarse por registros asociados, pero fue desactivado con sus vehículos.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('clientes:lista')
