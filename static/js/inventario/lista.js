
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Modal de eliminación ──
    const modalEl = document.getElementById('modalEliminarProducto');
    if (modalEl) {
      modalEl.addEventListener('show.bs.modal', function (event) {
        const btn = event.relatedTarget;
        if (!btn) return;

        const sku     = btn.getAttribute('data-producto-sku')    || '—';
        const nombre  = btn.getAttribute('data-producto-nombre') || '—';
        const stock   = btn.getAttribute('data-producto-stock')  || '0';
        const url     = btn.getAttribute('data-producto-url')    || '#';

        const skuEl    = document.getElementById('deleteProductoSku');
        const nombreEl = document.getElementById('deleteProductoNombre');
        const stockEl  = document.getElementById('deleteProductoStock');
        const formEl   = document.getElementById('formEliminarProducto');

        if (skuEl)    skuEl.textContent    = sku;
        if (nombreEl) nombreEl.textContent = nombre;
        if (stockEl)  stockEl.textContent  = stock;
        if (formEl)   formEl.action        = url;
      });
    }
    document.querySelectorAll('[data-auto-submit]').forEach(function (select) {
      select.addEventListener('change', function () {
        if (this.form) this.form.submit();
      });
    });

  });
})();