/* ==========================================================================
   Órdenes Module - Detalle JS (Búsqueda AJAX de Repuestos Internos)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const filtroInput = document.getElementById('filtro-producto-ajax') || document.getElementById('filtro-producto');
  const productoSelect = document.getElementById('id_producto') || document.querySelector('select[name="producto"]');
  const modalProducto = document.getElementById('modal-producto');
  const listGroupResultados = document.getElementById('resultado-busqueda-repuesto');

  if (filtroInput && productoSelect) {
    let debounceTimer = null;

    filtroInput.addEventListener('input', function() {
      const q = this.value.trim();
      clearTimeout(debounceTimer);

      if (!q) {
        if (listGroupResultados) {
          listGroupResultados.classList.add('d-none');
          listGroupResultados.innerHTML = '';
        }
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/inventario/ajax/buscar-repuestos/?q=${encodeURIComponent(q)}`)
          .then(res => res.json())
          .then(data => {
            if (listGroupResultados) {
              listGroupResultados.innerHTML = '';
              if (!data.results || data.results.length === 0) {
                listGroupResultados.innerHTML = '<div class="list-group-item list-group-item-light small text-muted">No se encontraron repuestos con stock.</div>';
                listGroupResultados.classList.remove('d-none');
                return;
              }

              data.results.forEach(item => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center py-2 px-3 small';
                btn.innerHTML = `
                  <div>
                    <span class="badge bg-secondary-subtle text-secondary font-monospace me-1">[${item.sku}]</span>
                    <strong>${item.nombre}</strong>
                  </div>
                  <div class="text-end">
                    <span class="badge bg-success-subtle text-success me-1">Stock: ${item.stock}</span>
                    <span class="text-muted">Bs ${item.precio.toFixed(2)}</span>
                  </div>
                `;
                btn.addEventListener('click', function(e) {
                  e.preventDefault();
                  // Preseleccionar en el select
                  let found = false;
                  for (let i = 0; i < productoSelect.options.length; i++) {
                    if (productoSelect.options[i].value == item.id) {
                      productoSelect.selectedIndex = i;
                      found = true;
                      break;
                    }
                  }
                  if (!found) {
                    const opt = new Option(`[${item.sku}] ${item.nombre} (Stock: ${item.stock})`, item.id, true, true);
                    productoSelect.add(opt);
                  }
                  listGroupResultados.classList.add('d-none');
                  filtroInput.value = `[${item.sku}] ${item.nombre}`;
                });
                listGroupResultados.appendChild(btn);
              });
              listGroupResultados.classList.remove('d-none');
            }
          })
          .catch(err => console.error('Error buscando repuestos:', err));
      }, 250);
    });

    if (modalProducto) {
      modalProducto.addEventListener('shown.bs.modal', function() {
        filtroInput.value = '';
        if (listGroupResultados) {
          listGroupResultados.innerHTML = '';
          listGroupResultados.classList.add('d-none');
        }
        filtroInput.focus();
      });
    }
  }
});
