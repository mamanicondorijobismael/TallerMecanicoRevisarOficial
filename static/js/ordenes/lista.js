/* ==========================================================================
   Órdenes Module - Lista JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const filterForm = document.getElementById('ordenesFilterForm');
  const estadoSelect = document.getElementById('estadoFilterSelect');

  if (estadoSelect && filterForm) {
    estadoSelect.addEventListener('change', function() {
      filterForm.submit();
    });
  }

  const modalEliminar = document.getElementById('modalEliminarOrden');
  if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const numero = button.getAttribute('data-orden-numero');
      const info = button.getAttribute('data-orden-info');
      const estado = button.getAttribute('data-orden-estado');
      const url = button.getAttribute('data-orden-url');

      document.getElementById('deleteOrdenNumero').textContent = 'OT #' + (numero || '');
      document.getElementById('deleteOrdenInfo').textContent = info || '';
      document.getElementById('deleteOrdenEstado').textContent = estado || '';
      document.getElementById('formEliminarOrden').action = url || '';
    });
  }
});
