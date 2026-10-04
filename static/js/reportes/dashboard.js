/* ==========================================================================
   Reportes Module - Dashboard JS (Chart.js integrations)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
  const labelsEl = document.getElementById('labels-data');
  const ingresosEl = document.getElementById('ingresos-data');
  const ordenesLabelsEl = document.getElementById('ordenes-labels');
  const ordenesDataEl = document.getElementById('ordenes-data');

  if (labelsEl && ingresosEl) {
    const labels = JSON.parse(labelsEl.textContent);
    const dataIngresos = JSON.parse(ingresosEl.textContent);
    const canvasIngresos = document.getElementById('ingresosChart');

    if (canvasIngresos) {
      new Chart(canvasIngresos.getContext('2d'), {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Ingresos ($)',
            data: dataIngresos,
            borderColor: '#0D284E',
            backgroundColor: 'rgba(13, 40, 78, 0.08)',
            borderWidth: 2.5,
            pointBackgroundColor: '#F2B705',
            pointBorderColor: '#0D284E',
            pointRadius: 4,
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 10 } } },
            x: { grid: { display: false }, ticks: { font: { size: 10 } } }
          }
        }
      });
    }
  }

  if (ordenesLabelsEl && ordenesDataEl) {
    const estados = JSON.parse(ordenesLabelsEl.textContent);
    const datosEstados = JSON.parse(ordenesDataEl.textContent);
    const canvasOrdenes = document.getElementById('ordenesChart');

    if (canvasOrdenes) {
      new Chart(canvasOrdenes.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: estados,
          datasets: [{
            data: datosEstados,
            backgroundColor: ['#F2B705', '#0D284E', '#DC2626', '#16A34A', '#7C3AED'],
            borderWidth: 2,
            borderColor: '#ffffff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
          },
          cutout: '68%'
        }
      });
    }
  }
});
