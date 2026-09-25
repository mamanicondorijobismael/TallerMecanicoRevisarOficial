# 04. Documentación Técnica y Explicación de Código: App `inventario`

La aplicación `inventario` es una de las más completas del sistema. Administra repuestos, neumáticos, categorías, stock actual y mínimo, alertas de stock crítico, movimientos de inventario (entradas, salidas, ajustes), y ventas directas en mostrador.

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `ForeignKey`, `OneToOneField`, `DecimalField`, `PositiveIntegerField`, `CharField`, `TextField`, `ImageField`, `BooleanField`, `F`, `Q` | Modela la jerarquía polimórfica (ProductoBase -> RepuestoGenerico / Neumatico). `F('stock_minimo')` permite comparar dos columnas de la misma fila en BD sin cargarlas en memoria Python. |
| `django.core.validators` | `MinValueValidator` | Asegura que precios y cantidades no sean negativos. |
| `core.models` | `ModeloBase`, `Auditoria` | Herencia base y auditoría de variaciones en precios de venta. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Enrutamiento de vistas y renderizado HTML. |
| `django.contrib` | `messages` | Mensajes flash para advertencias de stock insuficiente y confirmaciones de operaciones. |
| `django.forms` | `ModelForm`, `Form` | Formularios especializados para repuestos, neumáticos, ajustes y categorías. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/inventario/models.py)

#### 1. Categoría de Producto (`CategoriaProducto`)
- **Líneas 6-20**: Clasifica productos (`REPUESTO` o `NEUMATICO`). Incluye nombre, descripción e icono representativo para la interfaz gráfica.

#### 2. Producto Base (`ProductoBase`)
```python
class ProductoBase(ModeloBase):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.RESTRICT, related_name='productos')
    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name='Codigo SKU')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    precio_costo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    tipo_producto = models.CharField(max_length=20, choices=[('REPUESTO', 'Repuesto'), ('NEUMATICO', 'Neumatico')])
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    activo = models.BooleanField(default=True)
```
- **Líneas 47-52 (`save`)**: Generación automática de SKU (`REP-00001` o `NEU-00001`) si el usuario no ingresó uno manual.
- **Líneas 58-70 (`@property margen_ganancia`, `@property stock_critico`)**:
  - `margen_ganancia`: Calcula el porcentaje de ganancia sobre el precio de venta `((venta - costo) / venta) * 100`.
  - `stock_critico`: Retorna `True` si `stock_actual <= stock_minimo`.

#### 3. Repuesto Genérico (`RepuestoGenerico`)
- **Líneas 72-85**: Extiende `ProductoBase` mediante `OneToOneField(primary_key=True)`. Agrega `marca_repuesto`, `numero_parte` y lista de compatibilidades (`compatible_con`).

#### 4. Neumático (`Neumatico`)
- **Líneas 87-114**: Extiende `ProductoBase` con especificaciones de gomería:
  - `ancho` (mm), `perfil` (%), `diametro` (R).
  - `indice_carga`, `indice_velocidad`, `tipo` (`VERANO`, `INVIERNO`, `ALL_SEASON`, `OFF_ROAD`), `estado` (`NUEVO`, `USADO`), y `profundidad_restante` (mm de dibujo para usados).
  - `@property medida`: Retorna la nomenclatura estándar (ej. `205/55R16`).

#### 5. Movimiento de Stock (`MovimientoStock`)
- **Líneas 116-143**: Libro mayor de auditoría de inventario:
  - Registra cada `ENTRADA`, `SALIDA`, `AJUSTE` o `VENTA_DIRECTA`.
  - Guarda la `cantidad`, el `stock_resultante` exacto tras la transacción, el `motivo`, la `orden` de trabajo vinculada (si aplica) y el `usuario` responsable.

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/inventario/views.py)

#### 1. `producto_list(request)` (Líneas 9-46)
- Gestiona filtros combinados: búsqueda por texto (`q`), solo stock crítico (`criticos=1`), tipo de producto (`REPUESTO` o `NEUMATICO`), y categoría.
- Admite modo de visualización en tarjetas o en tabla (`view=grid` vs `view=table`).
- Utiliza `select_related('categoria', 'repuesto', 'neumatico')` para optimizar consultas a la BD.

#### 2. `repuesto_list` y `neumatico_list` (Líneas 49-83)
- Listados técnicos especializados con filtros dimensionales para neumáticos (ancho, perfil, rodado).

#### 3. `venta_directa(request, pk)` (Líneas 166-195)
- Permite vender un repuesto o neumático en el mostrador sin necesidad de crear una Orden de Trabajo completa.
- Valida disponibilidad en stock, descuenta unidades, genera el `MovimientoStock` de tipo `VENTA_DIRECTA` y redirige a la generación de comprobante (`venta_recibo`).

#### 4. `ajuste_stock(request, pk)` (Líneas 204-231)
- Permite ingresar compras a proveedores o asentar bajas por rotura/merma física.
- Actualiza el stock atómicamente y deja registro en `MovimientoStock`.

#### 5. CRUD de Categorías y Visor de Movimientos
- `categoria_lista`, `categoria_crear`, `categoria_editar`, `categoria_eliminar` (con validación de que no tenga productos asignados antes de borrar).
- `movimientos_list`: Registro cronológico global de movimientos para auditoría.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/inventario/urls.py)

Rutas principales con namespace `inventario`:
- `''` -> `producto_list` (`inventario:lista`)
- `'repuestos/'` -> `repuesto_list` (`inventario:repuestos`)
- `'repuestos/crear/'` -> `repuesto_crear` (`inventario:repuesto_crear`)
- `'repuestos/<int:pk>/editar/'` -> `repuesto_editar` (`inventario:repuesto_editar`)
- `'neumaticos/'` -> `neumatico_list` (`inventario:neumaticos`)
- `'neumaticos/crear/'` -> `neumatico_crear` (`inventario:neumatico_crear`)
- `'neumaticos/<int:pk>/editar/'` -> `neumatico_editar` (`inventario:neumatico_editar`)
- `'producto/<int:pk>/venta-directa/'` -> `venta_directa` (`inventario:venta_directa`)
- `'producto/<int:pk>/ajuste/'` -> `ajuste_stock` (`inventario:ajuste_stock`)
- `'movimientos/'` -> `movimientos_list` (`inventario:movimientos`)
- `'categorias/'` -> `categoria_lista` (`inventario:categoria_lista`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/inventario/lista.html` | `base.html` | `productos`, `criticos_count`, `categorias`, `view_mode`, `query` | Dashboard de inventario con toggle de vista Grid/Tabla, barra de filtros rápidos (Stock Crítico, Repuestos, Neumáticos), badges de alerta roja si `stock_critico`. |
| `templates/inventario/repuestos.html` | `base.html` | `repuestos`, `query` | Lista técnica con número de pieza, marcas de compatibilidad y botones de ajuste rápido. |
| `templates/inventario/neumaticos.html` | `base.html` | `neumaticos`, `filtro_ancho`, `filtro_perfil`, `filtro_diametro` | Buscador por medida (ej. 195/65 R15), estado (Nuevo/Usado), y tipo de temporada. |
| `templates/inventario/form_repuesto.html` | `base.html` | `form`, `title`, `repuesto`, `movimientos` | Formulario compuesto (ProductoBase + RepuestoGenerico) con histórico de últimos movimientos. |
| `templates/inventario/form_neumatico.html` | `base.html` | `form`, `title`, `neumatico`, `movimientos` | Formulario técnico con dimensiones de neumático. |
| `templates/inventario/venta_directa.html` | `base.html` | `producto` | Modal/pantalla de venta rápida con cálculo de subtotal en tiempo real. |
| `templates/inventario/venta_recibo.html` | `base.html` | `movimiento` | Comprobante imprimible tipo ticket para entrega al cliente. |
| `templates/inventario/form_ajuste.html` | `base.html` | `form`, `producto` | Formulario de entrada/salida de stock con validación de remanente. |
| `templates/inventario/movimientos.html` | `base.html` | `movimientos` | Bitácora de transacciones con badges de Entrada (Verde), Salida (Rojo) y Ajuste (Azul). |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Lotes y Valuación FIFO / LIFO / Precio Promedio Ponderado (PPP)
Actualmente el costo de reposición se maneja a nivel de producto (`precio_costo`). Si se requiere trazabilidad contable avanzada de compras a diferentes precios a lo largo del tiempo:
```python
class LoteInventario(models.Model):
    producto = models.ForeignKey(ProductoBase, on_delete=models.CASCADE, related_name='lotes')
    nro_lote = models.CharField(max_length=50)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    costo_unitario_compra = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
```

### Opción 2: Lector de Códigos de Barra / Escáner QR
Se puede integrar una librería JavaScript en `lista.html` (como `html5-qrcode` o `quagga.js`) para capturar códigos de barra con la cámara del teléfono o pistola lectora USB y buscar el SKU automáticamente.
