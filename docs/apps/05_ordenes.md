# 05. Documentación Técnica y Explicación de Código: App `ordenes`

La aplicación `ordenes` es el núcleo operativo del taller mecánico. Controla el ciclo de vida completo de los trabajos: ingreso del vehículo, asignación de mecánico, diagnóstico, carga de mano de obra (servicios) y repuestos consumidos, cálculo automático de totales e IVA, transiciones de estado y descuento automático de inventario al completar la orden.

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `ForeignKey`, `RESTRICT`, `CASCADE`, `SET_NULL`, `TextChoices`, `CharField`, `TextField`, `PositiveIntegerField`, `DecimalField`, `DateTimeField`, `Index` | Modelado de la orden de trabajo y sus líneas de detalle (servicios y repuestos). Define llaves foráneas con eliminación protegida o en cascada. |
| `django.core.validators` | `MinValueValidator` | Valida cantidades y precios mínimos en mano de obra y repuestos. |
| `django.utils` | `timezone` | Asigna la fecha y hora de cierre al completar la orden de trabajo. |
| `django.conf` | `settings` | Lee variables de configuración global como `IVA_PORCENTAJE` (por defecto 21%). |
| `apps.vehiculos.models` | `Vehiculo` | Vehículo intervenido en la orden. |
| `apps.accounts.models` | `Usuario` | Mecánico asignado y usuario creador de la orden. |
| `apps.inventario.models` | `ProductoBase`, `MovimientoStock` | Vinculación y consumo de repuestos con actualización de stock. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Flujo de navegación y renderizado de plantillas. |
| `django.contrib` | `messages` | Mensajes flash de validación de transiciones de estado y operaciones. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/ordenes/models.py)

#### 1. Estados y Máquina de Transiciones (`OrdenTrabajo.Estado` y `TRANSICIONES_VALIDAS`)
```python
class OrdenTrabajo(ModeloBase):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        PAUSADA = 'PAUSADA', 'Pausada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        FACTURADA = 'FACTURADA', 'Cobrada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    TRANSICIONES_VALIDAS = {
        'PENDIENTE': ['EN_PROCESO', 'COMPLETADA', 'PAUSADA', 'CANCELADA'],
        'EN_PROCESO': ['COMPLETADA', 'PAUSADA', 'PENDIENTE', 'CANCELADA'],
        'PAUSADA': ['EN_PROCESO', 'COMPLETADA', 'PENDIENTE', 'CANCELADA'],
        'COMPLETADA': ['EN_PROCESO', 'PAUSADA'],
        'FACTURADA': [], # Estado terminal
        'CANCELADA': ['PENDIENTE', 'EN_PROCESO'],
    }
```
- **Líneas 9-24**: Define los estados posibles y la matriz de transiciones válidas para evitar inconsistencias lógicas (ej. no se puede saltar una orden directamente de cancelada a facturada).

#### 2. Campos Principales y Guardado Automático del Número de Orden
- **Líneas 26-43**:
  - `numero_orden`: Identificador correlativo anual/mensual (ej. `2024090001`).
  - `vehiculo`: FK a `Vehiculo` con `RESTRICT`.
  - `mecanico`: FK a `Usuario` filtrado por rol con `limit_choices_to={'rol__in': ['MECANICO', 'ADMINISTRADOR', 'DUENO']}`.
  - `kilometraje`: Odómetro al ingreso.
  - `diagnostico`, `observaciones`, `fecha_prometida`, `fecha_cierre`.
- **Líneas 57-63 (`save`)**:
  ```python
  if not self.numero_orden:
      prefix = datetime.date.today().strftime('%Y%m')
      last = OrdenTrabajo.objects.filter(numero_orden__startswith=prefix).count()
      self.numero_orden = f'{prefix}{str(last + 1).zfill(4)}'
  ```
  Genera automáticamente el número correlativo de orden.

#### 3. Propiedades Financieras Calculadas
- **`subtotal_servicios` (Línea 70)**: Sumatoria de `cantidad * precio_unitario` de todos los servicios asociados (`self.servicios.all()`).
- **`subtotal_productos` (Línea 74)**: Sumatoria de `cantidad * precio_unitario` de todos los repuestos agregados (`self.productos.all()`).
- **`subtotal` (Línea 78)**: `subtotal_servicios + subtotal_productos`.
- **`iva_monto` (Línea 82)**: Cálculo automático del impuesto: `round(self.subtotal * iva / 100, 2)`.
- **`total` (Línea 88)**: `subtotal + iva_monto`.
- **`costo_total` (Línea 92)**: Costo real de compra de los repuestos consumidos.
- **`ganancia_bruta` (Línea 96)**: `total - costo_total`.

#### 4. Detalles de Servicios y Productos (`DetalleServicio`, `DetalleProducto`)
- **Líneas 103-120 (`DetalleServicio`)**: Representa mano de obra, horas hombre, alineación, balanceo, scanner, etc.
- **Líneas 122-143 (`DetalleProducto`)**: Representa repuestos instalados (aceite, filtros, pastillas de freno, cubiertas). Contiene `@property subtotal` y `@property costo_total`.

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/ordenes/views.py)

#### 1. `orden_list(request)` (Líneas 10-25)
- Permite filtrar órdenes por estado (`PENDIENTE`, `EN_PROCESO`, etc.) y buscar por número de orden, patente o nombre del cliente.
- Utiliza `select_related('vehiculo', 'vehiculo__cliente', 'mecanico')` para optimizar consultas.

#### 2. `orden_detalle(request, pk)` (Líneas 28-38)
- Vista principal de la orden: lista servicios, repuestos instalados, resumen financiero, botones para cambiar de estado y formularios incrustados para agregar ítems.

#### 3. `orden_crear(request)` y `orden_editar(request, pk)` (Líneas 41-82)
- Registra la orden e incrementa el odómetro del vehículo si el kilometraje ingresado es mayor al registrado previamente.

#### 4. `orden_cambiar_estado(request, pk)` (Líneas 84-112)
- Valida si la transición es permitida con `orden.puede_transicionar(nuevo_estado)`.
- **Lógica de Cierre (`COMPLETADA`)**:
  - Asigna `orden.fecha_cierre = timezone.now()`.
  - Recorre todos los repuestos cargados en la orden (`orden.productos.all()`).
  - Descuenta el `stock_actual` de cada producto.
  - Genera automáticamente un `MovimientoStock` de tipo `SALIDA` con motivo `"Consumo OT#..."`.

#### 5. `agregar_servicio`, `agregar_producto`, `eliminar_servicio`, `eliminar_producto` (Líneas 115-162)
- Gestiona la adición y remoción dinámica de líneas de detalle en la orden abierta.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/ordenes/urls.py)

- `''` -> `orden_list` (`ordenes:lista`)
- `'crear/'` -> `orden_crear` (`ordenes:crear`)
- `'<int:pk>/'` -> `orden_detalle` (`ordenes:detalle`)
- `'<int:pk>/editar/'` -> `orden_editar` (`ordenes:editar`)
- `'<int:pk>/estado/'` -> `orden_cambiar_estado` (`ordenes:cambiar_estado`)
- `'<int:pk>/servicios/agregar/'` -> `agregar_servicio` (`ordenes:agregar_servicio`)
- `'<int:pk>/servicios/<int:spk>/eliminar/'` -> `eliminar_servicio` (`ordenes:eliminar_servicio`)
- `'<int:pk>/productos/agregar/'` -> `agregar_producto` (`ordenes:agregar_producto`)
- `'<int:pk>/productos/<int:ppk>/eliminar/'` -> `eliminar_producto` (`ordenes:eliminar_producto`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/ordenes/lista.html` | `base.html` | `ordenes`, `estados`, `estado_filter`, `query` | Tablero de órdenes con filtros de estado (chips de color), buscador, mecánico asignado, importe total y botón para crear orden. |
| `templates/ordenes/detalle.html` | `base.html` | `orden`, `servicios`, `productos`, `form_servicio`, `form_producto` | Vista integral de la orden: barra de estado interactiva (botones para pasar a En Proceso, Completar, Facturar), tablas de servicios y repuestos con botones de eliminar, resumen de subtotal, IVA y total general. |
| `templates/ordenes/form.html` | `base.html` | `form`, `title`, `orden` | Formulario de datos iniciales: selección de vehículo, kilometraje, mecánico responsable, diagnóstico y fecha prometida. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Generación de Orden de Trabajo en PDF Imprimible
Se puede añadir una vista para exportar la orden de trabajo con formato de taller (con firma de conformidad del cliente y checklist de recepción del auto) usando `django.template.loader.render_to_string` y `weasyprint` o `reportlab`.

### Opción 2: Checklist de Inspección Inicial (Daños y Nivel de Combustible)
Se puede agregar un modelo relacionado `ChecklistIngreso` con campos booleanos:
```python
class InspeccionIngreso(models.Model):
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name='inspeccion')
    nivel_combustible = models.CharField(max_length=20, choices=[('RESERVA', '1/8'), ('MEDIO', '1/2'), ('LLENO', 'Lleno')])
    rueda_auxilio = models.BooleanField(default=True)
    crique_llave = models.BooleanField(default=True)
    rayones_golpes = models.TextField(blank=True)
```
