/* ==========================================================================
   Inventario Module - Lista JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const catSelect = document.getElementById('categoriaFilterSelect');
  if (catSelect) {
    catSelect.addEventListener('change', function() {
      this.form.submit();
    });
  }
});
