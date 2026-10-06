from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AlertaMantenimiento, TipoServicio
from .forms import AlertaForm, TipoServicioForm

@login_required
def alerta_list(request):
    estado_filter = request.GET.get('estado', 'PENDIENTE')
    qs = AlertaMantenimiento.objects.select_related('vehiculo', 'vehiculo__cliente', 'tipo_servicio').order_by('-fecha_creacion')
    if estado_filter:
        qs = qs.filter(estado=estado_filter)
    total_pendiente = AlertaMantenimiento.objects.filter(estado='PENDIENTE').count()
    return render(request, 'mantenimiento/alertas.html', {
        'alertas': qs, 'estado_filter': estado_filter, 'total_pendiente': total_pendiente
    })

@login_required
def alerta_crear(request):
    form = AlertaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alerta = form.save()
        messages.success(request, f'Alerta creada para {alerta.vehiculo.patente}.')
        return redirect('mantenimiento:alertas')
    return render(request, 'mantenimiento/form_alerta.html', {'form': form, 'title': 'Nueva Alerta'})

@login_required
def alerta_cambiar_estado(request, pk, estado):
    alerta = get_object_or_404(AlertaMantenimiento, pk=pk)
    alerta.estado = estado
    alerta.save()
    messages.success(request, f'Alerta marcada como {alerta.get_estado_display()}.')
    return redirect('mantenimiento:alertas')

@login_required
def tipo_servicio_list(request):
    tipos = TipoServicio.objects.filter(activo=True).order_by('nombre')
    return render(request, 'mantenimiento/tipos.html', {'tipos': tipos})

@login_required
def tipo_servicio_crear(request):
    form = TipoServicioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Nuevo plan de mantenimiento creado.')
        return redirect('mantenimiento:tipos')
    return render(request, 'mantenimiento/form_tipo.html', {'form': form, 'title': 'Nuevo Plan'})

@login_required
def tipo_servicio_editar(request, pk):
    tipo = get_object_or_404(TipoServicio, pk=pk)
    form = TipoServicioForm(request.POST or None, instance=tipo)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Plan {tipo.nombre} actualizado.')
        return redirect('mantenimiento:tipos')
    return render(request, 'mantenimiento/form_tipo.html', {'form': form, 'title': f'Editar: {tipo.nombre}'})


@login_required
def alerta_eliminar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar alertas.')
        return redirect('mantenimiento:alertas')

    if request.method != 'POST':
        messages.warning(request, 'Método no permitido.')
        return redirect('mantenimiento:alertas')

    alerta = get_object_or_404(AlertaMantenimiento, pk=pk)
    vehiculo_placa = alerta.vehiculo.patente
    servicio = alerta.tipo_servicio.nombre
    alerta.delete()
    messages.success(request, f'Alerta de "{servicio}" para {vehiculo_placa} eliminada.')
    return redirect('mantenimiento:alertas')


@login_required
def tipo_servicio_eliminar(request, pk):
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden eliminar planes de servicio.')
        return redirect('mantenimiento:tipos')

    if request.method != 'POST':
        messages.warning(request, 'Método no permitido.')
        return redirect('mantenimiento:tipos')

    tipo = get_object_or_404(TipoServicio, pk=pk)
    nombre = tipo.nombre
    tiene_alertas = tipo.alertas.exists()

    if tiene_alertas:
        tipo.activo = False
        tipo.save()
        messages.info(request, f'El plan "{nombre}" tiene alertas asociadas, por lo que fue desactivado.')
    else:
        tipo.delete()
        messages.success(request, f'Plan de servicio "{nombre}" eliminado.')

    return redirect('mantenimiento:tipos')
