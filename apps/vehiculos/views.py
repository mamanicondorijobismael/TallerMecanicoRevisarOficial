from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehiculo
from .forms import VehiculoForm
from core.models import Auditoria

from django.db.models import RestrictedError, ProtectedError    
@login_required
def vehiculo_list(request):
    query = request.GET.get('q', '')
    # Auto-recuperar vehículos sin órdenes que quedaron inactivos por el formulario anterior
    Vehiculo.objects.filter(activo=False, ordenes__isnull=True, reservas__isnull=True).update(activo=True)
    qs = Vehiculo.objects.select_related('cliente').filter(activo=True)
    
    if query:
        qs = qs.filter(
            Q(placa__icontains=query) | Q(marca__icontains=query) |
            Q(modelo__icontains=query) | Q(cliente__nombre_razon_social__icontains=query)
        )
        
    from apps.clientes.models import Cliente
    clientes = Cliente.objects.filter(activo=True).order_by('nombre_razon_social')
    return render(request, 'vehiculos/lista.html', {'vehiculos': qs, 'query': query, 'clientes': clientes})


@login_required
def vehiculo_detalle(request, pk):
    vehiculo = get_object_or_404(Vehiculo.objects.select_related('cliente'), pk=pk)
    ordenes = vehiculo.ordenes.select_related('mecanico').order_by('-fecha_creacion')
    return render(request, 'vehiculos/detalle.html', {'vehiculo': vehiculo, 'ordenes': ordenes})


@login_required
def vehiculo_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para registrar vehiculos.')
        return redirect('vehiculos:lista')
    from apps.clientes.models import Cliente
    cliente_id = request.GET.get('cliente_id')
    initial = {}
    
    if cliente_id:
        initial['cliente'] = cliente_id
    
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
            for field, errs in form.errors.items():
                messages.error(request, f'Error en {field}: {errs[0]}')
            return redirect('vehiculos:lista')
    
    form = VehiculoForm(initial=initial)
    return render(request, 'vehiculos/form.html', {'form': form, 'title': 'Nuevo Vehículo'})


@login_required
def vehiculo_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para editar vehiculos.')
        return redirect('vehiculos:lista')
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, request.FILES or None, instance=vehiculo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Vehiculo {vehiculo.placa} actualizado.')
        return redirect('vehiculos:detalle', pk=vehiculo.pk)
    return render(request, 'vehiculos/form.html', {'form': form, 'title': f'Editar: {vehiculo.placa}', 'vehiculo': vehiculo})

@login_required
def vehiculo_eliminar(request, pk):
    
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar o desactivar vehículos.')
        return redirect('vehiculos:lista')
    
    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para esta acción.')
        return redirect('vehiculos:lista')

    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    placa = vehiculo.placa
    cliente_nombre = vehiculo.cliente.nombre_razon_social if vehiculo.cliente else 'Sin cliente'

    # 3. Comprobar si existen relaciones registradas (Órdenes o Reservas)
    tiene_ordenes = hasattr(vehiculo, 'ordenes') and vehiculo.ordenes.exists()
    tiene_reservas = hasattr(vehiculo, 'reservas') and vehiculo.reservas.exists()

    try:
        if tiene_ordenes or tiene_reservas:
            # Soft Delete: Desactivación lógica para no romper el historial operativo ni financiero
            vehiculo.activo = False
            vehiculo.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'El vehículo {placa} posee historial en el taller (órdenes/turnos), por lo que fue desactivado del parque automotor.'
        else:
            # Hard Delete: Borrado físico si no posee registros vinculados
            vehiculo.delete()
            accion_audit = 'ELIMINAR'
            mensaje = f'El vehículo {placa} fue eliminado exitosamente.'

        # 4. Registro transparente en Auditoría
        Auditoria.objects.create(
            tabla='Vehiculo',
            registro_id=pk,
            accion=accion_audit,
            usuario=request.user.username,
            valores_anteriores={'placa': placa, 'cliente': cliente_nombre},
        )
        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        # Captura de seguridad si la BD frena la eliminación física
        vehiculo.activo = False
        vehiculo.save()
        messages.warning(
            request, 
            f'El vehículo {placa} no pudo eliminarse permanentemente por registros asociados, pero se desactivó del parque automotor.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('vehiculos:lista')