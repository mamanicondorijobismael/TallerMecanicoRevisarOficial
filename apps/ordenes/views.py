from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, RestrictedError, ProtectedError
from django.utils import timezone
from django.http import JsonResponse
from .models import OrdenTrabajo, DetalleServicio, DetalleProducto, RepuestoExterno
from .forms import OrdenTrabajoForm, DetalleServicioForm, DetalleProductoForm, RepuestoExternoForm
from apps.accounts.decorador import requiere_permiso


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
    vehiculos = Vehiculo.objects.filter(activo=True, cliente__activo=True).select_related('cliente').order_by('placa')
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
@requiere_permiso('puede_ver_ordenes')
def orden_imprimir(request, pk):
    """Vista de impresión formal, profesional y minimalista de la Orden de Trabajo."""
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico'),
        pk=pk
    )
    servicios = orden.servicios.all()
    productos = orden.productos.select_related('producto').all()
    repuestos_externos = orden.repuestos_externos.all()
    return render(request, 'ordenes/imprimir.html', {
        'orden': orden,
        'servicios': servicios,
        'productos': productos,
        'repuestos_externos': repuestos_externos,
    })


@login_required
@requiere_permiso('puede_crear_ordenes', login_url='ordenes:lista')
def orden_crear(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    initial = {}
    if vehiculo_id:
        from apps.vehiculos.models import Vehiculo
        v_obj = Vehiculo.objects.filter(pk=vehiculo_id, activo=True, cliente__activo=True).first()
        if v_obj:
            initial = {'vehiculo': v_obj.pk, 'kilometraje': v_obj.kilometraje_actual}
        else:
            messages.warning(request, 'El vehículo indicado no existe o se encuentra deshabilitado.')

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
            messages.error(request, 'Por favor corrige los errores del formulario.')
            return render(request, 'ordenes/form.html', {'form': form, 'title': 'Nueva Orden de Trabajo'})

    # GET: renderizar formulario con valores iniciales
    form = OrdenTrabajoForm(initial=initial)
    return render(request, 'ordenes/form.html', {'form': form, 'title': 'Nueva Orden de Trabajo'})


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def orden_editar(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['COBRADA', 'CANCELADA']:
        messages.error(request, 'No se puede editar una orden con recibo emitido o cancelada.')
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
            estado_anterior = orden.estado

            # VALIDACIÓN ESTRICTA: Impedir completar si stock es insuficiente
            if nuevo_estado in ['COMPLETADA', 'ENTREGADA'] and estado_anterior not in ['COMPLETADA', 'ENTREGADA']:
                faltantes = []
                for dp in orden.productos.all():
                    if dp.producto.stock_actual < dp.cantidad:
                        faltantes.append(f"{dp.producto.nombre} (Stock actual: {dp.producto.stock_actual}, Requiere: {dp.cantidad})")
                if faltantes:
                    messages.error(
                        request,
                        f"No se puede completar la orden. Stock insuficiente en: {', '.join(faltantes)}."
                    )
                    return redirect('ordenes:detalle', pk=pk)

            orden.estado = nuevo_estado
            from apps.inventario.models import MovimientoStock

            # Al completar/entregar: descontar stock si no se había descontado
            if nuevo_estado in ['COMPLETADA', 'ENTREGADA'] and estado_anterior not in ['COMPLETADA', 'ENTREGADA']:
                orden.fecha_cierre = timezone.now()
                ya_descontado = MovimientoStock.objects.filter(orden=orden, tipo_movimiento='SALIDA').exists()
                if not ya_descontado:
                    for dp in orden.productos.all():
                        prod = dp.producto
                        prod.stock_actual -= dp.cantidad
                        prod.save()
                        MovimientoStock.objects.create(
                            producto=prod, orden=orden, tipo_movimiento='SALIDA',
                            cantidad=-dp.cantidad, stock_resultante=prod.stock_actual,
                            motivo=f'Consumo OT#{orden.numero_orden}', usuario=request.user.username,
                            precio_unitario=dp.precio_unitario
                        )

            # Reintegro automático de stock en caso de cancelación de OT
            if nuevo_estado == 'CANCELADA' and estado_anterior != 'CANCELADA':
                movimientos_salida = MovimientoStock.objects.filter(orden=orden, tipo_movimiento='SALIDA')
                if movimientos_salida.exists():
                    for mov in movimientos_salida:
                        prod = mov.producto
                        cant_reintegrar = abs(mov.cantidad)
                        prod.stock_actual += cant_reintegrar
                        prod.save()
                        MovimientoStock.objects.create(
                            producto=prod, orden=orden, tipo_movimiento='ENTRADA',
                            cantidad=cant_reintegrar, stock_resultante=prod.stock_actual,
                            motivo=f'Reintegro por cancelación OT#{orden.numero_orden}', usuario=request.user.username,
                            precio_unitario=mov.precio_unitario
                        )
                    messages.info(request, 'Se ha reintegrado automáticamente el stock de los productos consumidos.')

            orden.save()
            messages.success(request, f'Estado cambiado a: {orden.get_estado_display()}')
        else:
            messages.error(request, f'No se puede cambiar de {orden.get_estado_display()} a ese estado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def agregar_servicio(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['COBRADA', 'CANCELADA']:
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
    if orden.estado in ['COBRADA', 'CANCELADA']:
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
    if orden.estado not in ['COBRADA', 'CANCELADA']:
        DetalleServicio.objects.filter(pk=spk, orden=orden).delete()
        messages.success(request, 'Servicio eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def eliminar_producto(request, pk, ppk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado not in ['COBRADA', 'CANCELADA']:
        DetalleProducto.objects.filter(pk=ppk, orden=orden).delete()
        messages.success(request, 'Producto eliminado.')
    return redirect('ordenes:detalle', pk=pk)


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def agregar_repuesto_externo(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if orden.estado in ['COBRADA', 'CANCELADA']:
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
    if orden.estado not in ['COBRADA', 'CANCELADA']:
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

    try:
        if orden.estado == 'COBRADA':
            messages.error(request, f'La orden #{numero} tiene recibo emitido y no puede eliminarse. Debe anularse el recibo primero.')
            return redirect('ordenes:detalle', pk=pk)

        try:
            tiene_comprobante = orden.recibo is not None
        except Exception:
            tiene_comprobante = False

        if tiene_comprobante:
            orden.estado = 'CANCELADA'
            orden.save()
            mensaje = f'La orden #{numero} posee recibo asociado, por lo que fue cancelada en lugar de eliminada.'
        elif orden.estado in ['PENDIENTE', 'CANCELADA']:
            # Reintegrar stock si tuviera consumos registrados antes de borrar
            from apps.inventario.models import MovimientoStock
            movs = MovimientoStock.objects.filter(orden=orden, tipo_movimiento='SALIDA')
            for mov in movs:
                prod = mov.producto
                prod.stock_actual += abs(mov.cantidad)
                prod.save()
            orden.delete()
            mensaje = f'La orden #{numero} fue eliminada exitosamente.'
        else:
            orden.estado = 'CANCELADA'
            # Reintegrar stock
            from apps.inventario.models import MovimientoStock
            movs = MovimientoStock.objects.filter(orden=orden, tipo_movimiento='SALIDA')
            for mov in movs:
                prod = mov.producto
                cant = abs(mov.cantidad)
                prod.stock_actual += cant
                prod.save()
                MovimientoStock.objects.create(
                    producto=prod, orden=orden, tipo_movimiento='ENTRADA',
                    cantidad=cant, stock_resultante=prod.stock_actual,
                    motivo=f'Reintegro por cancelación OT#{orden.numero_orden}', usuario=request.user.username,
                    precio_unitario=mov.precio_unitario
                )
            orden.save()
            mensaje = f'La orden #{numero} fue cancelada. Se reintegró el stock consumido.'

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


@login_required
@requiere_permiso('puede_ver_ordenes')
def orden_kanban(request):
    ahora = timezone.now()
    estados_kanban = ['PENDIENTE', 'EN_PROCESO', 'ESPERA_REPUESTOS', 'COMPLETADA', 'ENTREGADA']
    qs = OrdenTrabajo.objects.select_related('vehiculo', 'vehiculo__cliente', 'mecanico').filter(
        estado__in=estados_kanban
    ).order_by('fecha_prometida', '-fecha_creacion')

    columnas = {e: [] for e in estados_kanban}
    for orden in qs:
        if orden.fecha_prometida:
            diff = orden.fecha_prometida - ahora
            if diff.total_seconds() < 0:
                orden.alerta_plazo = 'rojo'
            elif diff.total_seconds() < 6 * 3600:
                orden.alerta_plazo = 'amarillo'
            else:
                orden.alerta_plazo = 'verde'
        else:
            orden.alerta_plazo = None
        columnas[orden.estado].append(orden)

    labels = {
        'PENDIENTE': 'Pendiente',
        'EN_PROCESO': 'En Proceso',
        'ESPERA_REPUESTOS': 'Espera Repuestos',
        'COMPLETADA': 'Completada',
        'ENTREGADA': 'Entregada',
    }
    return render(request, 'ordenes/kanban.html', {
        'columnas': columnas,
        'estados_kanban': estados_kanban,
        'labels': labels,
    })


@login_required
@requiere_permiso('puede_editar_ordenes', login_url='ordenes:lista')
def reprogramar_fecha(request, pk):
    """Permite reprogramar la fecha prometida de entrega desde el Kanban o Detalle."""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        nueva_fecha = request.POST.get('fecha_prometida')
        justificacion = request.POST.get('justificacion', '').strip()
        if nueva_fecha:
            from django.utils.dateparse import parse_datetime
            parsed = parse_datetime(nueva_fecha)
            if parsed:
                orden.fecha_prometida = parsed
                if justificacion:
                    nota = f" [Reprogramación: {justificacion}]"
                    orden.observaciones = (orden.observaciones or "") + nota
                orden.save(update_fields=['fecha_prometida', 'observaciones'])
                messages.success(request, f'Fecha prometida de OT #{orden.numero_orden} reprogramada.')
            else:
                messages.error(request, 'Formato de fecha inválido.')
    return redirect(request.META.get('HTTP_REFERER') or 'ordenes:kanban')


@login_required
def ajax_buscar_vehiculos(request):
    """Combobox AJAX para búsqueda interactiva de vehículos por placa, cliente o modelo."""
    q = request.GET.get('q', '').strip()
    from apps.vehiculos.models import Vehiculo
    qs = Vehiculo.objects.filter(activo=True, cliente__activo=True).select_related('cliente')
    if q:
        qs = qs.filter(
            Q(placa__icontains=q) |
            Q(marca__icontains=q) |
            Q(modelo__icontains=q) |
            Q(cliente__nombre_razon_social__icontains=q)
        )
    qs = qs[:20]
    data = [
        {
            'id': v.pk,
            'placa': v.placa,
            'marca': v.marca,
            'modelo': v.modelo,
            'cliente': v.cliente.nombre_razon_social,
            'km': v.kilometraje_actual,
            'label': f"{v.placa} — {v.marca} {v.modelo} ({v.cliente.nombre_razon_social})"
        }
        for v in qs
    ]
    return JsonResponse({'results': data})


@login_required
def ajax_vehiculo_km(request):
    vehiculo_id = request.GET.get('id')
    try:
        from apps.vehiculos.models import Vehiculo
        v = Vehiculo.objects.get(pk=vehiculo_id, activo=True, cliente__activo=True)
        return JsonResponse({'km': v.kilometraje_actual, 'placa': v.placa, 'descripcion': str(v)})
    except Vehiculo.DoesNotExist:
        return JsonResponse({'error': 'No encontrado o inactivo'}, status=404)
