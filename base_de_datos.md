# 🗄️ Diccionario y Modelo de Base de Datos - Sistema TallerGes
**Motor de Base de Datos:** SQLite 3 (Entorno local) / PostgreSQL 14+ (Producción)  
**ORM:** Django ORM con migraciones automáticas  
**Patrón de Diseño:** Modelo Entidad-Relación Relacional Normalizado (3FN)  

---

## 1. Diagrama Entidad-Relación (Mermaid ERD)

```mermaid
erDiagram
    USUARIO ||--o{ ORDEN_TRABAJO : "crea / atiende"
    USUARIO ||--o{ MOVIMIENTO_STOCK : "registra"
    
    CLIENTE ||--o{ VEHICULO : "posee"
    CLIENTE ||--o{ FACTURA : "es facturado"
    CLIENTE ||--o{ RESERVA : "reserva"
    
    VEHICULO ||--o{ ORDEN_TRABAJO : "ingresa a"
    VEHICULO ||--o{ RESERVA : "es atendido en"
    VEHICULO ||--o{ ALERTA_MANTENIMIENTO : "recibe"
    
    CATEGORIA_PRODUCTO ||--o{ PRODUCTO_BASE : "clasifica"
    PRODUCTO_BASE ||--o| REPUESTO_GENERICO : "extiende (1:1)"
    PRODUCTO_BASE ||--o| NEUMATICO : "extiende (1:1)"
    PRODUCTO_BASE ||--o{ MOVIMIENTO_STOCK : "tiene"
    PRODUCTO_BASE ||--o{ DETALLE_PRODUCTO : "se usa en"
    
    ORDEN_TRABAJO ||--o{ DETALLE_SERVICIO : "contiene"
    ORDEN_TRABAJO ||--o{ DETALLE_PRODUCTO : "consume"
    ORDEN_TRABAJO ||--o| FACTURA : "genera (1:1)"
    ORDEN_TRABAJO ||--o| RESERVA : "origina (1:1)"
    ORDEN_TRABAJO ||--o{ MOVIMIENTO_STOCK : "origina"
    
    FACTURA ||--o{ PAGO : "recibe"
    
    TIPO_SERVICIO ||--o{ ALERTA_MANTENIMIENTO : "define"

    USUARIO {
        int id PK
        string username UK
        string email UK
        string nombre_completo
        string rol
        string telefono
        string foto
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime date_joined
        datetime ultimo_acceso
    }

    CLIENTE {
        int id PK
        string nombre_razon_social
        string documento UK
        string telefono
        string email
        text direccion
        string foto
        boolean activo
        datetime fecha_creacion
        datetime fecha_modificacion
    }

    VEHICULO {
        int id PK
        int cliente_id FK
        string patente UK
        string marca
        string modelo
        int anio
        string vin
        string color
        int kilometraje_actual
        string foto
        boolean activo
        datetime fecha_creacion
    }

    CATEGORIA_PRODUCTO {
        int id PK
        string nombre UK
        string tipo
        text descripcion
        string icono
        datetime fecha_creacion
    }

    PRODUCTO_BASE {
        int id PK
        int categoria_id FK
        string codigo_sku UK
        string nombre
        text descripcion
        decimal precio_costo
        decimal precio_venta
        int stock_actual
        int stock_minimo
        string tipo_producto
        string imagen
        boolean activo
        datetime fecha_creacion
    }

    REPUESTO_GENERICO {
        int producto_id PK, FK
        string marca_repuesto
        string numero_parte
        text compatible_con
    }

    NEUMATICO {
        int producto_id PK, FK
        string marca_neumatico
        string modelo_neumatico
        int ancho
        int perfil
        int diametro
        string indice_carga
        string indice_velocidad
        string tipo
        string estado
        decimal profundidad_restante
    }

    MOVIMIENTO_STOCK {
        int id PK
        int producto_id FK
        string tipo_movimiento
        int cantidad
        int stock_resultante
        string motivo
        int orden_id FK
        string usuario
        decimal precio_unitario
        datetime fecha_movimiento
    }

    ORDEN_TRABAJO {
        int id PK
        string numero_orden UK
        int vehiculo_id FK
        int mecanico_id FK
        int creado_por_id FK
        string estado
        int kilometraje
        text diagnostico
        text observaciones
        datetime fecha_prometida
        datetime fecha_cierre
        datetime fecha_creacion
    }

    DETALLE_SERVICIO {
        int id PK
        int orden_id FK
        string descripcion
        decimal cantidad
        decimal precio_unitario
    }

    DETALLE_PRODUCTO {
        int id PK
        int orden_id FK
        int producto_id FK
        int cantidad
        decimal precio_unitario
    }

    FACTURA {
        int id PK
        string numero_factura UK
        int orden_id FK, UK
        int cliente_id FK
        datetime fecha_emision
        decimal subtotal
        decimal iva_porcentaje
        decimal iva_monto
        decimal total
        string estado_pago
        text notas
    }

    PAGO {
        int id PK
        int factura_id FK
        decimal monto
        string metodo_pago
        string referencia
        datetime fecha
        string usuario
    }

    RESERVA {
        int id PK
        int cliente_id FK
        int vehiculo_id FK
        datetime fecha_hora
        string servicio_solicitado
        string estado
        text notas
        int orden_generada_id FK, UK
    }

    TIPO_SERVICIO {
        int id PK
        string nombre UK
        text descripcion
        decimal precio_base
        int intervalo_km
        int intervalo_meses
        boolean activo
    }

    ALERTA_MANTENIMIENTO {
        int id PK
        int vehiculo_id FK
        int tipo_servicio_id FK
        string estado
        int km_estimado
        date fecha_estimada
        text notas
        datetime fecha_creacion
    }

    AUDITORIA {
        int id PK
        string tabla
        int registro_id
        string accion
        string usuario
        json valores_anteriores
        json valores_nuevos
        datetime fecha
        string ip_address
    }
```

---

## 2. Diccionario de Datos por Tablas

### 1. `accounts_usuario` (Usuarios y Personal)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador único del usuario |
| `username` | VARCHAR(50) | NO | Nombre de usuario (Único) |
| `email` | VARCHAR(254) | NO | Correo electrónico institucional (Único) |
| `nombre_completo` | VARCHAR(150) | NO | Nombre y apellido del empleado |
| `rol` | VARCHAR(20) | NO | `DUENO`, `ADMINISTRADOR`, `MECANICO` |
| `telefono` | VARCHAR(20) | SÍ | Teléfono de contacto directo |
| `foto` | VARCHAR(100) | SÍ | Ruta de imagen de perfil |
| `is_active` | BOOLEAN | NO | Estado de habilitación en el sistema |
| `is_staff` | BOOLEAN | NO | Acceso al panel administrativo |
| `date_joined` | DATETIME | NO | Fecha de alta |

---

### 2. `clientes_cliente` (Clientes del Taller)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador único |
| `nombre_razon_social` | VARCHAR(100) | NO | Razón social o Nombre completo |
| `documento` | VARCHAR(20) | NO | DNI o CUIT (Único) |
| `telefono` | VARCHAR(20) | SÍ | Teléfono principal / WhatsApp |
| `email` | VARCHAR(254) | SÍ | Correo electrónico para notificaciones |
| `direccion` | TEXT | SÍ | Dirección postal |
| `foto` | VARCHAR(100) | SÍ | Foto o documento escaneado |
| `activo` | BOOLEAN | NO | Estado activo/inactivo |

---

### 3. `vehiculos_vehiculo` (Parque Automotor)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador único del vehículo |
| `cliente_id` | INTEGER (FK) | NO | Relación con `clientes_cliente` |
| `patente` | VARCHAR(15) | NO | Dominio / Patente (Única) |
| `marca` | VARCHAR(50) | NO | Marca (ej: Toyota, Ford, Chevrolet) |
| `modelo` | VARCHAR(50) | NO | Modelo (ej: Hilux, Focus, Cruze) |
| `anio` | INTEGER | NO | Año de fabricación |
| `vin` | VARCHAR(30) | SÍ | Número de chasis (VIN) |
| `color` | VARCHAR(30) | SÍ | Color exterior |
| `kilometraje_actual` | INTEGER | NO | Odómetro actual en kilómetros |
| `activo` | BOOLEAN | NO | Estado operativo |

---

### 4. `inventario_productobase` (Catálogo General de Productos)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador del producto |
| `categoria_id` | INTEGER (FK) | NO | Relación con `inventario_categoriaproducto` |
| `codigo_sku` | VARCHAR(50) | NO | Código SKU único (`REP-XXXXX` / `NEU-XXXXX`) |
| `nombre` | VARCHAR(150) | NO | Denominación comercial |
| `precio_costo` | DECIMAL(12,2) | NO | Costo de adquisición unitario |
| `precio_venta` | DECIMAL(12,2) | NO | Precio de venta final al público |
| `stock_actual` | INTEGER | NO | Existencia física disponible en depósito |
| `stock_minimo` | INTEGER | NO | Umbral de alerta de reposición |
| `tipo_producto` | VARCHAR(20) | NO | `REPUESTO` o `NEUMATICO` |

---

### 5. `inventario_movimientostock` (Movimientos y Trazabilidad)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador del movimiento |
| `producto_id` | INTEGER (FK) | NO | Relación con `inventario_productobase` |
| `tipo_movimiento` | VARCHAR(20) | NO | `ENTRADA`, `SALIDA`, `AJUSTE`, `VENTA_DIRECTA` |
| `cantidad` | INTEGER | NO | Unidades ingresadas (+) o egresadas (-) |
| `stock_resultante` | INTEGER | NO | Saldo de stock tras la operación |
| `motivo` | VARCHAR(200) | NO | Detalle descriptivo / Factura de compra |
| `usuario` | VARCHAR(150) | SÍ | Nombre del usuario que registró la acción |
| `fecha_movimiento`| DATETIME | NO | Timestamp de registro |

---

### 6. `ordenes_ordentrabajo` (Órdenes de Servicio de Taller)
| Campo | Tipo | Nulo | Descripción |
|---|---|---|---|
| `id` | INTEGER (PK AUTO) | NO | Identificador único de orden |
| `numero_orden` | VARCHAR(20) | NO | Número correlativo anual (`YYYYMM####`) |
| `vehiculo_id` | INTEGER (FK) | NO | Relación con `vehiculos_vehiculo` |
| `mecanico_id` | INTEGER (FK) | SÍ | Mecánico asignado (`accounts_usuario`) |
| `creado_por_id` | INTEGER (FK) | SÍ | Usuario receptor de la orden |
| `estado` | VARCHAR(20) | NO | `PENDIENTE`, `EN_PROCESO`, `PAUSADA`, `COMPLETADA`, `FACTURADA`, `CANCELADA` |
| `kilometraje` | INTEGER | NO | Odómetro al momento del ingreso |
| `diagnostico` | TEXT | SÍ | Motivo de ingreso y fallas reportadas |
| `fecha_prometida` | DATETIME | SÍ | Compromiso de entrega pactado |

---

### 7. `facturas_factura` y `facturas_pago` (Cobranzas)
- **`facturas_factura`**:
  - `numero_factura` (Único), `orden_id` (1:1), `cliente_id` (FK), `subtotal`, `iva_monto`, `total`, `estado_pago` (`PENDIENTE`, `PARCIAL`, `PAGADA`, `ANULADA`).
- **`facturas_pago`**:
  - `factura_id` (FK), `monto`, `metodo_pago` (`EFECTIVO`, `TARJETA_DEBITO`, `TARJETA_CREDITO`, `TRANSFERENCIA`, `MERCADO_PAGO`, `CHEQUE`), `referencia`, `fecha`, `usuario`.
