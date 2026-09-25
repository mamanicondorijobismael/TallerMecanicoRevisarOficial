from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.ordenes.models import OrdenTrabajo
from apps.facturas.models import Factura, Pago
from apps.inventario.models import ProductoBase, MovimientoStock
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.mantenimiento.models import AlertaMantenimiento


@login_required
def dashboard_reportes(request):
    if not request.user.es_dueno:
        from django.contrib import messages
        messages.error(request, 'Solo el dueno puede ver los reportes.')
        return redirect('dashboard')

    periodo = int(request.GET.get('periodo', 30))
    hoy = timezone.localtime(timezone.now()).date()
    inicio = hoy - timedelta(days=periodo)

    # Ingresos por periodo
    facturas = Factura.objects.filter(fecha_emision__date__gte=inicio)
    ingresos = facturas.aggregate(total=Sum('total'))['total'] or Decimal('0')
    costos = Decimal('0')
    for f in facturas:
        costos += sum(d.costo_total for d in f.orden.productos.all()) if f.orden else 0
    ganancia = ingresos - costos
    margen = round((ganancia / ingresos * 100), 1) if ingresos > 0 else 0

    # Ventas de hoy
    facturas_hoy = Factura.objects.filter(fecha_emision__date=hoy)
    ventas_hoy = facturas_hoy.aggregate(total=Sum('total'))['total'] or Decimal('0')
    cantidad_ventas_hoy = facturas_hoy.count()

    # Ordenes por estado
    ordenes_stats = OrdenTrabajo.objects.filter(
        fecha_creacion__date__gte=inicio
    ).values('estado').annotate(cantidad=Count('id')).order_by('estado')

    # Tickets por periodo para grafico
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

    # Top clientes
    top_clientes = Factura.objects.filter(fecha_emision__date__gte=inicio)\
        .values('cliente__nombre_razon_social')\
        .annotate(total=Sum('total'), cantidad=Count('id'))\
        .order_by('-total')[:5]

    from django.db.models.functions import Abs, Coalesce
    # Top productos vendidos
    top_productos = MovimientoStock.objects.filter(
        tipo_movimiento__in=['SALIDA', 'VENTA_DIRECTA'],
        fecha_movimiento__date__gte=inicio
    ).values('producto__nombre').annotate(
        num_movimientos=Count('id'), total_salidas=Coalesce(Abs(Sum('cantidad')), 0)
    ).order_by('-total_salidas')[:5]

    facturas_recientes = Factura.objects.select_related('cliente', 'orden').order_by('-fecha_emision')[:10]

    ordenes_estados = [stat['estado'] for stat in ordenes_stats]
    ordenes_datos = [stat['cantidad'] for stat in ordenes_stats]

    # Productos con Bajo Stock
    productos_bajo_stock = ProductoBase.objects.filter(stock_actual__lte=F('stock_minimo')).order_by('stock_actual')[:5]

    # Alertas de mantenimiento pendientes
    alertas_proximas = AlertaMantenimiento.objects.filter(estado='PENDIENTE').select_related('vehiculo', 'tipo_servicio').order_by('fecha_estimada')[:5]

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
        'facturas_recientes': facturas_recientes,
        'productos_bajo_stock': productos_bajo_stock,
        'alertas_proximas': alertas_proximas,
        'total_clientes': Cliente.objects.count(),
        'hoy': hoy,
        'ventas_hoy': ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'facturas_hoy_list': facturas_hoy,
    }
    return render(request, 'reportes/dashboard.html', context)


@login_required
def reporte_diario(request):
    if not request.user.es_dueno:
        return redirect('dashboard')
    
    hoy = timezone.localtime(timezone.now()).date()
    
    # --- RESPALDO AUTOMÁTICO AL CIERRE ---
    import shutil
    import os
    from django.conf import settings
    
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Crear nombre de archivo con la fecha
    backup_name = f"backup_diario_{hoy.strftime('%Y_%m_%d')}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Solo hacer backup si no existe el de hoy (para no sobrecargar)
    if not os.path.exists(backup_path):
        try:
            shutil.copy2(settings.DATABASES['default']['NAME'], backup_path)
            # Mantener solo los últimos 30 backups para no llenar el disco
            all_backups = sorted([os.path.join(backup_dir, f) for f in os.listdir(backup_dir)], key=os.path.getctime)
            if len(all_backups) > 30:
                os.remove(all_backups[0])
        except Exception:
            pass # No bloquear el reporte si falla el backup
    # --------------------------------------
    
    # Ventas Detalladas (incluyendo productos de la orden)
    facturas_hoy = Factura.objects.filter(fecha_emision__date=hoy).select_related('cliente', 'orden').prefetch_related('orden__productos', 'orden__productos__producto')
    total_ventas = facturas_hoy.aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Pagos recibidos hoy con método de pago
    pagos_hoy = Pago.objects.filter(fecha__date=hoy).select_related('factura', 'factura__cliente')
    total_recaudado = pagos_hoy.aggregate(total=Sum('monto'))['total'] or Decimal('0')
    
    # Movimientos de inventario recontra detallados
    movimientos_hoy = MovimientoStock.objects.filter(fecha_movimiento__date=hoy).select_related('producto').order_by('-fecha_movimiento')
    
    # Mantenimiento hoy (Alertas atendidas y programadas)
    alertas_atendidas = AlertaMantenimiento.objects.filter(estado='ATENDIDA', fecha_modificacion__date=hoy).select_related('vehiculo', 'tipo_servicio')
    alertas_nuevas = AlertaMantenimiento.objects.filter(fecha_creacion__date=hoy).select_related('vehiculo', 'tipo_servicio')
    
    # Órdenes de trabajo hoy
    ordenes_hoy = OrdenTrabajo.objects.filter(Q(fecha_creacion__date=hoy) | Q(fecha_modificacion__date=hoy, estado='COMPLETADA')).select_related('vehiculo', 'cliente')

    # Nuevos Registros
    clientes_nuevos = Cliente.objects.filter(fecha_creacion__date=hoy)
    vehiculos_nuevos = Vehiculo.objects.filter(fecha_creacion__date=hoy).select_related('cliente')

    context = {
        'hoy': hoy,
        'facturas': facturas_hoy,
        'total_ventas': total_ventas,
        'total_recaudado': total_recaudado,
        'pagos': pagos_hoy,
        'movimientos': movimientos_hoy,
        'alertas_atendidas': alertas_atendidas,
        'alertas_nuevas': alertas_nuevas,
        'ordenes': ordenes_hoy,
        'clientes_nuevos': clientes_nuevos,
        'vehiculos_nuevos': vehiculos_nuevos,
        'resumen': {
            'ventas_count': facturas_hoy.count(),
            'pagos_count': pagos_hoy.count(),
            'movimientos_count': movimientos_hoy.count(),
            'alertas_atendidas_count': alertas_atendidas.count(),
            'ordenes_count': ordenes_hoy.count(),
        }
    }
    return render(request, 'reportes/diario.html', context)


@login_required
def reporte_movimientos(request):
    if not request.user.es_dueno:
        return redirect('dashboard')
    
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')
    
    hoy = timezone.localtime(timezone.now()).date()
    inicio = fecha_inicio if fecha_inicio else hoy.strftime('%Y-%m-%d')
    fin = fecha_fin if fecha_fin else hoy.strftime('%Y-%m-%d')
    
    movimientos = MovimientoStock.objects.select_related('producto').filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')
    
    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)
        
    # Resumen
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
