/* ==========================================================================
   Inventario Module - Categorías JS
   ========================================================================== */

function selectCategoryIcon(name) {
  const iconInput = document.querySelector('input[name="icono"]');
  if (iconInput) iconInput.value = name;

  const preview = document.getElementById('icon-preview');
  if (preview) {
    preview.innerHTML = `<span class="material-symbols-outlined fs-4">${name}</span>`;
  }

  document.querySelectorAll('.icon-selector-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  const activeBtn = document.getElementById('icon-btn-' + name);
  if (activeBtn) {
    activeBtn.classList.add('active');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const iconInput = document.querySelector('input[name="icono"]');
  if (iconInput && iconInput.value) {
    selectCategoryIcon(iconInput.value);
  }
});
