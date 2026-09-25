/* 
   ==========================================================================
   El Taller del Maestro - Lógica de Inicio de Sesión (login.js)
   ========================================================================== 
*/

document.addEventListener('DOMContentLoaded', function() {
  const togglePassword = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('password');
  const visibilityIcon = document.getElementById('visibilityIcon');

  if (togglePassword && passwordInput && visibilityIcon) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      visibilityIcon.textContent = type === 'password' ? 'visibility_off' : 'visibility';
    });
  }
});

function fillLogin(u, p) {
  const userInput = document.getElementById('username');
  const passInput = document.getElementById('password');
  if (userInput) userInput.value = u;
  if (passInput) passInput.value = p;
}
