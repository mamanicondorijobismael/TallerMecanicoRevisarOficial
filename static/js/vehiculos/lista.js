/* ==========================================================================
   Vehículos Module - Lista JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const fotoInput = document.getElementById('vehiculo-foto-input');
  const previewImg = document.getElementById('vehiculo-foto-preview');
  const previewPlaceholder = document.getElementById('vehiculo-foto-placeholder');
  const dropzone = document.getElementById('vehiculo-dropzone');
  const removeBtn = document.getElementById('vehiculo-foto-remove');

  if (fotoInput) {
    fotoInput.addEventListener('change', function(e) {
      handleVehiculoImagePreview(this.files[0]);
    });
  }

  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0 && fotoInput) {
        fotoInput.files = files;
        handleVehiculoImagePreview(files[0]);
      }
    });
  }

  if (removeBtn) {
    removeBtn.addEventListener('click', function(e) {
      e.preventDefault();
      if (fotoInput) fotoInput.value = '';
      if (previewImg) {
        previewImg.src = '';
        previewImg.classList.add('d-none');
      }
      if (previewPlaceholder) {
        previewPlaceholder.classList.remove('d-none');
      }
      removeBtn.classList.add('d-none');
    });
  }

  function handleVehiculoImagePreview(file) {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = function(e) {
      if (previewImg) {
        previewImg.src = e.target.result;
        previewImg.classList.remove('d-none');
      }
      if (previewPlaceholder) {
        previewPlaceholder.classList.add('d-none');
      }
      if (removeBtn) {
        removeBtn.classList.remove('d-none');
      }
    };
    reader.readAsDataURL(file);
  }
});

document.addEventListener('DOMContentLoaded', function () {
  const modalEliminar = document.getElementById('modalEliminarVehiculo');
  if (modalEliminar) {
    modalEliminar.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      if (!button) return;

      const placa = button.getAttribute('data-vehiculo-placa');
      const info = button.getAttribute('data-vehiculo-info');
      const url = button.getAttribute('data-vehiculo-url');

      document.getElementById('deleteVehiculoPlaca').textContent = placa || '';
      document.getElementById('deleteVehiculoInfo').textContent = info || '';
      document.getElementById('formEliminarVehiculo').action = url || '';
    });
  }
});
