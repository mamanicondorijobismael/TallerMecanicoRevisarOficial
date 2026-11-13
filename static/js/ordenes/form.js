/* ==========================================================================
   Órdenes Module - Form JS (Autocompletar KM & Toggle de Edición)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const vehiculoSelect = document.querySelector('select[name="vehiculo"]');
  const kmInput = document.querySelector('input[name="kilometraje"]');
  const btnToggleKm = document.getElementById('btn-toggle-km');
  const kmInfoMsg = document.getElementById('km-info-msg');
  const buscarVehiculoInput = document.getElementById('buscar-vehiculo-ajax');

  // Buscador AJAX en tiempo real para el selector de vehículos
  if (buscarVehiculoInput && vehiculoSelect) {
    let timeoutBusqueda = null;
    buscarVehiculoInput.addEventListener('input', function() {
      const q = this.value.trim();
      clearTimeout(timeoutBusqueda);
      if (q.length < 2) {
        // Restaurar opciones completas si limpia
        Array.from(vehiculoSelect.options).forEach(opt => opt.style.display = '');
        return;
      }
      timeoutBusqueda = setTimeout(() => {
        fetch(`/ordenes/ajax/buscar-vehiculos/?q=${encodeURIComponent(q)}`)
          .then(res => res.json())
          .then(data => {
            if (data && data.results) {
              const idsEncontrados = data.results.map(r => String(r.id));
              Array.from(vehiculoSelect.options).forEach(opt => {
                if (!opt.value) {
                  opt.style.display = '';
                } else if (idsEncontrados.includes(opt.value)) {
                  opt.style.display = '';
                } else {
                  opt.style.display = 'none';
                }
              });
              // Si hay coincidencia exacta de 1, pre-seleccionarlo
              if (data.results.length === 1) {
                vehiculoSelect.value = data.results[0].id;
                vehiculoSelect.dispatchEvent(new Event('change'));
              }
            }
          })
          .catch(err => console.error('Error buscando vehículos:', err));
      }, 250);
    });
  }

  if (kmInput) {
    // Por defecto dejar en modo sólo lectura si ya tiene valor o si se autocompleta
    if (kmInput.value && kmInput.value !== '0') {
      kmInput.setAttribute('readonly', 'readonly');
      kmInput.style.backgroundColor = '#f8fafc';
    }

    if (btnToggleKm) {
      btnToggleKm.addEventListener('click', function(e) {
        e.preventDefault();
        if (kmInput.hasAttribute('readonly')) {
          kmInput.removeAttribute('readonly');
          kmInput.style.backgroundColor = '#ffffff';
          kmInput.focus();
          btnToggleKm.innerHTML = '<span class="material-symbols-outlined fs-6 align-middle">lock</span> Bloquear KM';
          if (kmInfoMsg) kmInfoMsg.textContent = 'Modo edición activado. Ingresá el nuevo kilometraje.';
        } else {
          kmInput.setAttribute('readonly', 'readonly');
          kmInput.style.backgroundColor = '#f8fafc';
          btnToggleKm.innerHTML = '<span class="material-symbols-outlined fs-6 align-middle">edit</span> ¿Actualizar KM?';
          if (kmInfoMsg) kmInfoMsg.textContent = 'Kilometraje fijado.';
        }
      });
    }
  }

  if (vehiculoSelect && kmInput) {
    vehiculoSelect.addEventListener('change', function() {
      const vehiculoId = this.value;
      if (!vehiculoId) return;

      fetch(`/ordenes/ajax/vehiculo-km/?id=${vehiculoId}`)
        .then(response => response.json())
        .then(data => {
          if (data && data.km !== undefined) {
            kmInput.value = data.km;
            kmInput.setAttribute('readonly', 'readonly');
            kmInput.style.backgroundColor = '#f8fafc';
            if (btnToggleKm) {
              btnToggleKm.innerHTML = '<span class="material-symbols-outlined fs-6 align-middle">edit</span> ¿Actualizar KM?';
            }
            if (kmInfoMsg) {
              kmInfoMsg.textContent = `Kilometraje registrado previamente: ${data.km} km.`;
            }
          }
        })
        .catch(err => console.error('Error al consultar KM del vehículo:', err));
    });
  }
});
