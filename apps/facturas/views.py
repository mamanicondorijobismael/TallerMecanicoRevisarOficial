from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Factura, Pago
from apps.ordenes.models import OrdenTrabajo
from apps.accounts.decorador import requiere_permiso
from django.conf import settings


@login_required
@requiere_permiso('puede_ver_comprobantes')
def factura_list(request):
    """Listado general de Comprobantes de Cobro."""
    estado_filter = request.GET.get('estado', '')
    query = request.GET.get('q', '').strip()
    qs = Factura.objects.select_related('cliente', 'orden', 'orden__vehiculo').order_by('-fecha_emision')
    if estado_filter:
        qs = qs.filter(estado_pago=estado_filter)
    if query:
        qs = qs.filter(Q(numero_factura__icontains=query) | Q(cliente__nombre_razon_social__icontains=query) | Q(orden__numero_orden__icontains=query))
    return render(request, 'facturas/lista.html', {'facturas': qs, 'query': query, 'estado_filter': estado_filter})


@login_required
@requiere_permiso('puede_ver_comprobantes')
def factura_detalle(request, pk):
    """Ficha detallada del Comprobante, liquidación e historial de pagos."""
    factura = get_object_or_404(Factura.objects.select_related('cliente', 'orden', 'orden__vehiculo'), pk=pk)
    pagos = factura.pagos.all().order_by('-fecha')
    return render(request, 'facturas/detalle.html', {'factura': factura, 'pagos': pagos})


@login_required
@requiere_permiso('puede_crear_comprobantes', login_url='ordenes:lista')
def generar_factura(request, orden_pk):
    """Emisión oficial de un Comprobante a partir de una orden de trabajo completada."""
    orden = get_object_or_404(OrdenTrabajo, pk=orden_pk)
    if orden.estado != 'COMPLETADA':
        messages.error(request, 'Solo se pueden emitir comprobantes para órdenes de trabajo completadas.')
        return redirect('ordenes:detalle', pk=orden_pk)
    if hasattr(orden, 'factura'):
        messages.warning(request, 'Esta orden de trabajo ya tiene un comprobante generado.')
        return redirect('facturas:detalle', pk=orden.factura.pk)

    iva_pct = getattr(settings, 'IVA_PORCENTAJE', 21)
    factura = Factura.objects.create(
        orden=orden,
        cliente=orden.cliente,
        subtotal=orden.subtotal,
        iva_porcentaje=iva_pct,
        iva_monto=orden.iva_monto,
        total=orden.total,
    )
    orden.estado = 'FACTURADA'
    orden.save()
    messages.success(request, f'Comprobante #{factura.numero_factura} generado exitosamente.')
    return redirect('facturas:detalle', pk=factura.pk)


@login_required
@requiere_permiso('puede_cobrar_comprobantes', login_url='facturas:lista')
def registrar_pago(request, pk):
    """Registro de abonos o pagos totales para un comprobante."""
    factura = get_object_or_404(Factura, pk=pk)
    if factura.estado_pago == 'ANULADA':
        messages.error(request, 'No se pueden registrar pagos en un comprobante anulado.')
        return redirect('facturas:detalle', pk=pk)

    if request.method == 'POST':
        try:
            monto = float(request.POST.get('monto', 0))
            metodo = 'EFECTIVO'
            referencia = request.POST.get('referencia', '').strip()
            if monto <= 0:
                raise ValueError
            if monto > float(factura.saldo_pendiente):
                messages.error(request, f'El monto ingresado (Bs {monto:.2f}) supera el saldo pendiente (Bs {factura.saldo_pendiente:.2f}).')
            else:
                Pago.objects.create(
                    factura=factura, monto=monto, metodo_pago=metodo,
                    referencia=referencia, usuario=request.user.username
                )
                factura.actualizar_estado()
                messages.success(request, f'Pago de Bs {monto:.2f} registrado exitosamente.')
        except (ValueError, TypeError):
            messages.error(request, 'Monto inválido ingresado.')
    return redirect('facturas:detalle', pk=pk)


@login_required
@requiere_permiso('puede_anular_comprobantes', login_url='facturas:lista')
def anular_factura(request, pk):
    """Anulación de comprobante."""
    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para anulación.')
        return redirect('facturas:detalle', pk=pk)

    factura = get_object_or_404(Factura, pk=pk)
    if factura.pagos.exists():
        messages.error(request, 'No se puede anular un comprobante que ya posee cobros registrados.')
        return redirect('facturas:detalle', pk=pk)

    factura.estado_pago = 'ANULADA'
    factura.save()
    if factura.orden:
        factura.orden.estado = 'COMPLETADA'
        factura.orden.save()

    messages.success(request, f'Comprobante #{factura.numero_factura} anulado. La orden de trabajo fue restablecida a estado Completada.')
    return redirect('facturas:detalle', pk=pk)


@login_required
@requiere_permiso('puede_ver_comprobantes')
def imprimir_comprobante(request, pk):
    """Vista formal e imprimible del comprobante para entrega al cliente."""
    factura = get_object_or_404(Factura.objects.select_related('cliente', 'orden', 'orden__vehiculo'), pk=pk)
    pagos = factura.pagos.all().order_by('fecha')
    servicios = factura.orden.servicios.all() if factura.orden else []
    productos = factura.orden.productos.select_related('producto').all() if factura.orden else []
    repuestos_externos = factura.orden.repuestos_externos.all() if factura.orden else []

    return render(request, 'facturas/imprimir.html', {
        'factura': factura,
        'pagos': pagos,
        'servicios': servicios,
        'productos': productos,
        'repuestos_externos': repuestos_externos,
    })
