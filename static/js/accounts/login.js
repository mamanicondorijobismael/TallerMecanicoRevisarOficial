/* ==========================================================================
   Accounts Module - Login JS v2.0
   - Toggle de visibilidad de contraseña
   - Auto-completar credenciales demo (solo si el bloque existe)
   - Autofocus inteligente (solo desktop)
   ========================================================================== */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Toggle mostrar/ocultar contraseña ──
    const toggleBtn = document.getElementById('togglePassword');
    const pwdInput  = document.getElementById('password');
    const icon      = document.getElementById('visibilityIcon');

    if (toggleBtn && pwdInput && icon) {
      toggleBtn.addEventListener('click', function () {
        const isPassword = pwdInput.type === 'password';
        pwdInput.type = isPassword ? 'text' : 'password';
        icon.textContent = isPassword ? 'visibility' : 'visibility_off';
        // Mantener el foco en el input
        pwdInput.focus();
      });
    }

    // ── 2. Autofocus solo en desktop (evita abrir teclado en móvil) ──
    const isDesktop = window.matchMedia('(min-width: 992px)').matches;
    const usernameInput = document.getElementById('username');
    if (isDesktop && usernameInput && !usernameInput.value) {
      usernameInput.focus();
    }

    // ── 3. Enter en el campo usuario → foco al password ──
    if (usernameInput && pwdInput) {
      usernameInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          pwdInput.focus();
        }
      });
    }
  });

  // ── 4. Función global para autocompletar credenciales demo ──
  window.fillLogin = function (username, password) {
    const u = document.getElementById('username');
    const p = document.getElementById('password');
    if (u && p) {
      u.value = username;
      p.value = password;
      p.focus();
    }
  };
})();