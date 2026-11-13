# 08. Documentación Técnica y Explicación de Código: App `facturas`

La aplicación `facturas` maneja el proceso contable y de cobranzas: generación de facturas a partir de órdenes de trabajo completadas, cálculo de subtotal, IVA, total, seguimiento de estado de cobro (`PENDIENTE`, `PARCIAL`, `PAGADA`, `ANULADA`), y registro de pagos en diferentes métodos (Efectivo, Tarjetas, Transferencia, Mercado Pago, Cheque).

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `OneToOneField`, `ForeignKey`, `CharField`, `DecimalField`, `DateTimeField`, `TextField`, `TextChoices`, `RESTRICT`, `CASCADE`, `Q` | Relaciona la factura con su orden de trabajo de origen y con el cliente. |
| `django.core.validators` | `MinValueValidator` | Asegura que los pagos registrados sean mayores a cero (`MinValueValidator(0.01)`). |
| `core.models` | `ModeloBase` | Herencia de campos de auditoría temporal. |
| `apps.ordenes.models` | `OrdenTrabajo` | Orden sobre la cual se emite la factura. |
| `apps.clientes.models` | `Cliente` | Cliente titular de la factura. |
| `django.conf` | `settings` | Lee configuración impositiva (`IVA_PORCENTAJE`). |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Renderizado y control de flujo. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/facturas/models.py)

#### 1. Factura (`Factura`)
```python
class Factura(ModeloBase):
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PARCIAL = 'PARCIAL', 'Pago parcial'
        PAGADA = 'PAGADA', 'Pagada'
        ANULADA = 'ANULADA', 'Anulada'

    numero_factura = models.CharField(max_length=20, unique=True, verbose_name='N° Factura')
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.RESTRICT, related_name='factura')
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='facturas')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    iva_monto = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    notas = models.TextField(blank=True)
```
- **Líneas 35-41 (`save`)**: Generación correlativa mensual del número de factura (ej. `F2024090001`).
- **Líneas 43-50 (`@property total_pagado`, `@property saldo_pendiente`)**:
  - `total_pagado`: Suma de todos los pagos ingresados (`sum(p.monto for p in self.pagos.all())`).
  - `saldo_pendiente`: `total - total_pagado`.
- **Líneas 51-60 (`actualizar_estado`)**: Método que reevalúa el estado (`PAGADA`, `PARCIAL`, `PENDIENTE`) según el saldo cubierto tras cada pago.

#### 2. Pago (`Pago`)
```python
class Pago(models.Model):
    METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_DEBITO', 'Tarjeta de debito'),
        ('TARJETA_CREDITO', 'Tarjeta de credito'),
        ('TRANSFERENCIA', 'Transferencia bancaria'),
        ('CHEQUE', 'Cheque'),
        ('MERCADO_PAGO', 'Mercado Pago'),
    ]
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES, default='EFECTIVO')
    referencia = models.CharField(max_length=100, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=150, blank=True)
```

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/facturas/views.py)

#### 1. `factura_list(request)` (Líneas 11-20)
- Listado de facturas emitidas con filtro por estado de pago y buscador por número o cliente.

#### 2. `factura_detalle(request, pk)` (Líneas 23-27)
- Vista completa del comprobante contable con desglose de servicios, repuestos y tabla de pagos recibidos.

#### 3. `generar_factura(request, orden_pk)` (Líneas 30-54)
- Valida que la orden esté en estado `COMPLETADA` y no tenga factura previa.
- Copia los importes exactos (`subtotal`, `iva_monto`, `total`), crea la `Factura`, y cambia el estado de la orden a `FACTURADA`.

#### 4. `registrar_pago(request, pk)` (Líneas 57-80)
- Valida que el monto abonado no exceda el saldo pendiente.
- Inserta el `Pago`, ejecuta `factura.actualizar_estado()` y emite notificación.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/facturas/urls.py)

- `''` -> `factura_list` (`facturas:lista`)
- `'<int:pk>/'` -> `factura_detalle` (`facturas:detalle`)
- `'generar/<int:orden_pk>/'` -> `generar_factura` (`facturas:generar`)
- `'<int:pk>/pago/'` -> `registrar_pago` (`facturas:registrar_pago`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/facturas/lista.html` | `base.html` | `facturas`, `query`, `estado_filter` | Listado general con badges de estado (Verde: Pagada, Naranja: Parcial, Rojo: Pendiente), montos totales y saldo por cobrar. |
| `templates/facturas/detalle.html` | `base.html` | `factura`, `pagos` | Factura formal tipo A/B con desglose tributario, botón de impresión / PDF, y modal/formulario para asentar pagos parciales o totales. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Integración con Facturación Electrónica AFIP / SRI / SAT / DIAN
Para emitir comprobantes fiscales oficiales (CAE/Factura Electrónica), se puede crear un servicio `apps/facturas/services/afip.py` utilizando librerías como `PyAfipWs` o `httpx` para conectar con el Web Service de la entidad tributaria.

### Opción 2: Generación de Factura PDF con Código QR
Generar el archivo PDF directamente con `weasyprint` o `reportlab` incorporando el código QR oficial con los datos del comprobante.
