/**
 * Lógica interactiva para formularios de inventario (Repuestos, Neumáticos y Llantas)
 * - Autogeneración INSTANTÁNEA (0 ms, sin lag) del Código SKU: [FAMILIA]-[SUBFAMILIA/ESPECIFICACIÓN]-[CORRELATIVO]
 * - Verificación asíncrona de correlativo en segundo plano.
 * - Margen de ganancia en tiempo real.
 */
document.addEventListener('DOMContentLoaded', function () {
  const categoriaSelect = document.getElementById('id_categoria');
  const skuInput = document.getElementById('id_codigo_sku');
  const costoInput = document.getElementById('id_precio_costo');
  const ventaInput = document.getElementById('id_precio_venta');
  const btnAutogenerar = document.getElementById('btn-autogenerar-sku');
  const livePreview = document.getElementById('sku-live-preview');
  const liveText = document.getElementById('sku-live-text');

  const isRepuesto = !!document.getElementById('id_marca_repuesto');
  const isNeumatico = !!document.getElementById('id_ancho');
  const isLlanta = !!document.getElementById('id_rin');

  let skuModificadoManualmente = false;

  // Si ya tiene un valor inicial guardado (ej: modo edición), no pisarlo automáticamente
  if (skuInput && skuInput.value.trim() && !skuInput.value.trim().endsWith('-')) {
    skuModificadoManualmente = true;
  }

  if (skuInput) {
    skuInput.addEventListener('input', function () {
      if (this.value.trim() && !this.value.trim().endsWith('-')) {
        skuModificadoManualmente = true;
      } else {
        skuModificadoManualmente = false;
        actualizarSkuInstantaneo();
      }
    });
  }

  // ── 1. CÁLCULO INSTANTÁNEO EN CLIENTE (0 MILISEGUNDOS) ──────────────────
  function obtenerPrefijoFamilia() {
    let prefijo = 'REP';
    if (categoriaSelect && categoriaSelect.selectedIndex >= 0) {
      const optText = categoriaSelect.options[categoriaSelect.selectedIndex].textContent || '';
      const match = optText.match(/\[([A-Za-z0-9_]{2,6})\]/);
      if (match) {
        return match[1].toUpperCase();
      }
    }
    if (isNeumatico) return 'NEU';
    if (isLlanta) return 'LLA';
    return prefijo;
  }

  function obtenerSubfamilia() {
    if (isRepuesto) {
      const marcaEl = document.getElementById('id_marca_repuesto');
      const marca = marcaEl ? marcaEl.value.trim().toUpperCase() : '';
      return marca.replace(/[^A-Z0-9]/g, '').slice(0, 8) || 'GEN';
    }
    if (isNeumatico) {
      const a = (document.getElementById('id_ancho') || {}).value || '205';
      const p = (document.getElementById('id_perfil') || {}).value || '55';
      const d = (document.getElementById('id_diametro') || {}).value || '16';
      const tipoEl = document.getElementById('id_tipo');
      const t = tipoEl && tipoEl.value ? tipoEl.value.toUpperCase() : 'AT';
      return `${a}${p}R${d}-${t}`;
    }
    if (isLlanta) {
      const r = (document.getElementById('id_rin') || {}).value || '17';
      const sfEl = document.getElementById('id_subfamilia');
      const sf = sfEl && sfEl.value ? sfEl.value.toUpperCase() : 'ALU';
      const apEl = document.getElementById('id_apernadura');
      const ap = apEl ? apEl.value.toUpperCase().replace(/[^A-Z0-9]/g, '') : '5X114';
      return `${r}IN-${sf}-${ap}`;
    }
    return 'GEN';
  }

  let correlativoActual = '001';

  function actualizarSkuInstantaneo(forzar) {
    if (!skuInput) return;
    if (skuModificadoManualmente && !forzar) return;

    const prefijo = obtenerPrefijoFamilia();
    const sub = obtenerSubfamilia();
    const skuCalculado = `${prefijo}-${sub}-${correlativoActual}`;

    // Actualización inmediata (0 ms) en el input
    skuInput.value = skuCalculado;

    if (livePreview && liveText) {
      liveText.textContent = `SKU generado en vivo: ${skuCalculado}`;
      livePreview.classList.remove('d-none');
    }

    // Consulta en segundo plano (asíncrona) para asegurar el correlativo exacto
    verificarCorrelativoServidor(prefijo, sub);
  }

  // ── 2. VERIFICACIÓN EN SEGUNDO PLANO (NON-BLOCKING) ────────────────────
  let backgroundTimer = null;
  function verificarCorrelativoServidor(prefijo, sub) {
    clearTimeout(backgroundTimer);
    backgroundTimer = setTimeout(() => {
      let tipoParam = isNeumatico ? 'NEUMATICO' : isLlanta ? 'LLANTA' : 'REPUESTO';
      let catId = (categoriaSelect && categoriaSelect.value) ? categoriaSelect.value : '';
      let extra = '';

      if (isNeumatico) {
        const a = (document.getElementById('id_ancho') || {}).value || '205';
        const p = (document.getElementById('id_perfil') || {}).value || '55';
        const d = (document.getElementById('id_diametro') || {}).value || '16';
        const t = (document.getElementById('id_tipo') || {}).value || 'AT';
        extra = `&ancho=${a}&perfil=${p}&diametro=${d}&tipo_neu=${t}`;
      } else if (isLlanta) {
        const r = (document.getElementById('id_rin') || {}).value || '17';
        const sf = (document.getElementById('id_subfamilia') || {}).value || 'ALU';
        const ap = (document.getElementById('id_apernadura') || {}).value || '5X114';
        extra = `&rin=${r}&subfamilia=${sf}&apernadura=${ap}`;
      } else {
        const marcaEl = document.getElementById('id_marca_repuesto');
        const marca = marcaEl ? marcaEl.value.trim() : '';
        extra = `&marca=${encodeURIComponent(marca)}`;
      }

      const url = `/inventario/ajax/sugerir-sku/?tipo=${tipoParam}&categoria_id=${encodeURIComponent(catId)}${extra}`;

      fetch(url)
        .then(res => res.json())
        .then(data => {
          if (data && data.correlativo && data.correlativo !== correlativoActual) {
            correlativoActual = data.correlativo;
            if (!skuModificadoManualmente) {
              const prefijoActual = obtenerPrefijoFamilia();
              const subActual = obtenerSubfamilia();
              skuInput.value = `${prefijoActual}-${subActual}-${correlativoActual}`;
              if (liveText) {
                liveText.textContent = `SKU generado en vivo: ${skuInput.value}`;
              }
            }
          }
        })
        .catch(() => {});
    }, 150);
  }

  // ── 3. LISTENERS INSTANTÁNEOS (0 ms de respuesta) ───────────────────────
  if (categoriaSelect) {
    categoriaSelect.addEventListener('change', () => actualizarSkuInstantaneo(false));
  }

  if (isRepuesto) {
    const marcaInput = document.getElementById('id_marca_repuesto');
    if (marcaInput) {
      marcaInput.addEventListener('input', () => actualizarSkuInstantaneo(false));
    }
  }

  if (isNeumatico) {
    ['id_ancho', 'id_perfil', 'id_diametro', 'id_tipo'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => actualizarSkuInstantaneo(false));
        el.addEventListener('change', () => actualizarSkuInstantaneo(false));
      }
    });
  }

  if (isLlanta) {
    ['id_rin', 'id_subfamilia', 'id_apernadura'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => actualizarSkuInstantaneo(false));
        el.addEventListener('change', () => actualizarSkuInstantaneo(false));
      }
    });
  }

  // Botón explícito "Autogenerar ahora"
  if (btnAutogenerar) {
    btnAutogenerar.addEventListener('click', function (e) {
      e.preventDefault();
      skuModificadoManualmente = false;
      actualizarSkuInstantaneo(true);
    });
  }

  // Ejecución inicial instantánea al abrir el formulario
  if (skuInput && (!skuInput.value.trim() || skuInput.value.trim().endsWith('-'))) {
    actualizarSkuInstantaneo(false);
  }

  // ── 4. CÁLCULO DEL MARGEN DE GANANCIA (0 ms) ─────────────────────────
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
    calcularMargen();
  }
});
