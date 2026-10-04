/* ==========================================================================
   Accounts Module - Dashboard JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  // Period filter change handler
  const periodSelect = document.getElementById('periodSelect');
  if (periodSelect) {
    periodSelect.addEventListener('change', function() {
      window.location.href = '?periodo=' + this.value;
    });
  }
});
