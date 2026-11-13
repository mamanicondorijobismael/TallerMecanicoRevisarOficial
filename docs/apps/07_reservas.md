# 07. Documentación Técnica y Explicación de Código: App `reservas`

La aplicación `reservas` gestiona la agenda de turnos y citas previas del taller mecánico, vinculando al cliente, vehículo, fecha/hora y motivo de visita, con la capacidad de transformarse en una Orden de Trabajo activa.

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `ForeignKey`, `OneToOneField`, `DateTimeField`, `CharField`, `TextField`, `TextChoices`, `RESTRICT`, `SET_NULL`, `Q` | Modela la entidad `Reserva` vinculada a `Cliente`, `Vehiculo` y opcionalmente a la `OrdenTrabajo` resultante. |
| `core.models` | `ModeloBase` | Auditoría de creación y modificación. |
| `django.utils` | `timezone` | Comparación de fecha y hora respecto a la fecha actual para resaltar turnos de hoy o futuros. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Navegación y respuestas HTTP. |
| `django.forms` | `ModelForm`, `DateTimeInput` | Formulario con selector de fecha y hora. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/reservas/models.py)

```python
class Reserva(ModeloBase):
    class Estado(models.TextChoices):
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        PENDIENTE = 'PENDIENTE', 'Pendiente'

    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='reservas', verbose_name='Cliente')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, related_name='reservas', verbose_name='Vehiculo')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y hora')
    servicio_solicitado = models.CharField(max_length=200, verbose_name='Servicio solicitado')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, verbose_name='Estado')
    notas = models.TextField(blank=True, verbose_name='Notas adicionales')
    orden_generada = models.OneToOneField(
        'ordenes.OrdenTrabajo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reserva_origen', verbose_name='Orden de trabajo generada'
    )
```

- **Líneas 9-14 (`Estado`)**: Ciclo de vida del turno (`PENDIENTE` -> `CONFIRMADA` -> `COMPLETADA` o `CANCELADA`).
- **Líneas 21-24 (`orden_generada`)**: Permite vincular el turno con la orden física generada cuando el vehículo ingresa formalmente al taller.

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/reservas/views.py)

- **`reserva_list(request)` (Líneas 9-20)**: Lista de citas ordenadas cronológicamente (`fecha_hora`), con filtros de estado y búsqueda por nombre de cliente o patente del vehículo.
- **`reserva_crear(request)` (Líneas 22-30)**: Registro de nuevo turno en la agenda.
- **`reserva_editar(request, pk)` (Líneas 32-41)**: Modificación de fecha, hora o estado de la reserva.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/reservas/urls.py)

- `''` -> `reserva_list` (`reservas:lista`)
- `'crear/'` -> `reserva_crear` (`reservas:crear`)
- `'<int:pk>/editar/'` -> `reserva_editar` (`reservas:editar`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/reservas/lista.html` | `base.html` | `reservas`, `query`, `estado_filter`, `hoy` | Agenda de turnos con badges de estado, fecha/hora formateada, vehículo y enlace para convertir en orden de trabajo. |
| `templates/reservas/form.html` | `base.html` | `form`, `title`, `reserva` | Formulario con selector de cliente, auto y datetime-local input. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Vista de Calendario Visual (FullCalendar.js)
En lugar de únicamente una lista tabular, se puede integrar la librería `FullCalendar` en `lista.html` consumiendo un endpoint JSON con las citas del mes:
```javascript
var calendar = new FullCalendar.Calendar(calendarEl, {
  initialView: 'dayGridMonth',
  events: '/reservas/api/eventos/'
});
```

### Opción 2: Botón de "Convertir en Orden de Trabajo"
Se puede añadir una acción directa en la vista:
```python
def convertir_en_orden(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    orden = OrdenTrabajo.objects.create(
        vehiculo=reserva.vehiculo,
        diagnostico=reserva.servicio_solicitado,
        creado_por=request.user
    )
    reserva.orden_generada = orden
    reserva.estado = 'COMPLETADA'
    reserva.save()
    return redirect('ordenes:detalle', pk=orden.pk)
```
