from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from decimal import Decimal, InvalidOperation

from .models import Recibo, Pago
from apps.ordenes.models import OrdenTrabajo
from apps.accounts.decorador import requiere_permiso


# ═══════════════════════════════════════════════════════════════════════════
# LISTA
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_ver_comprobantes')
def recibo_lista(request):
    """Listado general de Recibos de Servicio y Cobro."""
    estado_filter = request.GET.get('estado', '').strip()
    query         = request.GET.get('q', '').strip()

    qs = Recibo.objects.select_related(
        'cliente', 'orden', 'orden__vehiculo'
    ).order_by('-fecha_emision')

    if estado_filter:
        qs = qs.filter(estado_pago=estado_filter)

    if query:
        qs = qs.filter(
            Q(numero_recibo__icontains=query) |
            Q(cliente__nombre_razon_social__icontains=query) |
            Q(orden__numero_orden__icontains=query)
        )

    paginator = Paginator(qs, 25)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'recibos/lista.html', {
        'recibos': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
        'estado_filter': estado_filter,
    })


# ═══════════════════════════════════════════════════════════════════════════
# DETALLE
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_ver_comprobantes')
def recibo_detalle(request, pk):
    """Ficha detallada del Recibo, liquidación e historial de pagos."""
    recibo = get_object_or_404(
        Recibo.objects.select_related('cliente', 'orden', 'orden__vehiculo'),
        pk=pk
    )
    pagos = recibo.pagos.all().order_by('-fecha')
    return render(request, 'recibos/detalle.html', {
        'recibo': recibo,
        'pagos': pagos,
    })


# ═══════════════════════════════════════════════════════════════════════════
# GENERAR RECIBO
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_crear_comprobantes', login_url='ordenes:lista')
def generar_recibo(request, orden_pk):
    """Emisión oficial de un Recibo a partir de una orden completada."""
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related('vehiculo__cliente'),
        pk=orden_pk
    )

    if orden.estado != 'COMPLETADA':
        messages.error(request, 'Solo se pueden emitir recibos para órdenes de trabajo completadas.')
        return redirect('ordenes:detalle', pk=orden_pk)

    # Si ya tiene recibo, redirigir al existente
    recibo_existente = getattr(orden, 'recibo', None)
    if recibo_existente:
        messages.warning(request, 'Esta orden de trabajo ya tiene un recibo generado.')
        return redirect('recibos:detalle', pk=recibo_existente.pk)

    iva_pct = Decimal(str(getattr(settings, 'IVA_PORCENTAJE', 21)))

    recibo = Recibo.objects.create(
        orden=orden,
        cliente=orden.vehiculo.cliente,
        subtotal=orden.subtotal,
        iva_porcentaje=iva_pct,
        iva_monto=orden.iva_monto,
        total=orden.total,
    )

    orden.estado = 'COBRADA'
    orden.save(update_fields=['estado'])

    messages.success(request, f'Recibo #{recibo.numero_recibo} generado exitosamente.')
    return redirect('recibos:detalle', pk=recibo.pk)


# ═══════════════════════════════════════════════════════════════════════════
# REGISTRAR PAGO
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_cobrar_comprobantes', login_url='recibos:lista')
def registrar_pago(request, pk):
    """Registro de cobro o pagos para un recibo."""
    recibo = get_object_or_404(Recibo.objects.select_related('orden'), pk=pk)

    if recibo.estado_pago == 'ANULADA':
        messages.error(request, 'No se pueden registrar pagos en un recibo anulado.')
        return redirect('recibos:detalle', pk=pk)

    if request.method != 'POST':
        return redirect('recibos:detalle', pk=pk)

    # Parseo tolerante del monto (acepta "1500", "1500.50", "1.500,50")
    monto_raw = (request.POST.get('monto') or '').strip().replace(' ', '')
    monto_raw = monto_raw.replace('.', '').replace(',', '.') if ',' in monto_raw else monto_raw

    try:
        monto = Decimal(monto_raw)
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, 'Monto inválido. Usá solo números (ej: 1500.50).')
        return redirect('recibos:detalle', pk=pk)

    if monto <= 0:
        messages.error(request, 'El monto debe ser mayor a cero.')
        return redirect('recibos:detalle', pk=pk)

    saldo = Decimal(str(recibo.saldo_pendiente or 0))
    if monto > saldo:
        messages.error(
            request,
            f'El monto ingresado (Bs {monto:.2f}) supera el saldo pendiente (Bs {saldo:.2f}).'
        )
        return redirect('recibos:detalle', pk=pk)

    metodo     = (request.POST.get('metodo_pago') or 'EFECTIVO').upper()
    referencia = (request.POST.get('referencia') or '').strip()

    Pago.objects.create(
        recibo=recibo,
        monto=monto,
        metodo_pago=metodo,
        referencia=referencia,
        usuario=request.user.username,
    )
    recibo.actualizar_estado()

    messages.success(request, f'Pago de Bs {monto:.2f} registrado exitosamente.')
    return redirect('recibos:detalle', pk=pk)


# ═══════════════════════════════════════════════════════════════════════════
# ANULAR RECIBO
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_anular_comprobantes', login_url='recibos:lista')
def anular_recibo(request, pk):
    """Anulación de recibo."""
    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para anulación.')
        return redirect('recibos:detalle', pk=pk)

    recibo = get_object_or_404(Recibo.objects.select_related('orden'), pk=pk)

    if recibo.estado_pago == 'ANULADA':
        messages.info(request, 'Este recibo ya estaba anulado.')
        return redirect('recibos:detalle', pk=pk)

    if recibo.pagos.exists():
        messages.error(request, 'No se puede anular un recibo que ya posee cobros registrados.')
        return redirect('recibos:detalle', pk=pk)

    recibo.estado_pago = 'ANULADA'
    recibo.save(update_fields=['estado_pago'])

    if recibo.orden:
        recibo.orden.estado = 'COMPLETADA'
        recibo.orden.save(update_fields=['estado'])

    messages.success(
        request,
        f'Recibo #{recibo.numero_recibo} anulado. La orden fue restablecida a "Completada".'
    )
    return redirect('recibos:detalle', pk=pk)


# ═══════════════════════════════════════════════════════════════════════════
# IMPRIMIR
# ═══════════════════════════════════════════════════════════════════════════
@login_required
@requiere_permiso('puede_ver_comprobantes')
def imprimir_recibo(request, pk):
    """Vista formal e imprimible del recibo."""
    recibo = get_object_or_404(
        Recibo.objects.select_related('cliente', 'orden', 'orden__vehiculo'),
        pk=pk
    )
    pagos = recibo.pagos.all().order_by('fecha')

    orden              = recibo.orden
    servicios          = orden.servicios.all() if orden else []
    productos          = orden.productos.select_related('producto').all() if orden else []
    repuestos_externos = orden.repuestos_externos.all() if orden else []

    return render(request, 'recibos/imprimir.html', {
        'recibo': recibo,
        'pagos': pagos,
        'servicios': servicios,
        'productos': productos,
        'repuestos_externos': repuestos_externos,
    })