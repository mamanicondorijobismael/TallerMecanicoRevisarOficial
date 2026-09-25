from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Reserva
from .forms import ReservaForm


@login_required
def reserva_list(request):
    estado_filter = request.GET.get('estado', '')
    query = request.GET.get('q', '')
    qs = Reserva.objects.select_related('cliente', 'vehiculo').order_by('fecha_hora')
    if estado_filter:
        qs = qs.filter(estado=estado_filter)
    if query:
        from django.db.models import Q
        qs = qs.filter(Q(cliente__nombre_razon_social__icontains=query) | Q(vehiculo__patente__icontains=query))
    return render(request, 'reservas/lista.html', {'reservas': qs, 'query': query, 'estado_filter': estado_filter, 'hoy': timezone.now().date()})


@login_required
def reserva_crear(request):
    form = ReservaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        reserva = form.save()
        messages.success(request, f'Reserva creada para {reserva.cliente} el {reserva.fecha_hora.strftime("%d/%m/%Y %H:%M")}.')
        return redirect('reservas:lista')
    return render(request, 'reservas/form.html', {'form': form, 'title': 'Nueva Reserva'})


@login_required
def reserva_editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    form = ReservaForm(request.POST or None, instance=reserva)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada.')
        return redirect('reservas:lista')
    return render(request, 'reservas/form.html', {'form': form, 'title': f'Editar Reserva', 'reserva': reserva})
