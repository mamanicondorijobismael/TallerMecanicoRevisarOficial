/* ==========================================================================
   Accounts Module - Login JS
   ========================================================================== */

function fillLogin(user, pass) {
  const userInput = document.getElementById('username');
  const passInput = document.getElementById('password');
  if (userInput) userInput.value = user;
  if (passInput) passInput.value = pass;
}

document.addEventListener('DOMContentLoaded', function() {
  const toggleBtn = document.getElementById('togglePassword');
  const passInput = document.getElementById('password');
  const visibilityIcon = document.getElementById('visibilityIcon');

  if (toggleBtn && passInput) {
    toggleBtn.addEventListener('click', function() {
      const isPassword = passInput.getAttribute('type') === 'password';
      passInput.setAttribute('type', isPassword ? 'text' : 'password');
      if (visibilityIcon) {
        visibilityIcon.textContent = isPassword ? 'visibility' : 'visibility_off';
      }
    });
  }
});
