/* ==========================================================================
   El Taller del Maestro - Base JS
   ========================================================================== */

// ── Sidebar Toggle for Mobile ──
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;
  sidebar.classList.toggle('show');
  if (backdrop) {
    backdrop.classList.toggle('show');
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

// ── Global Event Listeners ──
document.addEventListener('DOMContentLoaded', function() {
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

  // ESC key handler for modals/lightbox
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeLightbox();
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
