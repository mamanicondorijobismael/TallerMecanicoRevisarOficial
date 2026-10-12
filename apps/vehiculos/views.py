from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, RestrictedError, ProtectedError

from .models import Vehiculo
from .forms import VehiculoForm
from apps.clientes.models import Cliente
from apps.accounts.decorador import requiere_permiso
from core.models import Auditoria


@login_required
@requiere_permiso('puede_ver_vehiculos')
def vehiculo_list(request):
    query = request.GET.get('q', '').strip()
    qs = Vehiculo.objects.select_related('cliente').filter(activo=True)
    
    if query:
        qs = qs.filter(
            Q(placa__icontains=query) | 
            Q(marca__icontains=query) |
            Q(modelo__icontains=query) | 
            Q(cliente__nombre_razon_social__icontains=query)
        )
        
    clientes = Cliente.objects.filter(activo=True).order_by('nombre_razon_social')
    return render(request, 'vehiculos/lista.html', {
        'vehiculos': qs, 
        'query': query, 
        'clientes': clientes
    })


@login_required
@requiere_permiso('puede_ver_vehiculos')
def vehiculo_detalle(request, pk):
    """
    Ficha técnica del vehículo y su historial de órdenes de trabajo.
    """
    vehiculo = get_object_or_404(Vehiculo.objects.select_related('cliente'), pk=pk)
    ordenes = vehiculo.ordenes.select_related('mecanico').order_by('-fecha_creacion')
    return render(request, 'vehiculos/detalle.html', {
        'vehiculo': vehiculo, 
        'ordenes': ordenes
    })


@login_required
@requiere_permiso('puede_crear_vehiculos', login_url='vehiculos:lista')
def vehiculo_crear(request):
    """
    Registro de un nuevo vehículo en el sistema.
    Restringido por privilegio 'puede_crear_vehiculos'.
    """
    cliente_id = request.GET.get('cliente_id')
    initial = {'cliente': cliente_id} if cliente_id else {}
    
    if request.method == 'POST':
        data = request.POST.copy()
        if 'patente' in data and not data.get('placa'):
            data['placa'] = data.get('patente')
            
        form = VehiculoForm(data, request.FILES or None, initial=initial)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.activo = True
            vehiculo.save()
            messages.success(request, f'Vehículo {vehiculo.placa} registrado exitosamente.')
            return redirect('vehiculos:detalle', pk=vehiculo.pk)
        else:
            messages.error(request, 'Por favor corrige los errores resaltados en el formulario.')
            return render(request, 'vehiculos/form.html', {
                'form': form, 
                'title': 'Nuevo Vehículo'
            })
    
    form = VehiculoForm(initial=initial)
    return render(request, 'vehiculos/form.html', {
        'form': form, 
        'title': 'Nuevo Vehículo'
    })


@login_required
@requiere_permiso('puede_editar_vehiculos', login_url='vehiculos:lista')
def vehiculo_editar(request, pk):
    """
    Edición de datos del vehículo.
    Restringido por privilegio 'puede_editar_vehiculos'.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, request.FILES or None, instance=vehiculo)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehículo {vehiculo.placa} actualizado exitosamente.')
            return redirect('vehiculos:detalle', pk=vehiculo.pk)
        else:
            messages.error(request, 'Por favor corrige los errores resaltados en el formulario.')

    return render(request, 'vehiculos/form.html', {
        'form': form, 
        'title': f'Editar: {vehiculo.placa}', 
        'vehiculo': vehiculo
    })


@login_required
@requiere_permiso('puede_eliminar_vehiculos', login_url='vehiculos:lista')
def vehiculo_eliminar(request, pk):
    """
    Eliminación física o deshabilitación lógica (Soft Delete) según historial del vehículo.
    Restringido por privilegio 'puede_eliminar_vehiculos'.
    """
    if request.method != 'POST':
        messages.warning(request, 'Método de petición no permitido para esta acción.')
        return redirect('vehiculos:lista')

    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    placa = vehiculo.placa
    cliente_nombre = vehiculo.cliente.nombre_razon_social if vehiculo.cliente else 'Sin cliente'

    tiene_ordenes = hasattr(vehiculo, 'ordenes') and vehiculo.ordenes.exists()

    try:
        if tiene_ordenes:
            vehiculo.activo = False
            vehiculo.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'El vehículo {placa} posee historial operativo, por lo que fue desactivado del parque automotor.'
        else:
            vehiculo.delete()
            accion_audit = 'ELIMINAR'
            mensaje = f'El vehículo {placa} fue eliminado exitosamente.'

        Auditoria.objects.create(
            tabla='Vehiculo',
            registro_id=pk,
            accion=accion_audit,
            usuario=request.user.username,
            valores_anteriores={'placa': placa, 'cliente': cliente_nombre},
        )
        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        vehiculo.activo = False
        vehiculo.save()
        messages.warning(
            request, 
            f'El vehículo {placa} no pudo eliminarse permanentemente por registros asociados, pero se desactivó.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('vehiculos:lista')