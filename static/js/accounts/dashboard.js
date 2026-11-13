
document.addEventListener('DOMContentLoaded', function () {
  var periodSelect = document.getElementById('periodSelect');
  if (periodSelect && !periodSelect.dataset.bound) {
    periodSelect.dataset.bound = '1';
    periodSelect.addEventListener('change', function () {
      try {
        var url = new URL(window.location.href);
        url.searchParams.set('periodo', this.value);
        window.location.href = url.toString();
      } catch (e) {
        console.warn('No se pudo actualizar el período:', e);
      }
    });
  }

  document.querySelectorAll('.kpi-card').forEach(function (card) {
    card.addEventListener('mouseenter', function () {
      card.style.willChange = 'transform, box-shadow';
    });
    card.addEventListener('mouseleave', function () {
      card.style.willChange = 'auto';
    });
  });

  document.querySelectorAll('.kpi-value').forEach(function (el) {
    var text = el.textContent.trim();
    if (!/^\d+$/.test(text)) return;
    var target = parseInt(text, 10);
    if (target < 10) return;
    var start = Math.max(0, Math.floor(target * 0.7));
    var duration = 700;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.floor(start + (target - start) * eased);
      el.textContent = current.toLocaleString('es-BO');
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString('es-BO');
    }
    requestAnimationFrame(step);
  });
});