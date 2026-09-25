from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Factura, Pago
from apps.ordenes.models import OrdenTrabajo
from django.conf import settings


@login_required
def factura_list(request):
    estado_filter = request.GET.get('estado', '')
    query = request.GET.get('q', '')
    qs = Factura.objects.select_related('cliente', 'orden').order_by('-fecha_emision')
    if estado_filter:
        qs = qs.filter(estado_pago=estado_filter)
    if query:
        qs = qs.filter(Q(numero_factura__icontains=query) | Q(cliente__nombre_razon_social__icontains=query))
    return render(request, 'facturas/lista.html', {'facturas': qs, 'query': query, 'estado_filter': estado_filter})


@login_required
def factura_detalle(request, pk):
    factura = get_object_or_404(Factura.objects.select_related('cliente', 'orden'), pk=pk)
    pagos = factura.pagos.all()
    return render(request, 'facturas/detalle.html', {'factura': factura, 'pagos': pagos})


@login_required
def generar_factura(request, orden_pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para facturar.')
        return redirect('ordenes:lista')
    orden = get_object_or_404(OrdenTrabajo, pk=orden_pk)
    if orden.estado != 'COMPLETADA':
        messages.error(request, 'Solo se pueden facturar ordenes completadas.')
        return redirect('ordenes:detalle', pk=orden_pk)
    if hasattr(orden, 'factura'):
        messages.warning(request, 'Esta orden ya tiene una factura generada.')
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
    messages.success(request, f'Factura #{factura.numero_factura} generada exitosamente.')
    return redirect('facturas:detalle', pk=factura.pk)


@login_required
def registrar_pago(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('facturas:lista')
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        try:
            monto = float(request.POST.get('monto', 0))
            metodo = request.POST.get('metodo_pago', 'EFECTIVO')
            referencia = request.POST.get('referencia', '')
            if monto <= 0:
                raise ValueError
            if monto > float(factura.saldo_pendiente):
                messages.error(request, f'El monto supera el saldo pendiente (${factura.saldo_pendiente}).')
            else:
                Pago.objects.create(
                    factura=factura, monto=monto, metodo_pago=metodo,
                    referencia=referencia, usuario=request.user.username
                )
                factura.actualizar_estado()
                messages.success(request, f'Pago de ${monto} registrado.')
        except (ValueError, TypeError):
            messages.error(request, 'Monto invalido.')
    return redirect('facturas:detalle', pk=pk)
