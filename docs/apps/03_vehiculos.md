# 03. Documentación Técnica y Explicación de Código: App `vehiculos`

La aplicación `vehiculos` es responsable de la gestión de los vehículos que ingresan al taller (patente, marca, modelo, año, kilometraje, VIN/chasis, color y cliente propietario).

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `ForeignKey`, `RESTRICT`, `CharField`, `IntegerField`, `PositiveIntegerField`, `ImageField`, `BooleanField`, `Index`, `Q` | Modela la entidad `Vehiculo`. Se utiliza `on_delete=models.RESTRICT` en la relación con `Cliente` para evitar que se elimine un cliente si tiene vehículos registrados. |
| `django.core.validators` | `MinValueValidator` | Valida que el año del vehículo no sea menor a 1900 (`validators=[MinValueValidator(1900)]`). |
| `core.models` | `ModeloBase`, `Auditoria` | Herencia de campos de auditoría temporal (`fecha_creacion`, `fecha_modificacion`) y registro de logs de modificaciones. |
| `apps.clientes.models` | `Cliente` | Modelo foráneo con el cual se vincula cada vehículo de manera obligatoria. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Renderizado de vistas y control de flujo de peticiones. |
| `django.contrib.auth.decorators` | `login_required` | Protección de rutas para usuarios logueados. |
| `django.contrib` | `messages` | Mensajes flash de confirmación o advertencia. |
| `django.forms` | `ModelForm`, `Select`, `TextInput`, `NumberInput`, `FileInput` | Construcción de formularios HTML integrados a Django. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/vehiculos/models.py)

```python
class Vehiculo(ModeloBase):
    COLORES = [
        ('BLANCO', 'Blanco'), ('NEGRO', 'Negro'), ('GRIS', 'Gris'), ('PLATA', 'Plata'),
        ('ROJO', 'Rojo'), ('AZUL', 'Azul'), ('VERDE', 'Verde'), ('AMARILLO', 'Amarillo'),
        ('NARANJA', 'Naranja'), ('MARRON', 'Marron'), ('OTRO', 'Otro'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, related_name='vehiculos', verbose_name='Cliente')
    patente = models.CharField(max_length=10, unique=True, verbose_name='Patente')
    marca = models.CharField(max_length=30, verbose_name='Marca')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    anio = models.IntegerField(validators=[MinValueValidator(1900)], null=True, blank=True, verbose_name='Anio')
    vin = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='VIN / Nro. Chasis')
    color = models.CharField(max_length=20, choices=COLORES, default='BLANCO', verbose_name='Color')
    kilometraje_actual = models.PositiveIntegerField(default=0, verbose_name='Kilometraje actual')
    foto = models.ImageField(upload_to='vehiculos/', null=True, blank=True, verbose_name='Foto')
    activo = models.BooleanField(default=True, verbose_name='Activo')
```

- **Línea 14 (`cliente`)**: Relación Muchos a Uno con `Cliente`. `related_name='vehiculos'` permite acceder a todos los vehículos de un cliente con `cliente.vehiculos.all()`.
- **Línea 15 (`patente`)**: Clave única alfanumérica (`unique=True`) para evitar duplicidad de patentes en el sistema.
- **Línea 19 (`vin`)**: Número de chasis único e indexable (opcional).
- **Línea 21 (`kilometraje_actual`)**: Odómetro actual. Se actualiza automáticamente cada vez que se genera o actualiza una orden de trabajo.
- **Líneas 37-39 (`@property ultimo_servicio`)**:
  ```python
  @property
  def ultimo_servicio(self):
      return self.ordenes.filter(estado__in=['COMPLETADA', 'FACTURADA']).order_by('-fecha_creacion').first()
  ```
  Permite conocer inmediatamente cuál fue la última orden completada del auto.

---

### B. [forms.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/vehiculos/forms.py)

```python
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'anio', 'vin', 'color', 'kilometraje_actual', 'foto', 'activo']
```
- Contiene widgets personalizados con estilos CSS unificados para inputs de texto, números y selección desplegable del cliente.
- Normaliza la patente para guardarla siempre en mayúsculas sin espacios innecesarios.

---

### C. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/vehiculos/views.py)

#### 1. `vehiculo_list(request)`
- Búsqueda multi-criterio por `patente`, `marca`, `modelo` o `nombre del cliente` mediante `select_related('cliente')` para evitar el problema de consultas N+1 en la base de datos.

#### 2. `vehiculo_detalle(request, pk)`
- Muestra los datos técnicos del vehículo, historial cronológico de todas las órdenes de trabajo (`vehiculo.ordenes.all()`), y alertas de mantenimiento preventivo vigentes (`vehiculo.alertas_mantenimiento.all()`).

#### 3. `vehiculo_crear(request)` y `vehiculo_editar(request, pk)`
- Permite la creación vinculando opcionalmente un cliente preseleccionado si se pasa `cliente_id` por parámetro URL (`?cliente=ID`).
- Registra la acción en la tabla `Auditoria`.

---

### D. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/vehiculos/urls.py)

- `''` -> `vehiculo_list` (`vehiculos:lista`)
- `'crear/'` -> `vehiculo_crear` (`vehiculos:crear`)
- `'<int:pk>/'` -> `vehiculo_detalle` (`vehiculos:detalle`)
- `'<int:pk>/editar/'` -> `vehiculo_editar` (`vehiculos:editar`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/vehiculos/lista.html` | `base.html` | `vehiculos`, `query` | Grid responsivo de vehículos, foto del auto, badge de kilometraje, datos del propietario y botón para crear orden de trabajo directa. |
| `templates/vehiculos/detalle.html` | `base.html` | `vehiculo`, `ordenes`, `alertas` | Ficha técnica completa, odómetro con indicador visual, historial de mantenimientos pasados y alertas programadas. |
| `templates/vehiculos/form.html` | `base.html` | `form`, `title`, `vehiculo` | Formulario de alta y edición con selector de cliente y previsualización de imagen. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Autocompletado de Marcas y Modelos vía API Externa
Para mejorar la experiencia del usuario y evitar errores tipográficos (ej. "Toyota" vs "Toyotta"), se puede integrar un selector dependiente (Marca -> Modelo) consumiendo una base de datos o API como la de la NHTSA o un listado local precargado en JSON.

### Opción 2: Historial de Kilometraje (Timeline de Lecturas)
Si se desea llevar una gráfica histórica de la evolución del odómetro en cada visita, se puede crear un modelo intermedio:
```python
class LecturaKilometraje(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='lecturas_km')
    fecha = models.DateTimeField(auto_now_add=True)
    kilometraje = models.PositiveIntegerField()
    origen = models.CharField(max_length=50) # ej: "Ingreso OT #202401"
```
