/* ==========================================================================
   Reservas Module - Lista JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const modalEliminar = document.getElementById('modalEliminarReserva');
  if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const cliente = button.getAttribute('data-reserva-cliente');
      const fecha = button.getAttribute('data-reserva-fecha');
      const vehiculo = button.getAttribute('data-reserva-vehiculo');
      const url = button.getAttribute('data-reserva-url');

      document.getElementById('deleteReservaCliente').textContent = cliente || '';
      document.getElementById('deleteReservaFecha').textContent = fecha || '';
      document.getElementById('deleteReservaVehiculo').textContent = vehiculo || '';
      document.getElementById('formEliminarReserva').action = url || '';
    });
  }
});
