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
});
