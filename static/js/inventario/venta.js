/* ==========================================================================
   Inventario Module - Venta JS
   ========================================================================== */

function calculateSaleSubtotal() {
  const qtyInput = document.getElementById('id_cantidad');
  const priceInput = document.getElementById('id_precio_unitario');
  const totalDisplay = document.getElementById('sale-total-display');

  if (qtyInput && priceInput && totalDisplay) {
    const qty = parseFloat(qtyInput.value) || 0;
    const price = parseFloat(priceInput.value) || 0;
    const total = qty * price;
    totalDisplay.textContent = '$' + total.toFixed(2);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const qtyInput = document.getElementById('id_cantidad');
  const priceInput = document.getElementById('id_precio_unitario');

  if (qtyInput) qtyInput.addEventListener('input', calculateSaleSubtotal);
  if (priceInput) priceInput.addEventListener('input', calculateSaleSubtotal);
});
