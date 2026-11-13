/* ==========================================================================
   El Taller del Maestro - Base JS & Navigation Interactivity
   ========================================================================== */

// ── Mobile Drawer Toggle ──
function toggleMobileDrawer() {
  const drawer = document.getElementById('mobile-drawer');
  const overlay = document.getElementById('mobile-drawer-overlay');
  if (!drawer) return;
  const isShowing = drawer.classList.contains('show');
  if (isShowing) {
    drawer.classList.remove('show');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
  } else {
    drawer.classList.add('show');
    if (overlay) overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
}

// Backward compatibility with previous toggleSidebar calls
function toggleSidebar() {
  toggleMobileDrawer();
}

// ── Capsule Navigation Dropdown Toggle ──
function toggleCapsuleDropdown(element, event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  const parentItem = element.closest('.nav-capsule-item');
  if (!parentItem) return;
  const menu = parentItem.querySelector('.capsule-dropdown-menu');
  if (!menu) return;

  const isOpen = menu.classList.contains('show');

  // Close any other open dropdowns first
  document.querySelectorAll('.capsule-dropdown-menu.show').forEach(m => {
    if (m !== menu) m.classList.remove('show');
  });

  if (isOpen) {
    menu.classList.remove('show');
  } else {
    menu.classList.add('show');
  }
}

// ── Lightbox (Image preview) ──
function openLightbox(src, alt) {
  const overlay = document.getElementById('lightbox-overlay');
  const img = document.getElementById('lightbox-img');
  const caption = document.getElementById('lightbox-caption');
  if (!overlay || !img) return;
  img.src = src;
  img.alt = alt || 'Vista previa';
  if (caption) {
    caption.textContent = alt || '';
    caption.style.display = alt ? 'block' : 'none';
  }
  overlay.style.display = 'flex';
  overlay.classList.add('show', 'open');
  document.body.style.overflow = 'hidden';
}

function closeLightbox(e) {
  if (e && e.target !== document.getElementById('lightbox-overlay') && e.target !== document.getElementById('lightbox-close') && !e.target.closest('#lightbox-close')) return;
  const overlay = document.getElementById('lightbox-overlay');
  if (overlay) {
    overlay.classList.remove('show', 'open');
    overlay.style.display = 'none';
    document.body.style.overflow = '';
  }
}

// ── Modales ──
function openModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.classList.add('open', 'show');
  document.body.style.overflow = 'hidden';
  setTimeout(() => {
    const firstInput = overlay.querySelector('input:not([type=hidden]), select, textarea');
    if (firstInput) firstInput.focus();
  }, 120);
}

function closeModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.classList.remove('open', 'show');
  document.body.style.overflow = '';
}

// ── Global Event Listeners ──
document.addEventListener('DOMContentLoaded', function() {
  // Close capsule dropdowns when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-capsule-item')) {
      document.querySelectorAll('.capsule-dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });

  // Lightbox triggers
  document.querySelectorAll('[data-lightbox]').forEach(el => {
    el.style.cursor = 'zoom-in';
    el.addEventListener('click', function(e) {
      e.preventDefault();
      const src = this.dataset.lightbox || this.src || this.href;
      const alt = this.dataset.alt || this.alt || '';
      openLightbox(src, alt);
    });
  });

  // Modal backdrop click
  document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('modal-overlay')) {
      const redirectUrl = e.target.getAttribute('data-backdrop-redirect');
      if (redirectUrl) {
        window.location.href = redirectUrl;
      } else {
        e.target.classList.remove('open', 'show');
        document.body.style.overflow = '';
      }
    }
  });

  // ESC key handler for modals/lightbox/dropdowns
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.capsule-dropdown-menu.show').forEach(m => {
        m.classList.remove('show');
      });
      document.querySelectorAll('.modal-overlay.open, .modal-overlay.show').forEach(m => {
        const redirectUrl = m.getAttribute('data-backdrop-redirect');
        if (redirectUrl) {
          window.location.href = redirectUrl;
        } else {
          m.classList.remove('open', 'show');
        }
      });
      document.body.style.overflow = '';
      closeLightbox();
      const drawer = document.getElementById('mobile-drawer');
      if (drawer && drawer.classList.contains('show')) {
        toggleMobileDrawer();
      }
    }
  });

  // Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }
    }, 5000);
  });
});
