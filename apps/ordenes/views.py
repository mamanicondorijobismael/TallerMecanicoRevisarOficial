from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, RestrictedError, ProtectedError
from django.utils import timezone
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto, RepuestoExterno
from .forms import OrdenTrabajoForm, DetalleServicioForm, DetalleProductoForm, RepuestoExternoForm
from apps.accounts.decorador import requiere_permiso
from core.models import Auditoria


@login_required
@requiere_permiso('puede_ver_ordenes')
def orden_list(request):
    estado_filter = request.GET.get('estado', '')
    query = request.GET.get('q', '').strip()
    qs = OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico').order_by('-fecha_creacion')
    if estado_filter:
        qs = qs.filter(estado=estado_filter)
    if query:
        qs = qs.filter(
            Q(numero_orden__icontains=query) | Q(vehiculo__placa__icontains=query) |
            Q(vehiculo__cliente__nombre_razon_social__icontains=query)
        )
    from apps.vehiculos.models import Vehiculo
    from apps.accounts.models import Usuario
    vehiculos = Vehiculo.objects.filter(activo=True).select_related('cliente').order_by('placa')
    mecanicos = Usuario.objects.filter(is_active=True).order_by('nombre_completo', 'username')
    estados = OrdenTrabajo.Estado.choices
    return render(request, 'ordenes/lista.html', {
        'ordenes': qs, 'query': query, 'estado_filter': estado_filter, 'estados': estados,
        'vehiculos': vehiculos, 'mecanicos': mecanicos
    })


@login_required
@requiere_permiso('puede_ver_ordenes')
def orden_detalle(request, pk):
    orden = get_object_or_404(OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico'), pk=pk)
    servicios = orden.servicios.all()
    productos = orden.productos.select_related('producto').all()
    repuestos_externos = orden.repuestos_externos.all()
    form_servicio = DetalleServicioForm()
    form_producto = DetalleProductoForm()
    form_repuesto_externo = RepuestoExternoForm()
    return render(request, 'ordenes/detalle.html', {
        'orden': orden, 'servicios': servicios, 'productos': productos, 'repuestos_externos': repuestos_externos,
        'form_servicio': form_servicio, 'form_producto': form_producto, 'form_repuesto_externo': form_repuesto_externo,
    })


@login_required
@requiere_permiso('puede_crear_ordenes', login_url='ordenes:lista')
def orden_crear(request):
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.creado_por = request.user
            if not orden.kilometraje and orden.vehiculo:
                orden.kilometraje = orden.vehiculo.kilometraje_actual
            orden.save()
            if orden.kilometraje and orden.vehiculo and orden.kilometraje > orden.vehiculo.kilometraje_actual:
                orden.vehiculo.kilometraje_actual = orden.kilometraje
                orden.vehiculo.save()
            messages.success(request, f'Orden #{orden.numero_orden} creada exitosamente.')
            return redirect('ordenes:detalle', pk=orden.pk)
        else:
            from apps.vehiculos.models import Vehiculo
            from apps.accounts.models import Usuario
            vehiculo_id = request.POST.get('vehiculo')
            try:
                vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
                mecanico_id = request.POST.get('mecanico')
                mecanico = Usuario.objects.filter(pk=mecanico_id).first() if mecanico_id else None
                kilometraje_val = request.POST.get('kilometraje')
                diagnostico_val = request.POST.get('diagnostico', '')
                observaciones_val = request.POST.get('observaciones', '')
                fecha_prometida_val = request.POST.get('fecha_prometida') or None
                fecha_prometida = None
                if fecha_prometida_val:
                    from django.utils.dateparse import parse_datetime
                    fecha_prometida = parse_datetime(fecha_prometida_val)

                orden = OrdenTrabajo.objects.create(
                    vehiculo=vehiculo,
                    mecanico=mecanico,
                    creado_por=request.user,
                    kilometraje=int(kilometraje_val) if kilometraje_val else vehiculo.kilometraje_actual,
                    diagnostico=diagnostico_val,
                    observaciones=observaciones_val,
                    fecha_prometida=fecha_prometida,
                )
                if orden.kilometraje and orden.kilometraje > vehiculo.kilometraje_actual:
                    vehiculo.kilometraje_actual = orden.kilometraje
                    vehiculo.save()
                messages.success(request, f'Orden #{orden.numero_orden} creada exitosamente.')
                return redirect('ordenes:detalle', pk=orden.pk)
            except Exception as e:
                for field, errs in form.errors.items():
                    messages.error(request, f'{field}: {errs[0]}')
                return redirect('ordenes:lista')

    # GET: renderizar formulario
    form = OrdenTrabajoForm()
    return render(request, 'ordenes/form.html', {'form': form, 'title': 'Nueva Orden de Trabajo'})


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def orden_editar(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['FACTURADA', 'CANCELADA']:
        messages.error(request, 'No se puede editar una orden con comprobante o cancelada.')
        return redirect('ordenes:detalle', pk=pk)
    form = OrdenTrabajoForm(request.POST or None, instance=orden)
    if request.method == 'POST' and form.is_valid():
        orden = form.save()
        vehiculo = orden.vehiculo
        if orden.kilometraje and orden.kilometraje > vehiculo.kilometraje_actual:
            vehiculo.kilometraje_actual = orden.kilometraje
            vehiculo.save()
        messages.success(request, f'Orden #{orden.numero_orden} actualizada exitosamente.')
        return redirect('ordenes:detalle', pk=orden.pk)
    return render(request, 'ordenes/form.html', {'form': form, 'title': f'Editar Orden #{orden.numero_orden}', 'orden': orden})


@login_required
@requiere_permiso('puede_cambiar_estado_ordenes', login_url='ordenes:lista')
def orden_cambiar_estado(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if orden.puede_transicionar(nuevo_estado):
            orden.estado = nuevo_estado
            if nuevo_estado == 'COMPLETADA':
                orden.fecha_cierre = timezone.now()
                # Descontar stock automáticamente
                for dp in orden.productos.all():
                    prod = dp.producto
                    if prod.stock_actual >= dp.cantidad:
                        prod.stock_actual -= dp.cantidad
                        prod.save()
                        from apps.inventario.models import MovimientoStock
                        MovimientoStock.objects.create(
                            producto=prod, orden=orden, tipo_movimiento='SALIDA',
                            cantidad=-dp.cantidad, stock_resultante=prod.stock_actual,
                            motivo=f'Consumo OT#{orden.numero_orden}', usuario=request.user.username,
                            precio_unitario=dp.precio_unitario
                        )
                    else:
                        messages.warning(request, f'Stock insuficiente para {prod.nombre}. Stock descontado parcialmente.')
            orden.save()
            messages.success(request, f'Estado cambiado a: {orden.get_estado_display()}')
        else:
            messages.error(request, f'No se puede cambiar de {orden.get_estado_display()} a ese estado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def agregar_servicio(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['FACTURADA', 'CANCELADA']:
        messages.error(request, 'No se puede modificar una orden cerrada.')
        return redirect('ordenes:detalle', pk=pk)
    form = DetalleServicioForm(request.POST)
    if form.is_valid():
        servicio = form.save(commit=False)
        servicio.orden = orden
        servicio.save()
        messages.success(request, 'Servicio agregado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def agregar_producto(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['FACTURADA', 'CANCELADA']:
        messages.error(request, 'No se puede modificar una orden cerrada.')
        return redirect('ordenes:detalle', pk=pk)
    form = DetalleProductoForm(request.POST)
    if form.is_valid():
        detalle = form.save(commit=False)
        detalle.orden = orden
        detalle.precio_unitario = detalle.producto.precio_venta
        detalle.save()
        messages.success(request, 'Producto agregado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def eliminar_servicio(request, pk, spk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['FACTURADA', 'CANCELADA']:
        DetalleServicio.objects.filter(pk=spk, orden=orden).delete()
        messages.success(request, 'Servicio eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def eliminar_producto(request, pk, ppk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['FACTURADA', 'CANCELADA']:
        DetalleProducto.objects.filter(pk=ppk, orden=orden).delete()
        messages.success(request, 'Producto eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def agregar_repuesto_externo(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['FACTURADA', 'CANCELADA']:
        messages.error(request, 'No se puede modificar una orden cerrada.')
        return redirect('ordenes:detalle', pk=pk)
    form = RepuestoExternoForm(request.POST)
    if form.is_valid():
        repuesto = form.save(commit=False)
        repuesto.orden = orden
        repuesto.save()
        messages.success(request, 'Repuesto externo agregado.')
    else:
        messages.error(request, 'Error al agregar repuesto externo. Verifique los datos.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def eliminar_repuesto_externo(request, pk, rpk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['FACTURADA', 'CANCELADA']:
        RepuestoExterno.objects.filter(pk=rpk, orden=orden).delete()
        messages.success(request, 'Repuesto externo eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_eliminar_ordenes', login_url='ordenes:lista')
def orden_eliminar(request, pk):
    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para esta acción.')
        return redirect('ordenes:lista')

    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    numero = orden.numero_orden
    placa = orden.vehiculo.placa
    cliente = orden.vehiculo.cliente.nombre_razon_social

    try:
        if orden.estado == 'FACTURADA':
            messages.error(request, f'La orden #{numero} tiene comprobante emitido y no puede eliminarse. Debe anularse el comprobante primero.')
            return redirect('ordenes:detalle', pk=pk)

        tiene_comprobante = hasattr(orden, 'factura')

        if tiene_comprobante:
            orden.estado = 'CANCELADA'
            orden.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'La orden #{numero} posee comprobante asociado, por lo que fue cancelada en lugar de eliminada.'
        elif orden.estado in ['PENDIENTE', 'CANCELADA']:
            orden.delete()
            accion_audit = 'ELIMINAR'
            mensaje = f'La orden #{numero} fue eliminada exitosamente.'
        else:
            orden.estado = 'CANCELADA'
            orden.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'La orden #{numero} fue cancelada. Las órdenes en proceso se cancelan para preservar el historial.'

        Auditoria.objects.create(
            tabla='OrdenTrabajo',
            registro_id=pk,
            accion=accion_audit,
            usuario=request.user.username,
            valores_anteriores={'numero_orden': numero, 'vehiculo': placa, 'cliente': cliente},
        )
        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        orden.estado = 'CANCELADA'
        orden.save()
        messages.warning(
            request,
            f'La orden #{numero} no pudo eliminarse permanentemente por registros asociados, pero fue cancelada.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('ordenes:lista')
