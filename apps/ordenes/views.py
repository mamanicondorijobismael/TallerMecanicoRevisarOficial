from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto
from .forms import OrdenTrabajoForm, DetalleServicioForm, DetalleProductoForm


@login_required
def orden_list(request):
    estado_filter = request.GET.get('estado', '')
    query = request.GET.get('q', '')
    qs = OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico').order_by('-fecha_creacion')
    if estado_filter:
        qs = qs.filter(estado=estado_filter)
    if query:
        qs = qs.filter(
            Q(numero_orden__icontains=query) | Q(vehiculo__patente__icontains=query) |
            Q(vehiculo__cliente__nombre_razon_social__icontains=query)
        )
    from apps.vehiculos.models import Vehiculo
    from apps.accounts.models import Usuario
    vehiculos = Vehiculo.objects.filter(activo=True).select_related('cliente').order_by('patente')
    mecanicos = Usuario.objects.filter(is_active=True).order_by('nombre_completo', 'username')
    estados = OrdenTrabajo.Estado.choices
    return render(request, 'ordenes/lista.html', {
        'ordenes': qs, 'query': query, 'estado_filter': estado_filter, 'estados': estados,
        'vehiculos': vehiculos, 'mecanicos': mecanicos
    })


@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico'), pk=pk)
    servicios = orden.servicios.all()
    productos = orden.productos.select_related('producto').all()
    form_servicio = DetalleServicioForm()
    form_producto = DetalleProductoForm()
    return render(request, 'ordenes/detalle.html', {
        'orden': orden, 'servicios': servicios, 'productos': productos,
        'form_servicio': form_servicio, 'form_producto': form_producto,
    })


@login_required
def orden_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para crear órdenes.')
        return redirect('ordenes:lista')
    if request.method == 'POST':
        # Procesar creación manual desde el modal (campos name="vehiculo", "mecanico", etc.)
        from apps.vehiculos.models import Vehiculo
        from apps.accounts.models import Usuario
        vehiculo_id = request.POST.get('vehiculo')
        mecanico_id = request.POST.get('mecanico') or None
        kilometraje_val = request.POST.get('kilometraje') or 0
        diagnostico_val = request.POST.get('diagnostico', '')
        observaciones_val = request.POST.get('observaciones', '')
        fecha_prometida_val = request.POST.get('fecha_prometida') or None

        try:
            vehiculo = Vehiculo.objects.get(pk=vehiculo_id)
        except (Vehiculo.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Debe seleccionar un vehículo válido.')
            return redirect('ordenes:lista')

        mecanico = None
        if mecanico_id:
            try:
                mecanico = Usuario.objects.get(pk=mecanico_id)
            except (Usuario.DoesNotExist, ValueError):
                pass

        # Procesar fecha
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

        # Actualizar odómetro del vehículo
        if orden.kilometraje and orden.kilometraje > vehiculo.kilometraje_actual:
            vehiculo.kilometraje_actual = orden.kilometraje
            vehiculo.save()

        messages.success(request, f'Orden #{orden.numero_orden} creada exitosamente.')
        return redirect('ordenes:detalle', pk=orden.pk)

    # GET: renderizar formulario standalone
    form = OrdenTrabajoForm()
    return render(request, 'ordenes/form.html', {'form': form, 'title': 'Nueva Orden de Trabajo'})


@login_required
def orden_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para editar órdenes.')
        return redirect('ordenes:detalle', pk=pk)
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['FACTURADA', 'CANCELADA']:
        messages.error(request, 'No se puede editar una orden facturada o cancelada.')
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
def orden_cambiar_estado(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if orden.puede_transicionar(nuevo_estado):
            orden.estado = nuevo_estado
            if nuevo_estado == 'COMPLETADA':
                orden.fecha_cierre = timezone.now()
                # Descontar stock automaticamente
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
def eliminar_servicio(request, pk, spk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar items de la orden.')
        return redirect('ordenes:detalle', pk=pk)
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['FACTURADA', 'CANCELADA']:
        DetalleServicio.objects.filter(pk=spk, orden=orden).delete()
        messages.success(request, 'Servicio eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
def eliminar_producto(request, pk, ppk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar items de la orden.')
        return redirect('ordenes:detalle', pk=pk)
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['FACTURADA', 'CANCELADA']:
        DetalleProducto.objects.filter(pk=ppk, orden=orden).delete()
        messages.success(request, 'Producto eliminado.')
    return redirect('ordenes:detalle', pk=pk)
