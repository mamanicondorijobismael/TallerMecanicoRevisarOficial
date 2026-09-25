# 09. Documentación Técnica y Explicación de Código: App `reportes`

La aplicación `reportes` proporciona análisis gerencial y financiero para la toma de decisiones del dueño del taller: ingresos, costos, margen de ganancia neto, desglose cronológico para gráficos, top de clientes, productos más vendidos, y generación de reportes diarios con respaldos automáticos de base de datos (`backups/`).

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `Sum`, `Count`, `Q`, `F` | Agregación de montos totales facturados, recuento de órdenes agrupadas por estado y filtros condicionales. |
| `django.db.models.functions` | `Abs`, `Coalesce` | `Abs` calcula valores absolutos (ej. convertir salidas negativas en cantidades positivas vendidas); `Coalesce` reemplaza valores nulos `None` por `0`. |
| `django.utils` | `timezone` | Fechas y tiempos sincronizados con la zona horaria del sistema. |
| `datetime` | `timedelta` | Cálculo de rangos dinámicos de días (7, 15, 30, 90 días). |
| `decimal` | `Decimal` | Exactitud en cálculos monetarios de ingresos, costos y ganancias. |
| `shutil`, `os` | `shutil.copy2`, `os.path`, `os.makedirs` | Realiza una copia de seguridad física de la base de datos SQLite en la carpeta `backups/` durante el cierre diario y rota archivos viejos manteniendo los últimos 30 backups. |
| `django.conf` | `settings` | Obtiene la ruta del archivo de base de datos (`settings.DATABASES['default']['NAME']`) y `BASE_DIR`. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/reportes/views.py)

#### 1. `dashboard_reportes(request)` (Líneas 17-107)
- **Control de Acceso**: Restringido exclusivamente al dueño (`if not request.user.es_dueno:`).
- **Cálculo de Ingresos y Costos Reales**:
  - `ingresos = facturas.aggregate(total=Sum('total'))['total']`
  - Suma el costo de compra de todos los repuestos consumidos en las órdenes del período para obtener `costos`.
  - `ganancia = ingresos - costos`
  - `margen = round((ganancia / ingresos * 100), 1)`
- **Ventas de Hoy**: Filtra facturas con fecha igual a la fecha local actual.
- **Series Temporales para Gráficos**: Itera a lo largo de los días del período generando arreglos `labels` (fechas en formato `DD/MM`) y `data_ingresos` (monto acumulado por día) para renderizar gráficos con Chart.js.
- **Top Clientes y Top Repuestos**:
  - Agrupa con `.values('cliente__nombre_razon_social').annotate(total=Sum('total')).order_by('-total')[:5]`.
  - Agrupa salidas de inventario para encontrar los productos de mayor rotación.

#### 2. `reporte_diario(request)` (Líneas 110-184)
- **Backup Automático Diario (Líneas 116-139)**:
  ```python
  backup_dir = os.path.join(settings.BASE_DIR, 'backups')
  backup_name = f"backup_diario_{hoy.strftime('%Y_%m_%d')}.sqlite3"
  backup_path = os.path.join(backup_dir, backup_name)
  if not os.path.exists(backup_path):
      shutil.copy2(settings.DATABASES['default']['NAME'], backup_path)
  ```
  Genera una copia de seguridad y purga archivos que excedan los 30 días para proteger el almacenamiento del servidor.
- **Detalle Integral del Día**:
  - Facturas emitidas hoy (con productos asociados precargados con `prefetch_related`).
  - Cobranzas del día discriminadas por método de pago.
  - Movimientos de inventario del día.
  - Alertas de mantenimiento atendidas y nuevas.
  - Nuevos clientes y vehículos incorporados.

#### 3. `reporte_movimientos(request)` (Líneas 187-219)
- Reporte detallado de auditoría de entradas y salidas de stock entre un rango de fechas `inicio` y `fin`.

---

### B. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/reportes/urls.py)

- `''` -> `dashboard_reportes` (`reportes:dashboard`)
- `'diario/'` -> `reporte_diario` (`reportes:diario`)
- `'movimientos/'` -> `reporte_movimientos` (`reportes:movimientos`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/reportes/dashboard.html` | `base.html` | `ingresos`, `costos`, `ganancia`, `margen`, `labels`, `data_ingresos`, `top_clientes`, `top_productos`, `ordenes_estados`, `ordenes_datos` | Gráficos interactivos en Chart.js (curva de ingresos por día, dona de órdenes por estado), tarjetas de rentabilidad y tablas de mejores clientes/productos. |
| `templates/reportes/diario.html` | `base.html` | `hoy`, `facturas`, `pagos`, `movimientos`, `ordenes`, `resumen`, `total_ventas`, `total_recaudado` | Cierre de caja diario con resumen ejecutivo y botón de impresión / PDF. |
| `templates/reportes/movimientos.html` | `base.html` | `movimientos`, `inicio`, `fin`, `tipo`, `total_entradas`, `total_salidas` | Tabla de auditoría de inventario filtrable por fecha y tipo de operación. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Exportación a Excel (.xlsx) con `openpyxl` o `pandas`
Se puede incorporar un botón para descargar cualquier reporte en formato Excel:
```python
import openpyxl
from django.http import HttpResponse

def exportar_reporte_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(["N° Factura", "Cliente", "Fecha", "Total"])
    for f in Factura.objects.all():
        ws.append([f.numero_factura, f.cliente.nombre_razon_social, f.fecha_emision.strftime('%Y-%m-%d'), float(f.total)])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reporte_ventas.xlsx'
    wb.save(response)
    return response
```

### Opción 2: Base de Datos PostgreSQL y Backups con `pg_dump`
Al migrar a un entorno productivo con PostgreSQL, el mecanismo de respaldo se puede cambiar a un comando administrado mediante `subprocess.run(["pg_dump", ...])` o tareas programadas en Celery / Cron.
