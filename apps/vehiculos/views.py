from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Vehiculo
from .forms import VehiculoForm


@login_required
def vehiculo_list(request):
    query = request.GET.get('q', '')
    qs = Vehiculo.objects.select_related('cliente').all()
    if query:
        qs = qs.filter(
            Q(patente__icontains=query) | Q(marca__icontains=query) |
            Q(modelo__icontains=query) | Q(cliente__nombre_razon_social__icontains=query)
        )
    from apps.clientes.models import Cliente
    clientes = Cliente.objects.filter(activo=True).order_by('nombre_razon_social')
    return render(request, 'vehiculos/lista.html', {'vehiculos': qs, 'query': query, 'clientes': clientes})


@login_required
def vehiculo_detalle(request, pk):
    vehiculo = get_object_or_404(Vehiculo.objects.select_related('cliente'), pk=pk)
    ordenes = vehiculo.ordenes.select_related('mecanico').order_by('-fecha_creacion')
    return render(request, 'vehiculos/detalle.html', {'vehiculo': vehiculo, 'ordenes': ordenes})


@login_required
def vehiculo_crear(request):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para registrar vehiculos.')
        return redirect('vehiculos:lista')
    from apps.clientes.models import Cliente
    cliente_id = request.GET.get('cliente_id')
    initial = {}
    if cliente_id:
        initial['cliente'] = cliente_id
    form = VehiculoForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        vehiculo = form.save()
        messages.success(request, f'Vehiculo {vehiculo.patente} registrado exitosamente.')
        return redirect('vehiculos:detalle', pk=vehiculo.pk)
    return render(request, 'vehiculos/form.html', {'form': form, 'title': 'Nuevo Vehiculo'})


@login_required
def vehiculo_editar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Sin permisos para editar vehiculos.')
        return redirect('vehiculos:lista')
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    form = VehiculoForm(request.POST or None, request.FILES or None, instance=vehiculo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Vehiculo {vehiculo.patente} actualizado.')
        return redirect('vehiculos:detalle', pk=vehiculo.pk)
    return render(request, 'vehiculos/form.html', {'form': form, 'title': f'Editar: {vehiculo.patente}', 'vehiculo': vehiculo})
