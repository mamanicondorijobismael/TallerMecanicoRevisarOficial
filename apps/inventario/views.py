from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import ProductoBase, RepuestoGenerico, Neumatico, CategoriaProducto, MovimientoStock
from .forms import RepuestoForm, NeumaticoForm, MovimientoStockForm, CategoriaForm


@login_required
def producto_list(request):
    query = request.GET.get('q', '')
    criticos_only = request.GET.get('criticos', '')
    tipo = request.GET.get('tipo', '')
    categoria_id = request.GET.get('categoria', '')
    view_mode = request.GET.get('view', 'grid')
    
    qs = ProductoBase.objects.select_related('categoria', 'repuesto', 'neumatico').filter(activo=True).order_by('-fecha_creacion')
    
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(codigo_sku__icontains=query) | Q(descripcion__icontains=query))
    if criticos_only:
        qs = qs.filter(stock_actual__lte=F('stock_minimo'))
    if tipo:
        qs = qs.filter(tipo_producto=tipo)
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    total_count = ProductoBase.objects.filter(activo=True).count()
    repuestos_count = ProductoBase.objects.filter(activo=True, tipo_producto='REPUESTO').count()
    neumaticos_count = ProductoBase.objects.filter(activo=True, tipo_producto='NEUMATICO').count()
    criticos_count = ProductoBase.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).count()
    categorias = CategoriaProducto.objects.all()

    return render(request, 'inventario/lista.html', {
        'productos': qs,
        'query': query,
        'criticos_count': criticos_count,
        'criticos_only': criticos_only,
        'tipo_filter': tipo,
        'categoria_filter': categoria_id,
        'view_mode': view_mode,
        'total_count': total_count,
        'repuestos_count': repuestos_count,
        'neumaticos_count': neumaticos_count,
        'categorias': categorias,
    })


@login_required
def repuesto_list(request):
    query = request.GET.get('q', '')
    qs = RepuestoGenerico.objects.select_related('producto', 'producto__categoria').filter(producto__activo=True).order_by('-producto__fecha_creacion')
    if query:
        qs = qs.filter(
            Q(producto__nombre__icontains=query) | Q(producto__codigo_sku__icontains=query) |
            Q(marca_repuesto__icontains=query) | Q(compatible_con__icontains=query)
        )
    return render(request, 'inventario/repuestos.html', {'repuestos': qs, 'query': query})


@login_required
def neumatico_list(request):
    query = request.GET.get('q', '')
    ancho = request.GET.get('ancho', '')
    perfil = request.GET.get('perfil', '')
    diametro = request.GET.get('diametro', '')
    qs = Neumatico.objects.select_related('producto', 'producto__categoria').filter(producto__activo=True).order_by('-producto__fecha_creacion')
    if query:
        qs = qs.filter(
            Q(producto__nombre__icontains=query) | Q(marca_neumatico__icontains=query) |
            Q(modelo_neumatico__icontains=query)
        )
    if ancho:
        qs = qs.filter(ancho=ancho)
    if perfil:
        qs = qs.filter(perfil=perfil)
    if diametro:
        qs = qs.filter(diametro=diametro)
    return render(request, 'inventario/neumaticos.html', {
        'neumaticos': qs, 'query': query,
        'filtro_ancho': ancho, 'filtro_perfil': perfil, 'filtro_diametro': diametro
    })


@login_required
def repuesto_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:repuestos')
    form = RepuestoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        repuesto = form.save()
        messages.success(request, f'Repuesto {repuesto.producto.nombre} creado.')
        return redirect('inventario:repuestos')
    return render(request, 'inventario/form_repuesto.html', {'form': form, 'title': 'Nuevo Repuesto'})


@login_required
def repuesto_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:repuestos')
    repuesto = get_object_or_404(RepuestoGenerico, pk=pk)
    old_precio = repuesto.producto.precio_venta
    form = RepuestoForm(request.POST or None, request.FILES or None, instance=repuesto)
    if request.method == 'POST' and form.is_valid():
        rep = form.save()
        if rep.producto.precio_venta != old_precio:
            from core.models import Auditoria
            Auditoria.objects.create(
                tabla='ProductoBase', registro_id=rep.producto.pk, accion='MODIFICAR',
                usuario=request.user.username,
                valores_anteriores={'precio_venta': float(old_precio)},
                valores_nuevos={'precio_venta': float(rep.producto.precio_venta)}
            )
        messages.success(request, f'Repuesto actualizado.')
        return redirect('inventario:repuestos')
    movimientos = repuesto.producto.movimientos.all().order_by('-fecha_movimiento')[:10]
    return render(request, 'inventario/form_repuesto.html', {
        'form': form, 'title': f'Editar: {repuesto.producto.nombre}', 
        'repuesto': repuesto, 'movimientos': movimientos
    })


@login_required
def neumatico_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:neumaticos')
    form = NeumaticoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        neumatico = form.save()
        messages.success(request, f'Neumatico {neumatico} creado.')
        return redirect('inventario:neumaticos')
    return render(request, 'inventario/form_neumatico.html', {'form': form, 'title': 'Nuevo Neumatico'})


@login_required
def neumatico_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:neumaticos')
    neumatico = get_object_or_404(Neumatico, pk=pk)
    old_precio = neumatico.producto.precio_venta
    form = NeumaticoForm(request.POST or None, request.FILES or None, instance=neumatico)
    if request.method == 'POST' and form.is_valid():
        neu = form.save()
        if neu.producto.precio_venta != old_precio:
            from core.models import Auditoria
            Auditoria.objects.create(
                tabla='ProductoBase', registro_id=neu.producto.pk, accion='MODIFICAR',
                usuario=request.user.username,
                valores_anteriores={'precio_venta': float(old_precio)},
                valores_nuevos={'precio_venta': float(neu.producto.precio_venta)}
            )
        messages.success(request, f'Neumatico actualizado.')
        return redirect('inventario:neumaticos')
    movimientos = neumatico.producto.movimientos.all().order_by('-fecha_movimiento')[:10]
    return render(request, 'inventario/form_neumatico.html', {
        'form': form, 'title': f'Editar: {neumatico}', 
        'neumatico': neumatico, 'movimientos': movimientos
    })


@login_required
def venta_directa(request, pk):
    """Vender un producto directamente sin orden de trabajo (FIFO)."""
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:lista')
    producto = get_object_or_404(ProductoBase, pk=pk)
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            if cantidad <= 0:
                raise ValueError
            if producto.stock_actual < cantidad:
                messages.error(request, f'Stock insuficiente. Disponible: {producto.stock_actual}')
                return redirect('inventario:lista')
            producto.stock_actual -= cantidad
            producto.save()
            mov = MovimientoStock.objects.create(
                producto=producto,
                tipo_movimiento='VENTA_DIRECTA',
                cantidad=-cantidad,
                stock_resultante=producto.stock_actual,
                motivo=f'Venta directa - {request.POST.get("motivo", "Sin detalle")}',
                usuario=request.user.username,
                precio_unitario=producto.precio_venta,
            )
            messages.success(request, f'Venta registrada: {cantidad}x {producto.nombre}.')
            return redirect('inventario:venta_recibo', pk=mov.pk)
        except (ValueError, TypeError):
            messages.error(request, 'Cantidad invalida.')
    return render(request, 'inventario/venta_directa.html', {'producto': producto})

@login_required
def venta_recibo(request, pk):
    mov = get_object_or_404(MovimientoStock, pk=pk, tipo_movimiento='VENTA_DIRECTA')
    return render(request, 'inventario/venta_recibo.html', {'movimiento': mov})


@login_required
def ajuste_stock(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:lista')
    producto = get_object_or_404(ProductoBase, pk=pk)
    form = MovimientoStockForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cantidad = form.cleaned_data['cantidad']
        tipo = form.cleaned_data['tipo_movimiento']
        if tipo == 'SALIDA' and producto.stock_actual < cantidad:
            messages.error(request, 'Stock insuficiente para la salida.')
        else:
            if tipo == 'SALIDA':
                producto.stock_actual -= cantidad
            else:
                producto.stock_actual += cantidad
            producto.save()
            MovimientoStock.objects.create(
                producto=producto, tipo_movimiento=tipo,
                cantidad=cantidad if tipo == 'ENTRADA' else -cantidad,
                stock_resultante=producto.stock_actual,
                motivo=form.cleaned_data['motivo'],
                usuario=request.user.username
            )
            messages.success(request, 'Stock actualizado.')
            return redirect('inventario:lista')
    return render(request, 'inventario/form_ajuste.html', {'form': form, 'producto': producto})


@login_required
def categoria_lista(request):
    categorias = CategoriaProducto.objects.all()
    return render(request, 'inventario/categorias.html', {'categorias': categorias})


@login_required
def categoria_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:categoria_lista')
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cat = form.save()
        messages.success(request, f'Categoría {cat.nombre} creada.')
        return redirect('inventario:categoria_lista')
    return render(request, 'inventario/form_categoria.html', {'form': form, 'title': 'Nueva Categoría'})


@login_required
def categoria_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:categoria_lista')
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Categoría {categoria.nombre} actualizada.')
        return redirect('inventario:categoria_lista')
    return render(request, 'inventario/form_categoria.html', {'form': form, 'title': f'Editar: {categoria.nombre}'})


@login_required
def categoria_eliminar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos.')
        return redirect('inventario:categoria_lista')
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    if categoria.productos.exists():
        messages.error(request, f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene productos asociados.')
    else:
        categoria.delete()
        messages.success(request, f'Categoría eliminada.')
    return redirect('inventario:categoria_lista')


@login_required
def movimientos_list(request):
    qs = MovimientoStock.objects.select_related('producto').order_by('-fecha_movimiento')[:100]
    return render(request, 'inventario/movimientos.html', {'movimientos': qs})


from django.db.models import RestrictedError, ProtectedError

@login_required
def producto_eliminar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar productos.')
        return redirect('inventario:lista')

    if request.method != 'POST':
        messages.warning(request, 'Método no permitido para esta acción.')
        return redirect('inventario:lista')

    producto = get_object_or_404(ProductoBase, pk=pk)
    nombre = producto.nombre
    sku = producto.codigo_sku

    tiene_movimientos = producto.movimientos.exists()
    tiene_usos = producto.usos.exists()

    try:
        if tiene_movimientos or tiene_usos:
            producto.activo = False
            producto.save()
            accion_audit = 'MODIFICAR'
            mensaje = f'El producto "{nombre}" posee historial de movimientos/órdenes, por lo que fue desactivado del catálogo.'
        else:
            producto.delete()
            accion_audit = 'ELIMINAR'
            mensaje = f'El producto "{nombre}" fue eliminado exitosamente.'

        from core.models import Auditoria
        Auditoria.objects.create(
            tabla='ProductoBase',
            registro_id=pk,
            accion=accion_audit,
            usuario=request.user.username,
            valores_anteriores={'nombre': nombre, 'codigo_sku': sku},
        )
        messages.success(request, mensaje)

    except (RestrictedError, ProtectedError):
        producto.activo = False
        producto.save()
        messages.warning(
            request,
            f'El producto "{nombre}" no pudo eliminarse por registros asociados, pero fue desactivado.'
        )
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la solicitud: {str(e)}')

    return redirect('inventario:lista')
