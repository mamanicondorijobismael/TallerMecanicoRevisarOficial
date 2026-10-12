import csv
from datetime import timedelta
from decimal import Decimal
import os
import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Abs, Coalesce
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.decorador import requiere_permiso
from apps.clientes.models import Cliente
from apps.facturas.models import Factura, Pago
from apps.inventario.models import MovimientoStock, ProductoBase
from apps.ordenes.models import OrdenTrabajo
from apps.vehiculos.models import Vehiculo


@login_required
@requiere_permiso('puede_ver_reportes')
def dashboard_reportes(request):
    """
    Panel General de Métricas y Analítica del Taller Mecánico.
    Acceso controlado estrictamente por rol y privilegios.
    """
    periodo = int(request.GET.get('periodo', 30))
    hoy = timezone.localtime(timezone.now()).date()
    inicio = hoy - timedelta(days=periodo)

    # Ingresos y Comprobantes por periodo
    comprobantes = Factura.objects.filter(fecha_emision__date__gte=inicio)
    ingresos = comprobantes.aggregate(total=Sum('total'))['total'] or Decimal('0')
    costos = Decimal('0')
    for f in comprobantes:
        if f.orden:
            costos += sum(d.costo_total for d in f.orden.productos.all())
    ganancia = ingresos - costos
    margen = round((ganancia / ingresos * 100), 1) if ingresos > 0 else 0

    # Ventas de hoy
    comprobantes_hoy = Factura.objects.filter(fecha_emision__date=hoy)
    ventas_hoy = comprobantes_hoy.aggregate(total=Sum('total'))['total'] or Decimal('0')
    cantidad_ventas_hoy = comprobantes_hoy.count()

    # Órdenes por estado
    ordenes_stats = OrdenTrabajo.objects.filter(
        fecha_creacion__date__gte=inicio
    ).values('estado').annotate(cantidad=Count('id')).order_by('estado')

    # Evolución de ventas/comprobantes para gráfico
    labels = []
    data_ingresos = []
    paso = 1 if periodo <= 31 else (periodo // 15)
    for i in range(periodo - 1, -1, -paso):
        dia = hoy - timedelta(days=i)
        labels.append(dia.strftime('%d/%m'))
        total_dia = Factura.objects.filter(
            fecha_emision__date=dia
        ).aggregate(t=Sum('total'))['t'] or 0
        data_ingresos.append(float(total_dia))

    # Top Clientes
    top_clientes = Factura.objects.filter(fecha_emision__date__gte=inicio)\
        .values('cliente__nombre_razon_social')\
        .annotate(total=Sum('total'), cantidad=Count('id'))\
        .order_by('-total')[:5]

    # Top Productos vendidos / despachados
    top_productos = MovimientoStock.objects.filter(
        tipo_movimiento__in=['SALIDA', 'VENTA_DIRECTA'],
        fecha_movimiento__date__gte=inicio
    ).values('producto__nombre').annotate(
        num_movimientos=Count('id'), total_salidas=Coalesce(Abs(Sum('cantidad')), 0)
    ).order_by('-total_salidas')[:5]

    comprobantes_recientes = Factura.objects.select_related('cliente', 'orden').order_by('-fecha_emision')[:10]

    ordenes_estados = [stat['estado'] for stat in ordenes_stats]
    ordenes_datos = [stat['cantidad'] for stat in ordenes_stats]

    # Productos con stock crítico
    productos_bajo_stock = ProductoBase.objects.filter(stock_actual__lte=F('stock_minimo')).order_by('stock_actual')[:5]

    context = {
        'periodo': periodo,
        'ingresos': ingresos,
        'costos': costos,
        'ganancia': ganancia,
        'margen': margen,
        'ordenes_stats': ordenes_stats,
        'ordenes_estados': ordenes_estados,
        'ordenes_datos': ordenes_datos,
        'labels': labels,
        'data_ingresos': data_ingresos,
        'top_clientes': top_clientes,
        'top_productos': top_productos,
        'comprobantes_recientes': comprobantes_recientes,
        'productos_bajo_stock': productos_bajo_stock,
        'total_clientes': Cliente.objects.filter(activo=True).count(),
        'hoy': hoy,
        'ventas_hoy': ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'comprobantes_hoy_list': comprobantes_hoy,
    }
    return render(request, 'reportes/dashboard.html', context)


@login_required
@requiere_permiso('puede_ver_cierre_diario')
def reporte_diario(request):
    """
    Cierre Oficial de Operaciones Diario con estructura formal contable y operativa.
    """
    fecha_param = request.GET.get('fecha')
    if fecha_param:
        try:
            from django.utils.dateparse import parse_date
            hoy = parse_date(fecha_param) or timezone.localtime(timezone.now()).date()
        except Exception:
            hoy = timezone.localtime(timezone.now()).date()
    else:
        hoy = timezone.localtime(timezone.now()).date()

    # Respaldo automático de la base de datos al generar cierre
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backup_name = f"backup_diario_{hoy.strftime('%Y_%m_%d')}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_name)

    if not os.path.exists(backup_path):
        try:
            shutil.copy2(settings.DATABASES['default']['NAME'], backup_path)
            all_backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)], key=os.path.getctime)
            if len(all_backups) > 30:
                os.remove(all_backups[0])
        except Exception:
            pass

    # 1. Comprobantes emitidos en el día
    comprobantes_hoy = Factura.objects.filter(fecha_emision__date=hoy).select_related(
        'cliente', 'orden'
    ).prefetch_related('orden__productos', 'orden__productos__producto')
    total_ventas = comprobantes_hoy.aggregate(total=Sum('total'))['total'] or Decimal('0')

    # 2. Pagos / Cobranzas recaudadas en el día
    pagos_hoy = Pago.objects.filter(fecha__date=hoy).select_related('factura', 'factura__cliente')
    total_recaudado = pagos_hoy.aggregate(total=Sum('monto'))['total'] or Decimal('0')

    # Desglose de cobros por método de pago
    cobros_por_metodo = pagos_hoy.values('metodo_pago').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')

    # 3. Movimientos de inventario registrados en el día
    movimientos_hoy = MovimientoStock.objects.filter(
        fecha_movimiento__date=hoy
    ).select_related('producto', 'producto__categoria').order_by('-fecha_movimiento')

    # 4. Órdenes de trabajo atendidas / cerradas en el día
    ordenes_hoy = OrdenTrabajo.objects.filter(
        Q(fecha_creacion__date=hoy) | Q(fecha_modificacion__date=hoy, estado__in=['COMPLETADA', 'FACTURADA'])
    ).select_related('vehiculo', 'vehiculo__cliente', 'mecanico')

    # 5. Nuevos registros
    clientes_nuevos = Cliente.objects.filter(fecha_creacion__date=hoy)
    vehiculos_nuevos = Vehiculo.objects.filter(fecha_creacion__date=hoy).select_related('cliente')

    context = {
        'hoy': hoy,
        'comprobantes': comprobantes_hoy,
        'total_ventas': total_ventas,
        'total_recaudado': total_recaudado,
        'pagos': pagos_hoy,
        'cobros_por_metodo': cobros_por_metodo,
        'movimientos': movimientos_hoy,
        'ordenes': ordenes_hoy,
        'clientes_nuevos': clientes_nuevos,
        'vehiculos_nuevos': vehiculos_nuevos,
        'resumen': {
            'comprobantes_count': comprobantes_hoy.count(),
            'pagos_count': pagos_hoy.count(),
            'movimientos_count': movimientos_hoy.count(),
            'ordenes_count': ordenes_hoy.count(),
            'clientes_count': clientes_nuevos.count(),
            'vehiculos_count': vehiculos_nuevos.count(),
        }
    }
    return render(request, 'reportes/diario.html', context)


@login_required
@requiere_permiso('puede_ver_cierre_diario')
def exportar_cierre_diario_csv(request):
    """Exportación oficial a CSV estructurado del cierre diario."""
    fecha_param = request.GET.get('fecha')
    if fecha_param:
        from django.utils.dateparse import parse_date
        hoy = parse_date(fecha_param) or timezone.localtime(timezone.now()).date()
    else:
        hoy = timezone.localtime(timezone.now()).date()

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="Cierre_Diario_{hoy.strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['EL TALLER DEL MAESTRO - REPORTE DE CIERRE DIARIO'])
    writer.writerow(['Fecha de Cierre:', hoy.strftime('%d/%m/%Y')])
    writer.writerow(['Generado por:', request.user.nombre_completo])
    writer.writerow([])

    # Sección I: Comprobantes emitidos
    writer.writerow(['--- I. COMPROBANTES EMITIDOS ---'])
    writer.writerow(['N° Comprobante', 'Hora', 'Cliente', 'Documento', 'OT', 'Subtotal', 'IVA', 'Total', 'Estado'])
    comprobantes = Factura.objects.filter(fecha_emision__date=hoy).select_related('cliente', 'orden')
    for c in comprobantes:
        ot_num = c.orden.numero_orden if c.orden else 'N/A'
        writer.writerow([
            c.numero_factura,
            c.fecha_emision.strftime('%H:%M'),
            c.cliente.nombre_razon_social,
            c.cliente.documento,
            f"OT#{ot_num}",
            f"{c.subtotal:.2f}",
            f"{c.iva_monto:.2f}",
            f"{c.total:.2f}",
            c.get_estado_pago_display()
        ])
    writer.writerow([])

    # Sección II: Pagos
    writer.writerow(['--- II. COBROS Y PAGOS REGISTRADOS ---'])
    writer.writerow(['Hora', 'Comprobante', 'Cliente', 'Método', 'Referencia', 'Monto'])
    pagos = Pago.objects.filter(fecha__date=hoy).select_related('factura', 'factura__cliente')
    for p in pagos:
        writer.writerow([
            p.fecha.strftime('%H:%M'),
            p.factura.numero_factura,
            p.factura.cliente.nombre_razon_social,
            p.get_metodo_pago_display(),
            p.referencia,
            f"{p.monto:.2f}"
        ])
    writer.writerow([])

    return response


@login_required
@requiere_permiso('puede_ver_reportes')
def reporte_movimientos(request):
    """
    Reporte y Kardex de Movimientos de Inventario con filtros por fecha y tipo.
    """
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')

    hoy = timezone.localtime(timezone.now()).date()
    inicio = fecha_inicio if fecha_inicio else (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    fin = fecha_fin if fecha_fin else hoy.strftime('%Y-%m-%d')

    movimientos = MovimientoStock.objects.select_related(
        'producto', 'producto__categoria'
    ).filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    total_entradas = movimientos.filter(tipo_movimiento='ENTRADA').aggregate(total=Sum('cantidad'))['total'] or 0
    total_salidas = movimientos.filter(tipo_movimiento__in=['SALIDA', 'VENTA_DIRECTA']).aggregate(total=Sum('cantidad'))['total'] or 0

    context = {
        'movimientos': movimientos,
        'inicio': inicio,
        'fin': fin,
        'tipo': tipo,
        'total_entradas': total_entradas,
        'total_salidas': abs(total_salidas),
    }
    return render(request, 'reportes/movimientos.html', context)


@login_required
@requiere_permiso('puede_ver_reportes')
def exportar_movimientos_csv(request):
    """Exportación de movimientos de almacén a CSV estructurado."""
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')

    hoy = timezone.localtime(timezone.now()).date()
    if not inicio:
        inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fin:
        fin = hoy.strftime('%Y-%m-%d')

    movimientos = MovimientoStock.objects.select_related('producto', 'producto__categoria').filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="Kardex_Movimientos_{inicio}_al_{fin}.csv"'

    writer = csv.writer(response)
    writer.writerow(['EL TALLER DEL MAESTRO - REPORTE DE MOVIMIENTOS DE INVENTARIO'])
    writer.writerow(['Periodo:', f'{inicio} al {fin}'])
    writer.writerow([])
    writer.writerow(['Fecha y Hora', 'SKU', 'Categoría', 'Producto', 'Tipo', 'Cantidad', 'Stock Resultante', 'Motivo', 'Registrado Por'])

    for m in movimientos:
        cat_nom = m.producto.categoria.nombre if m.producto.categoria else 'N/A'
        writer.writerow([
            m.fecha_movimiento.strftime('%d/%m/%Y %H:%M'),
            m.producto.codigo_sku,
            cat_nom,
            m.producto.nombre,
            m.tipo_movimiento,
            m.cantidad,
            m.stock_resultante,
            m.motivo,
            m.usuario
        ])

    return response
