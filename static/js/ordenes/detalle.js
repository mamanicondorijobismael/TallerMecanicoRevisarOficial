/* ==========================================================================
   Órdenes Module - Detalle JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const filtroInput = document.getElementById('filtro-producto');
  const productoSelect = document.getElementById('id_producto') || document.querySelector('select[name="producto"]');
  const modalProducto = document.getElementById('modal-producto');

  if (filtroInput && productoSelect) {
    // Guardar opciones originales
    const originalOptions = Array.from(productoSelect.options).map(opt => ({
      value: opt.value,
      text: opt.text,
      selected: opt.selected
    }));

    function normalizarTexto(txt) {
      return (txt || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    function filtrarProductos() {
      const query = normalizarTexto(filtroInput.value.trim());
      const selectedValue = productoSelect.value;
      
      // Limpiar select
      productoSelect.innerHTML = '';

      let matchingOptions = originalOptions.filter(opt => {
        if (!opt.value) return true; // Mantener opción vacía ("---------")
        if (!query) return true;
        return normalizarTexto(opt.text).includes(query);
      });

      if (matchingOptions.length === 0 || (matchingOptions.length === 1 && !matchingOptions[0].value)) {
        const noRes = document.createElement('option');
        noRes.value = '';
        noRes.textContent = '⚠️ No se encontraron repuestos con ese filtro';
        noRes.disabled = true;
        noRes.selected = true;
        productoSelect.appendChild(noRes);
      } else {
        matchingOptions.forEach(opt => {
          const optEl = document.createElement('option');
          optEl.value = opt.value;
          optEl.textContent = opt.text;
          if (opt.value === selectedValue) {
            optEl.selected = true;
          }
          productoSelect.appendChild(optEl);
        });

        // Si se filtró y hay opciones válidas, preseleccionar la primera si la anterior no coincide
        if (query && matchingOptions.some(o => o.value)) {
          const firstValid = matchingOptions.find(o => o.value);
          if (firstValid && productoSelect.value !== selectedValue) {
            productoSelect.value = firstValid.value;
          }
        }
      }
    }

    filtroInput.addEventListener('input', filtrarProductos);

    // Al abrir el modal, resetear y enfocar el campo de búsqueda
    if (modalProducto) {
      modalProducto.addEventListener('shown.bs.modal', function() {
        filtroInput.value = '';
        filtrarProductos();
        filtroInput.focus();
      });
    }
  }
});
