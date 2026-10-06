/* ==========================================================================
   Mantenimiento Module - Alertas JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const modalAlerta = document.getElementById('modalEliminarAlerta');
  if (modalAlerta) {
    modalAlerta.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const servicio = button.getAttribute('data-alerta-servicio');
      const vehiculo = button.getAttribute('data-alerta-vehiculo');
      const url = button.getAttribute('data-alerta-url');

      document.getElementById('deleteAlertaServicio').textContent = servicio || '';
      document.getElementById('deleteAlertaVehiculo').textContent = vehiculo || '';
      document.getElementById('formEliminarAlerta').action = url || '';
    });
  }

  const modalTipo = document.getElementById('modalEliminarTipo');
  if (modalTipo) {
    modalTipo.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const nombre = button.getAttribute('data-tipo-nombre');
      const precio = button.getAttribute('data-tipo-precio');
      const url = button.getAttribute('data-tipo-url');

      document.getElementById('deleteTipoNombre').textContent = nombre || '';
      document.getElementById('deleteTipoPrecio').textContent = precio ? '$' + precio : '';
      document.getElementById('formEliminarTipo').action = url || '';
    });
  }
});
