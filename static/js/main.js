/* 
   ==========================================================================
   El Taller del Maestro - Scripts Principales (main.js)
   ========================================================================== 
*/

// ── Sidebar Toggle ──
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;
  sidebar.classList.toggle('open');
  if (backdrop) {
    backdrop.classList.toggle('hidden');
  }
}

// ── Modales ──
function openModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
  setTimeout(() => {
    const firstInput = overlay.querySelector('input:not([type=hidden]), select, textarea');
    if (firstInput) firstInput.focus();
  }, 120);
}

function closeModal(modalId) {
  const overlay = document.getElementById(modalId);
  if (!overlay) return;
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// Clic fuera del contenido en modal (Overlay)
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList.contains('modal-overlay')) {
    const redirectUrl = e.target.getAttribute('data-backdrop-redirect');
    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      e.target.classList.remove('open');
      document.body.style.overflow = '';
    }
  }
});

// Cierre con Tecla Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      const redirectUrl = m.getAttribute('data-backdrop-redirect');
      if (redirectUrl) {
        window.location.href = redirectUrl;
      } else {
        m.classList.remove('open');
      }
    });
    document.body.style.overflow = '';
    closeLightbox();
  }
});

// ── Lightbox (Visor de Fotos Pro) ──
function openLightbox(src, alt) {
  const overlay = document.getElementById('lightbox-overlay');
  const img = document.getElementById('lightbox-img');
  const caption = document.getElementById('lightbox-caption');
  if (!overlay || !img) return;
  img.src = src;
  img.alt = alt || 'Imagen';
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

// Inicialización en Carga del Documento
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar Lightbox en elementos con atributo data-lightbox
  document.querySelectorAll('[data-lightbox]').forEach(el => {
    el.style.cursor = 'zoom-in';
    el.addEventListener('click', function(e) {
      e.preventDefault();
      const src = this.dataset.lightbox || this.src || this.href;
      const alt = this.dataset.alt || this.alt || '';
      openLightbox(src, alt);
    });
  });

  // Inicializar Lucide Icons si está disponible
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});
