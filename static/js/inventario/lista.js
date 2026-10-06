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

  const modalEliminar = document.getElementById('modalEliminarProducto');
  if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const nombre = button.getAttribute('data-producto-nombre');
      const sku = button.getAttribute('data-producto-sku');
      const url = button.getAttribute('data-producto-url');

      document.getElementById('deleteProductoNombre').textContent = nombre || '';
      document.getElementById('deleteProductoSku').textContent = sku || '';
      document.getElementById('formEliminarProducto').action = url || '';
    });
  }
});
