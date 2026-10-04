/* ==========================================================================
   Órdenes Module - Form JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  // Autofocus first input in order form
  const firstInput = document.querySelector('.order-form-container select, .order-form-container input');
  if (firstInput) {
    firstInput.focus();
  }
});
