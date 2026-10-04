/* ==========================================================================
   Vehículos Module - Form JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const fotoInput = document.getElementById('id_foto');
  const previewImg = document.getElementById('vehiculo-form-preview-img');
  const previewPlaceholder = document.getElementById('vehiculo-form-preview-placeholder');
  const dropzone = document.getElementById('vehiculo-form-dropzone');
  const removeBtn = document.getElementById('vehiculo-form-foto-remove');

  if (fotoInput) {
    fotoInput.addEventListener('change', function(e) {
      handleVehiculoPreview(this.files[0]);
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
        handleVehiculoPreview(files[0]);
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

  function handleVehiculoPreview(file) {
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
