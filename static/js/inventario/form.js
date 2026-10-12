/**
 * Lógica interactiva para formularios de inventario (Repuestos y Neumáticos)
 * - Actualización dinámica del Código SKU según la sigla de la categoría seleccionada (ej. FRE-001).
 * - Cálculo automático y en tiempo real del margen de ganancia.
 */
document.addEventListener('DOMContentLoaded', function () {
  const categoriaSelect = document.getElementById('id_categoria');
  const skuInput = document.getElementById('id_codigo_sku');
  const costoInput = document.getElementById('id_precio_costo');
  const ventaInput = document.getElementById('id_precio_venta');

  // Mapeo auxiliar por si las opciones no tienen corchetes
  const prefixMap = {
    'freno': 'FRE',
    'frenos': 'FRE',
    'filtro': 'FIL',
    'filtros': 'FIL',
    'lubricante': 'LUB',
    'lubricantes': 'LUB',
    'motor': 'MOT',
    'neumatico': 'NEU',
    'neumaticos': 'NEU',
    'neumático': 'NEU',
    'neumáticos': 'NEU',
    'llanta': 'NEU',
    'llantas': 'NEU',
    'suspension': 'SUS',
    'suspensión': 'SUS',
    'electrico': 'ELE',
    'eléctrico': 'ELE',
    'transmision': 'TRA',
    'transmisión': 'TRA'
  };

  function extraerPrefijo(texto) {
    if (!texto) return 'REP';
    // Buscar si viene en formato [FRE] o [FIL]
    const match = texto.match(/\[([A-Za-z0-9_]{2,6})\]/);
    if (match) {
      return match[1].toUpperCase();
    }
    // Buscar por coincidencia semántica
    const lower = texto.toLowerCase();
    for (const [key, val] of Object.entries(prefixMap)) {
      if (lower.includes(key)) {
        return val;
      }
    }
    // Si no coincide, tomar las primeras 3 letras
    const clean = texto.trim().replace(/[^a-zA-Z]/g, '');
    return clean ? clean.slice(0, 3).toUpperCase() : 'REP';
  }

  function actualizarPrefijoSku(forzar) {
    if (!categoriaSelect || !skuInput) return;
    const selectedOption = categoriaSelect.options[categoriaSelect.selectedIndex];
    if (!selectedOption || !selectedOption.value) return;

    const prefijo = extraerPrefijo(selectedOption.textContent);
    skuInput.placeholder = `Ej: ${prefijo}-001`;

    const valActual = skuInput.value.trim().toUpperCase();

    // Extraer cualquier número existente
    const matchNumero = valActual.match(/\d+/);
    const numeroStr = matchNumero ? matchNumero[0].padStart(3, '0') : '';

    if (forzar || !valActual || valActual.endsWith('-') || /^[A-Z]{2,4}-?$/.test(valActual)) {
      skuInput.value = numeroStr ? `${prefijo}-${numeroStr}` : `${prefijo}-`;
    } else if (numeroStr && !valActual.startsWith(`${prefijo}-`)) {
      skuInput.value = `${prefijo}-${numeroStr}`;
    }
  }

  if (categoriaSelect && skuInput) {
    categoriaSelect.addEventListener('change', function () {
      actualizarPrefijoSku(false);
    });

    // Si el campo SKU está vacío al enfocar o al cargar
    skuInput.addEventListener('focus', function () {
      if (!skuInput.value.trim() && categoriaSelect && categoriaSelect.selectedIndex >= 0) {
        actualizarPrefijoSku(false);
      }
    });

    // Al cargar la página, si no tiene nada escrito o es nuevo registro
    if (!skuInput.value.trim() && categoriaSelect && categoriaSelect.selectedIndex > 0) {
      actualizarPrefijoSku(false);
    }
  }

  // Margen de ganancia en tiempo real
  function calcularMargen() {
    if (!costoInput || !ventaInput) return;
    const costo = parseFloat(costoInput.value) || 0;
    const venta = parseFloat(ventaInput.value) || 0;
    const badgeMargen = document.getElementById('badge-margen-calculado');
    if (badgeMargen) {
      if (venta > 0) {
        const margen = (((venta - costo) / venta) * 100).toFixed(1);
        badgeMargen.textContent = `Margen: ${margen}%`;
        badgeMargen.className = `badge ${margen >= 20 ? 'bg-success' : margen > 0 ? 'bg-warning text-dark' : 'bg-danger'}`;
      } else {
        badgeMargen.textContent = 'Margen: 0%';
        badgeMargen.className = 'badge bg-secondary';
      }
    }
  }

  if (costoInput && ventaInput) {
    costoInput.addEventListener('input', calcularMargen);
    ventaInput.addEventListener('input', calcularMargen);
  }
});
