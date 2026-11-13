import csv
from datetime import timedelta
from decimal import Decimal
import io
import os
import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from apps.accounts.decorador import requiere_permiso
from apps.clientes.models import Cliente
from apps.recibos.models import Recibo, Pago
from apps.inventario.models import MovimientoStock, ProductoBase
from apps.ordenes.models import OrdenTrabajo
from apps.vehiculos.models import Vehiculo


@login_required
@requiere_permiso('puede_ver_reportes')
def dashboard_reportes(request):
    # Obtenemos el período, si no viene nada usamos 30
    periodo_str = request.GET.get('periodo')
    if periodo_str:
        periodo = int(periodo_str)
    else:
        periodo = 30

    hoy = timezone.localtime(timezone.now()).date()
    inicio = hoy - timedelta(days=periodo)

    # Buscamos los recibos del período
    comprobantes = Recibo.objects.filter(fecha_emision__date__gte=inicio)
    
    # Calculamos ingresos sumando uno por uno (estilo novato)
    ingresos = Decimal('0')
    for c in comprobantes:
        if c.total:
            ingresos = ingresos + c.total

    # Calculamos los costos usando un bucle anidado
    costos = Decimal('0')
    for f in comprobantes:
        if f.orden:
            # Buscamos los productos de la orden
            productos_orden = f.orden.productos.all()
            for d in productos_orden:
                if d.costo_total:
                    costos = costos + d.costo_total

    ganancia = ingresos - costos

    if ingresos > 0:
        margen = round((ganancia / ingresos * 100), 1)
    else:
        margen = 0

    # Ventas de hoy
    comprobantes_hoy = Recibo.objects.filter(fecha_emision__date=hoy)
    ventas_hoy = Decimal('0')
    for ch in comprobantes_hoy:
        if ch.total:
            ventas_hoy = ventas_hoy + ch.total
    cantidad_ventas_hoy = comprobantes_hoy.count()

    # Órdenes por estado
    ordenes_qs = OrdenTrabajo.objects.filter(fecha_creacion__date__gte=inicio)
    ordenes_stats = ordenes_qs.values('estado').annotate(cantidad=Count('id')).order_by('estado')

    # Datos para el gráfico (bucle clásico)
    labels = []
    data_ingresos = []
    
    if periodo <= 31:
        paso = 1
    else:
        paso = periodo // 15

    i = periodo - 1
    while i >= 0:
        dia = hoy - timedelta(days=i)
        labels.append(dia.strftime('%d/%m'))
        
        recibos_dia = Recibo.objects.filter(fecha_emision__date=dia)
        total_dia = Decimal('0')
        for r in recibos_dia:
            if r.total:
                total_dia = total_dia + r.total
                
        data_ingresos.append(float(total_dia))
        i = i - paso

    # Top Clientes
    top_clientes = Recibo.objects.filter(fecha_emision__date__gte=inicio)\
        .values('cliente__nombre_razon_social')\
        .annotate(total=Sum('total'), cantidad=Count('id'))\
        .order_by('-total')[:5]

    # Top Productos
    top_productos = MovimientoStock.objects.filter(
        tipo_movimiento__in=['SALIDA', 'VENTA_DIRECTA'],
        fecha_movimiento__date__gte=inicio
    ).values('producto__nombre').annotate(
        num_movimientos=Count('id'), total_salidas=Sum('cantidad')
    ).order_by('-total_salidas')[:5]

    # Para que no dé error si no hay salidas
    for tp in top_productos:
        if tp['total_salidas'] and tp['total_salidas'] < 0:
            tp['total_salidas'] = tp['total_salidas'] * -1
        elif not tp['total_salidas']:
            tp['total_salidas'] = 0

    comprobantes_recientes = Recibo.objects.select_related('cliente', 'orden').order_by('-fecha_emision')[:10]

    # Armar listas para el gráfico de estados
    ordenes_estados = []
    ordenes_datos = []
    for stat in ordenes_stats:
        ordenes_estados.append(stat['estado'])
        ordenes_datos.append(stat['cantidad'])

    productos_bajo_stock = ProductoBase.objects.filter(stock_actual__lte=F('stock_minimo')).order_by('stock_actual')[:5]

    # Compras
    compras_periodo = MovimientoStock.objects.filter(
        tipo_movimiento='ENTRADA',
        fecha_movimiento__date__gte=inicio
    ).select_related('producto').order_by('-fecha_movimiento')
    
    total_compras = Decimal('0')
    for cp in compras_periodo:
        if cp.precio_unitario and cp.cantidad:
            total_compras = total_compras + (cp.precio_unitario * cp.cantidad)
    
    ultimas_compras = compras_periodo[:10]

    total_clientes = Cliente.objects.filter(activo=True).count()

    # Preparamos los datos y los enviamos
    datos = {
        'periodo': periodo,
        'ingresos': ingresos,
        'costos': costos,
        'ganancia': ganancia,
        'margen': margen,
        'total_compras': total_compras,
        'ultimas_compras': ultimas_compras,
        'ordenes_stats': ordenes_stats,
        'ordenes_estados': ordenes_estados,
        'ordenes_datos': ordenes_datos,
        'labels': labels,
        'data_ingresos': data_ingresos,
        'top_clientes': top_clientes,
        'top_productos': top_productos,
        'comprobantes_recientes': comprobantes_recientes,
        'productos_bajo_stock': productos_bajo_stock,
        'total_clientes': total_clientes,
        'hoy': hoy,
        'ventas_hoy': ventas_hoy,
        'cantidad_ventas_hoy': cantidad_ventas_hoy,
        'comprobantes_hoy_list': comprobantes_hoy,
    }
    
    return render(request, 'reportes/dashboard.html', datos)


@login_required
@requiere_permiso('puede_ver_cierre_diario')
def reporte_diario(request):
    fecha_param = request.GET.get('fecha')
    if fecha_param:
        hoy = parse_date(fecha_param)
        if not hoy:
            hoy = timezone.localtime(timezone.now()).date()
    else:
        hoy = timezone.localtime(timezone.now()).date()

    # Hacemos el backup de la base de datos
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backup_name = "backup_diario_" + hoy.strftime('%Y_%m_%d') + ".sqlite3"
    backup_path = os.path.join(backup_dir, backup_name)

    if not os.path.exists(backup_path):
        try:
            db_path = settings.DATABASES['default']['NAME']
            shutil.copy2(db_path, backup_path)
            # Borrar backups viejos si hay más de 30
            todos_los_backups = []
            for archivo in os.listdir(backup_dir):
                todos_los_backups.append(os.path.join(backup_dir, archivo))
            
            todos_los_backups.sort(key=os.path.getctime)
            if len(todos_los_backups) > 30:
                os.remove(todos_los_backups[0])
        except Exception:
            pass

    # 1. Recibos de hoy
    comprobantes_hoy = Recibo.objects.filter(fecha_emision__date=hoy).select_related('cliente', 'orden')
    total_ventas = Decimal('0')
    for c in comprobantes_hoy:
        if c.total:
            total_ventas = total_ventas + c.total

    # 2. Pagos de hoy
    pagos_hoy = Pago.objects.filter(fecha__date=hoy).select_related('recibo', 'recibo__cliente')
    total_recaudado = Decimal('0')
    for p in pagos_hoy:
        if p.monto:
            total_recaudado = total_recaudado + p.monto

    cobros_por_metodo = pagos_hoy.values('metodo_pago').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')

    # 3. Compras
    compras_repuestos_hoy = MovimientoStock.objects.filter(
        fecha_movimiento__date=hoy,
        tipo_movimiento='ENTRADA'
    ).select_related('producto').order_by('-fecha_movimiento')
    
    total_compras_repuestos = Decimal('0')
    for c in compras_repuestos_hoy:
        if c.precio_unitario and c.cantidad:
            total_compras_repuestos = total_compras_repuestos + (c.precio_unitario * c.cantidad)

    balance_caja_dia = total_recaudado - total_compras_repuestos

    # 4. Movimientos
    movimientos_hoy = MovimientoStock.objects.filter(
        fecha_movimiento__date=hoy
    ).order_by('-fecha_movimiento')

    # 5. Órdenes
    ordenes_hoy = OrdenTrabajo.objects.filter(
        Q(fecha_creacion__date=hoy) | Q(fecha_modificacion__date=hoy, estado__in=['COMPLETADA', 'COBRADA'])
    )

    # 6. Nuevos
    clientes_nuevos = Cliente.objects.filter(fecha_creacion__date=hoy)
    vehiculos_nuevos = Vehiculo.objects.filter(fecha_creacion__date=hoy)

    # Resumen (paso a paso)
    resumen = {}
    resumen['comprobantes_count'] = comprobantes_hoy.count()
    resumen['pagos_count'] = pagos_hoy.count()
    resumen['compras_count'] = compras_repuestos_hoy.count()
    resumen['movimientos_count'] = movimientos_hoy.count()
    resumen['ordenes_count'] = ordenes_hoy.count()
    resumen['clientes_count'] = clientes_nuevos.count()
    resumen['vehiculos_count'] = vehiculos_nuevos.count()

    datos = {
        'hoy': hoy,
        'comprobantes': comprobantes_hoy,
        'total_ventas': total_ventas,
        'total_recaudado': total_recaudado,
        'pagos': pagos_hoy,
        'cobros_por_metodo': cobros_por_metodo,
        'compras_repuestos': compras_repuestos_hoy,
        'total_compras_repuestos': total_compras_repuestos,
        'balance_caja_dia': balance_caja_dia,
        'movimientos': movimientos_hoy,
        'ordenes': ordenes_hoy,
        'clientes_nuevos': clientes_nuevos,
        'vehiculos_nuevos': vehiculos_nuevos,
        'resumen': resumen
    }
    return render(request, 'reportes/diario.html', datos)


@login_required
@requiere_permiso('puede_ver_cierre_diario')
def exportar_cierre_diario_csv(request):
    fecha_param = request.GET.get('fecha')
    if fecha_param:
        hoy = parse_date(fecha_param)
        if not hoy:
            hoy = timezone.localtime(timezone.now()).date()
    else:
        hoy = timezone.localtime(timezone.now()).date()

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    nombre_archivo = "Cierre_Diario_" + hoy.strftime("%Y%m%d") + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + nombre_archivo + '"'

    writer = csv.writer(response)
    writer.writerow(['EL TALLER DEL MAESTRO - REPORTE DE CIERRE DIARIO'])
    writer.writerow(['Fecha de Cierre:', hoy.strftime('%d/%m/%Y')])
    writer.writerow(['Generado por:', request.user.nombre_completo])
    writer.writerow([])

    # I. Recibos
    writer.writerow(['--- I. RECIBOS EMITIDOS ---'])
    writer.writerow(['N° Recibo', 'Hora', 'Cliente', 'Documento', 'OT', 'Subtotal', 'IVA', 'Total', 'Estado'])
    comprobantes = Recibo.objects.filter(fecha_emision__date=hoy).select_related('cliente', 'orden')
    for c in comprobantes:
        if c.orden:
            ot_num = c.orden.numero_orden
        else:
            ot_num = 'N/A'
            
        writer.writerow([
            c.numero_recibo,
            c.fecha_emision.strftime('%H:%M'),
            c.cliente.nombre_razon_social,
            c.cliente.documento,
            "OT#" + str(ot_num),
            f"{c.subtotal:.2f}",
            f"{c.iva_monto:.2f}",
            f"{c.total:.2f}",
            c.get_estado_pago_display()
        ])
    writer.writerow([])

    # II. Pagos
    writer.writerow(['--- II. COBROS Y PAGOS REGISTRADOS ---'])
    writer.writerow(['Hora', 'Recibo', 'Cliente', 'Método', 'Referencia', 'Monto'])
    pagos = Pago.objects.filter(fecha__date=hoy).select_related('recibo', 'recibo__cliente')
    for p in pagos:
        writer.writerow([
            p.fecha.strftime('%H:%M'),
            p.recibo.numero_recibo,
            p.recibo.cliente.nombre_razon_social,
            p.get_metodo_pago_display(),
            p.referencia,
            f"{p.monto:.2f}"
        ])
    writer.writerow([])

    # III. Repuestos
    writer.writerow(['--- III. REPUESTOS COMPRADOS / INGRESOS ---'])
    writer.writerow(['Hora', 'SKU', 'Producto', 'Categoría', 'Cantidad', 'Costo Unitario', 'Total Compra', 'Motivo', 'Registrado Por'])
    compras = MovimientoStock.objects.filter(fecha_movimiento__date=hoy, tipo_movimiento='ENTRADA').select_related('producto')
    for cp in compras:
        if cp.precio_unitario:
            cu = cp.precio_unitario
        else:
            cu = Decimal('0')
            
        tot = cu * cp.cantidad
        
        if cp.producto.categoria:
            cat_nom = cp.producto.categoria.nombre
        else:
            cat_nom = 'N/A'
            
        writer.writerow([
            cp.fecha_movimiento.strftime('%H:%M'),
            cp.producto.codigo_sku,
            cp.producto.nombre,
            cat_nom,
            cp.cantidad,
            f"{cu:.2f}",
            f"{tot:.2f}",
            cp.motivo or 'Compra de Repuesto',
            cp.usuario or 'Sistema'
        ])
    writer.writerow([])

    return response


@login_required
@requiere_permiso('puede_ver_reportes')
def reporte_movimientos(request):
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')

    hoy = timezone.localtime(timezone.now()).date()
    
    if fecha_inicio:
        inicio = fecha_inicio
    else:
        inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        
    if fecha_fin:
        fin = fecha_fin
    else:
        fin = hoy.strftime('%Y-%m-%d')

    movimientos = MovimientoStock.objects.select_related('producto').filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    # Sumar entradas
    total_entradas = 0
    for m in movimientos:
        if m.tipo_movimiento == 'ENTRADA':
            total_entradas = total_entradas + m.cantidad

    # Sumar salidas
    total_salidas = 0
    for m in movimientos:
        if m.tipo_movimiento == 'SALIDA' or m.tipo_movimiento == 'VENTA_DIRECTA':
            total_salidas = total_salidas + m.cantidad

    datos = {
        'movimientos': movimientos,
        'inicio': inicio,
        'fin': fin,
        'tipo': tipo,
        'total_entradas': total_entradas,
        'total_salidas': abs(total_salidas),
    }
    return render(request, 'reportes/movimientos.html', datos)


@login_required
@requiere_permiso('puede_ver_reportes')
def exportar_movimientos_csv(request):
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')

    hoy = timezone.localtime(timezone.now()).date()
    if not inicio:
        inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fin:
        fin = hoy.strftime('%Y-%m-%d')

    movimientos = MovimientoStock.objects.select_related('producto').filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    nombre = "Kardex_Movimientos_" + inicio + "_al_" + fin + ".csv"
    response['Content-Disposition'] = 'attachment; filename="' + nombre + '"'

    writer = csv.writer(response)
    writer.writerow(['EL TALLER DEL MAESTRO - REPORTE DE MOVIMIENTOS DE INVENTARIO'])
    writer.writerow(['Periodo:', inicio + ' al ' + fin])
    writer.writerow([])
    writer.writerow(['Fecha y Hora', 'SKU', 'Categoría', 'Producto', 'Tipo', 'Cantidad', 'Stock Resultante', 'Motivo', 'Registrado Por'])

    for m in movimientos:
        if m.producto.categoria:
            cat_nom = m.producto.categoria.nombre
        else:
            cat_nom = 'N/A'
            
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


@login_required
@requiere_permiso('puede_ver_cierre_diario')
def exportar_cierre_diario_pdf(request):
    if not HAS_REPORTLAB:
        messages.error(request, 'El generador de PDF (ReportLab) no está disponible.')
        return redirect('reportes:diario')

    fecha_param = request.GET.get('fecha')
    if fecha_param:
        hoy = parse_date(fecha_param)
        if not hoy:
            hoy = timezone.localtime(timezone.now()).date()
    else:
        hoy = timezone.localtime(timezone.now()).date()

    comprobantes = Recibo.objects.filter(fecha_emision__date=hoy).select_related('cliente', 'orden')
    total_ventas = Decimal('0')
    for c in comprobantes:
        if c.total:
            total_ventas = total_ventas + c.total
            
    pagos = Pago.objects.filter(fecha__date=hoy).select_related('recibo')
    total_recaudado = Decimal('0')
    for p in pagos:
        if p.monto:
            total_recaudado = total_recaudado + p.monto

    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0D284E'))
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748B'))
    h2_style = ParagraphStyle('SectionH2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#0D284E'), spaceBefore=12, spaceAfter=6)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#1E293B'))
    cell_bold = ParagraphStyle('CellBold', parent=cell_style, fontName='Helvetica-Bold')
    cell_right = ParagraphStyle('CellRight', parent=cell_style, alignment=2)

    elements = []

    # Encabezado
    elements.append(Paragraph('EL TALLER DEL MAESTRO', title_style))
    elements.append(Paragraph('Cierre de Operaciones Diario · Fecha: ' + hoy.strftime("%d/%m/%Y") + ' · Generado por: ' + request.user.nombre_completo, subtitle_style))
    elements.append(Spacer(1, 10))

    # Resumen
    resumen_data = [[
        Paragraph('Total Ventas', cell_style),
        Paragraph(f'Bs. {total_ventas:.2f}', cell_bold),
        Paragraph('Total Recaudación', cell_style),
        Paragraph(f'Bs. {total_recaudado:.2f}', cell_bold),
    ]]
    t_resumen = Table(resumen_data, colWidths=[150, 110, 160, 120])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 12))

    # Recibos
    elements.append(Paragraph('1. Recibos Emitidos', h2_style))
    recibos_rows = [[Paragraph('N° Recibo', cell_bold), Paragraph('Hora', cell_bold), Paragraph('Cliente', cell_bold), Paragraph('Subtotal', cell_bold), Paragraph('Total', cell_bold)]]
    for r in comprobantes:
        recibos_rows.append([
            Paragraph(str(r.numero_recibo), cell_style),
            Paragraph(r.fecha_emision.strftime('%H:%M'), cell_style),
            Paragraph(r.cliente.nombre_razon_social[:28], cell_style),
            Paragraph(f'{r.subtotal:.2f}', cell_right),
            Paragraph(f'{r.total:.2f}', cell_right),
        ])
    if len(recibos_rows) == 1:
        recibos_rows.append([Paragraph('No hay recibos.', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style)])
        
    t_recibos = Table(recibos_rows, colWidths=[65, 45, 220, 75, 75])
    t_recibos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D284E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(t_recibos)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Cierre_Diario_' + hoy.strftime("%Y%m%d") + '.pdf"'
    return response


@login_required
@requiere_permiso('puede_ver_reportes')
def exportar_movimientos_pdf(request):
    if not HAS_REPORTLAB:
        messages.error(request, 'El generador de PDF no está disponible.')
        return redirect('reportes:movimientos')

    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    tipo = request.GET.get('tipo')

    hoy = timezone.localtime(timezone.now()).date()
    if not inicio:
        inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fin:
        fin = hoy.strftime('%Y-%m-%d')

    movimientos = MovimientoStock.objects.select_related('producto').filter(
        fecha_movimiento__date__range=[inicio, fin]
    ).order_by('-fecha_movimiento')

    if tipo:
        movimientos = movimientos.filter(tipo_movimiento=tipo)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0D284E'))
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748B'))
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor('#1E293B'))
    cell_bold = ParagraphStyle('CellBold', parent=cell_style, fontName='Helvetica-Bold')

    elements = []
    elements.append(Paragraph('EL TALLER DEL MAESTRO', title_style))
    elements.append(Paragraph('Kardex de Inventario · ' + inicio + ' al ' + fin, subtitle_style))
    elements.append(Spacer(1, 10))

    headers = [
        Paragraph('Fecha', cell_bold), Paragraph('SKU', cell_bold),
        Paragraph('Producto', cell_bold), Paragraph('Tipo', cell_bold),
        Paragraph('Cant.', cell_bold), Paragraph('Motivo', cell_bold),
    ]
    rows = [headers]

    contador = 0
    for m in movimientos:
        if contador >= 100:
            break # Solo mostramos 100
            
        rows.append([
            Paragraph(m.fecha_movimiento.strftime('%d/%m/%Y %H:%M'), cell_style),
            Paragraph(m.producto.codigo_sku, cell_style),
            Paragraph(m.producto.nombre[:25], cell_style),
            Paragraph(m.tipo_movimiento, cell_style),
            Paragraph(str(m.cantidad), cell_style),
            Paragraph((m.motivo or '')[:30], cell_style),
        ])
        contador = contador + 1

    if len(rows) == 1:
        rows.append([Paragraph('Sin movimientos.', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style)])

    t_mov = Table(rows, colWidths=[85, 85, 140, 60, 45, 100])
    t_mov.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D284E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(t_mov)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Kardex_' + inicio + '_al_' + fin + '.pdf"'
    return response