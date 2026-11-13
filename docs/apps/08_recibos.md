# 08. Documentación Técnica y Explicación de Código: App `recibos`

La aplicación `recibos` maneja el proceso de cobro y liquidación: generación de recibos a partir de órdenes de trabajo completadas, cálculo de subtotal, IVA, total, seguimiento de estado de cobro (`PENDIENTE`, `PARCIAL`, `PAGADA`, `ANULADA`), y registro de pagos en efectivo.

---

## 1. Librerías y Módulos Utilizados

| Módulo / Librería | Clases / Funciones | Propósito |
|---|---|---|
| `django.db.models` | `OneToOneField`, `ForeignKey`, `CharField`, `DecimalField`, `DateTimeField`, `TextField`, `TextChoices`, `RESTRICT`, `CASCADE`, `Q` | Relaciona el recibo con su orden de trabajo de origen y con el cliente. |
| `django.core.validators` | `MinValueValidator` | Asegura que los pagos registrados tengan un monto estrictamente mayor a 0. |
| `apps.ordenes.models` | `OrdenTrabajo` | Orden sobre la cual se emite el recibo. |
| `apps.clientes.models` | `Cliente` | Cliente titular del recibo. |
| `apps.accounts.decorador` | `requiere_permiso` | Decorador de seguridad para proteger vistas según permisos. |

---

## 2. Explicación de Archivos y Componentes

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/recibos/models.py)

#### 1. Recibo (`Recibo`)
```python
class Recibo(ModeloBase):
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PARCIAL = 'PARCIAL', 'Pago parcial'
        PAGADA = 'PAGADA', 'Pagado / Cobrado'
        ANULADA = 'ANULADA', 'Anulado'

    numero_recibo = models.CharField(max_length=20, unique=True, verbose_name='N° de Recibo')
    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.RESTRICT, related_name='recibo')
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='recibos')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    iva_monto = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices, default=EstadoPago.PENDIENTE)
    notas = models.TextField(blank=True)
```
- **Lógica `save`**: Generación correlativa mensual del número de recibo (ej. `REC2026100001`).
- **`total_pagado`**: Propiedad calculada que suma todos los pagos registrados para este recibo.
- **`saldo_pendiente`**: Resta el total menos lo pagado.
- **`actualizar_estado()`**: Cambia automáticamente a `PAGADA`, `PARCIAL` o `PENDIENTE`.

#### 2. Pago (`Pago`)
```python
class Pago(models.Model):
    recibo = models.ForeignKey(Recibo, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    metodo_pago = models.CharField(max_length=30, choices=[('EFECTIVO', 'Efectivo')], default='EFECTIVO')
    referencia = models.CharField(max_length=100, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=150, blank=True)
```
- Registra cada abono recibido, vinculándolo a su correspondiente recibo.

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/recibos/views.py)

1. `recibo_lista(request)`: Listado con filtros de estado y buscador por número de recibo o cliente.
2. `recibo_detalle(request, pk)`: Detalle del recibo con liquidación e historial de abonos.
3. `generar_recibo(request, orden_pk)`: Valida orden `COMPLETADA`, genera el `Recibo` y avanza la orden a `COBRADA`.
4. `registrar_pago(request, pk)`: Asienta el cobro, valida que no supere el saldo y actualiza el estado.
5. `anular_recibo(request, pk)`: Anula el recibo si no tiene pagos y restablece la orden a `COMPLETADA`.
6. `imprimir_recibo(request, pk)`: Vista formal para impresión / PDF.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/recibos/urls.py)

- `''` -> `recibo_lista` (`recibos:lista`)
- `'<int:pk>/'` -> `recibo_detalle` (`recibos:detalle`)
- `'generar/<int:orden_pk>/'` -> `generar_recibo` (`recibos:generar`)
- `'<int:pk>/pago/'` -> `registrar_pago` (`recibos:pago`)
- `'<int:pk>/anular/'` -> `anular_recibo` (`recibos:anular`)
- `'<int:pk>/imprimir/'` -> `imprimir_recibo` (`recibos:imprimir`)
