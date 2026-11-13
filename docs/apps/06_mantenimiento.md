# 06. Documentación Técnica y Explicación de Código: App `mantenimiento`

La aplicación `mantenimiento` gestiona los planes preventivos de servicio del taller (ej. Cambio de Aceite y Filtro cada 10.000 km o 12 meses, Rotación de Neumáticos cada 15.000 km, Distribución cada 60.000 km) y las alertas automáticas para notificar y fidelizar a los clientes.

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `ForeignKey`, `CASCADE`, `CharField`, `TextField`, `DecimalField`, `PositiveIntegerField`, `DateField`, `TextChoices` | Modela los tipos de mantenimiento y las alertas generadas por kilometraje o fecha estimada. |
| `core.models` | `ModeloBase` | Herencia de auditoría con marcas temporales de creación y modificación. |
| `apps.vehiculos.models` | `Vehiculo` | Entidad sobre la cual recae la alerta preventiva. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Renderizado y control de rutas. |
| `django.contrib.auth.decorators` | `login_required` | Seguridad en vistas. |
| `django.contrib` | `messages` | Mensajes flash de confirmación de estado de alertas. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/mantenimiento/models.py)

#### 1. Tipo de Servicio (`TipoServicio`)
```python
class TipoServicio(ModeloBase):
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre del servicio')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Precio base')
    intervalo_km = models.PositiveIntegerField(null=True, blank=True, verbose_name='Intervalo en km')
    intervalo_meses = models.PositiveIntegerField(null=True, blank=True, verbose_name='Intervalo en meses')
    activo = models.BooleanField(default=True, verbose_name='Activo')
```
- **Líneas 6-22**: Define el catálogo de servicios estándar ofrecidos por el taller con sus frecuencias recomendadas de kilometraje y tiempo.

#### 2. Alerta de Mantenimiento (`AlertaMantenimiento`)
```python
class AlertaMantenimiento(ModeloBase):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        NOTIFICADA = 'NOTIFICADA', 'Notificada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        IGNORADA = 'IGNORADA', 'Ignorada'

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='alertas_mantenimiento')
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE, related_name='alertas')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    km_estimado = models.PositiveIntegerField(null=True, blank=True)
    fecha_estimada = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
```
- **Líneas 24-46**: Asocia un vehículo con un servicio preventivo. Permite rastrear si el cliente ya fue notificado (por WhatsApp o email) o si ya concurrió al taller (`ATENDIDA`).

---

### B. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/mantenimiento/views.py)

- **`alerta_list(request)` (Líneas 8-16)**: Lista alertas filtradas por estado (`PENDIENTE` por defecto). Usa `select_related('vehiculo', 'vehiculo__cliente', 'tipo_servicio')` para cargar los datos del cliente y vehículo en una sola consulta SQL.
- **`alerta_crear(request)` (Líneas 19-25)**: Formulario para programar manualmente una alerta de mantenimiento.
- **`alerta_cambiar_estado(request, pk, estado)` (Líneas 28-33)**: Acción rápida para marcar una alerta como `NOTIFICADA`, `ATENDIDA` o `IGNORADA` desde la interfaz.
- **`tipo_servicio_list`, `tipo_servicio_crear`, `tipo_servicio_editar` (Líneas 36-58)**: CRUD de planes y precios base de mantenimiento.

---

### C. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/mantenimiento/urls.py)

- `'alertas/'` -> `alerta_list` (`mantenimiento:alertas`)
- `'alertas/crear/'` -> `alerta_crear` (`mantenimiento:alerta_crear`)
- `'alertas/<int:pk>/estado/<str:estado>/'` -> `alerta_cambiar_estado` (`mantenimiento:cambiar_estado`)
- `'tipos/'` -> `tipo_servicio_list` (`mantenimiento:tipos`)
- `'tipos/crear/'` -> `tipo_servicio_crear` (`mantenimiento:tipo_crear`)
- `'tipos/<int:pk>/editar/'` -> `tipo_servicio_editar` (`mantenimiento:tipo_editar`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/mantenimiento/alertas.html` | `base.html` | `alertas`, `estado_filter`, `total_pendiente` | Lista de alertas con badges de estado, datos de contacto del cliente (teléfono/email), y botones de acción rápida para marcar como Atendida o Notificada. |
| `templates/mantenimiento/tipos.html` | `base.html` | `tipos` | Catálogo de tipos de servicios con sus intervalos y precios base. |
| `templates/mantenimiento/form_alerta.html` | `base.html` | `form`, `title` | Selector de vehículo, tipo de servicio y fecha/km estimado. |
| `templates/mantenimiento/form_tipo.html` | `base.html` | `form`, `title` | Creación y edición de tipos de servicio. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Generación Automática de Alertas al Completar una Orden de Trabajo
Se puede conectar una señal Django (`post_save` en `OrdenTrabajo`) para que cuando una orden pase a `COMPLETADA`, calcule el próximo cambio de aceite sumando los `intervalo_km` al odómetro actual del auto:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=OrdenTrabajo)
def generar_alertas_automaticas(sender, instance, **kwargs):
    if instance.estado == 'COMPLETADA' and instance.kilometraje:
        tipo_aceite = TipoServicio.objects.filter(nombre__icontains='Aceite').first()
        if tipo_aceite and tipo_aceite.intervalo_km:
            AlertaMantenimiento.objects.get_or_create(
                vehiculo=instance.vehiculo,
                tipo_servicio=tipo_aceite,
                estado='PENDIENTE',
                defaults={'km_estimado': instance.kilometraje + tipo_aceite.intervalo_km}
            )
```

### Opción 2: Botón de WhatsApp Directo con Mensaje Prediseñado
En `templates/mantenimiento/alertas.html`, se puede añadir un enlace directo `https://wa.me/{{ alerta.vehiculo.cliente.telefono }}?text=Hola%20{{ alerta.vehiculo.cliente.nombre_razon_social }}...` para contactar al cliente con un solo clic.
