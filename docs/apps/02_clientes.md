# 02. Documentación Técnica y Explicación de Código: App `clientes`

La aplicación `clientes` administra el registro de personas físicas y empresas que ingresan sus vehículos al taller mecánico. Contiene su información de contacto, identificación fiscal (DNI/CUIT), histórico de vehículos, órdenes de trabajo y facturación asociada.

---

## 1. Librerías y Módulos Utilizados

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.db.models` | `Model`, `CharField`, `EmailField`, `TextField`, `BooleanField`, `ImageField`, `Index`, `Q` | Define la estructura en base de datos, tipos de columnas, índices para búsquedas optimizadas y filtrado con operadores lógicos (`Q`). |
| `core.models` | `ModeloBase`, `Auditoria` | `ModeloBase` provee los campos de timestamp (`fecha_creacion`, `fecha_modificacion`); `Auditoria` permite registrar qué usuario creó o editó un cliente y qué valores cambiaron. |
| `django.shortcuts` | `render`, `get_object_or_404`, `redirect` | Renderiza plantillas, busca instancias por Clave Primaria (o lanza HTTP 404) y redirige tras operaciones POST exitosas. |
| `django.contrib.auth.decorators` | `login_required` | Garantiza que solo usuarios autenticados consulten o gestionen clientes. |
| `django.contrib` | `messages` | Envía alertas visuales (`messages.success()`, `messages.error()`) que se muestran en el frontend. |
| `django.forms` | `ModelForm`, `TextInput`, `EmailInput`, `Textarea`, `FileInput` | Permite construir formularios HTML conectados al modelo `Cliente` con validaciones automáticas. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/clientes/models.py)

```python
class Cliente(ModeloBase):
    nombre_razon_social = models.CharField(max_length=100, verbose_name='Nombre / Razon Social')
    documento = models.CharField(max_length=20, unique=True, verbose_name='DNI / CUIT')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    email = models.EmailField(blank=True, verbose_name='Email')
    direccion = models.TextField(blank=True, verbose_name='Direccion')
    foto = models.ImageField(upload_to='clientes/', null=True, blank=True, verbose_name='Foto')
    activo = models.BooleanField(default=True, verbose_name='Activo')
```

- **Línea 6**: Hereda de `ModeloBase` (que inyecta automáticamente `fecha_creacion` y `fecha_modificacion`).
- **Línea 9 (`documento`)**: Clave única (`unique=True`) que evita duplicar clientes con el mismo DNI o CUIT/RUT.
- **Líneas 20-23 (`Meta.indexes`)**: Crea índices en la base de datos para `documento` y `nombre_razon_social`, permitiendo que el buscador responda en milisegundos aun con miles de registros.
- **Líneas 28-30 (`@property cantidad_vehiculos`)**: Retorna el total de vehículos vinculados usando la relación inversa `self.vehiculos.count()`.

---

### B. [forms.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/clientes/forms.py)

```python
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre_razon_social', 'documento', 'telefono', 'email', 'direccion', 'foto', 'activo']
```
- Vincula todos los campos del modelo con widgets HTML dotados de clases CSS unificadas (`form-input`, `form-textarea`) y placeholders intuitivos.

---

### C. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/clientes/views.py)

#### 1. `cliente_list(request)` (Líneas 11-16)
- Obtiene el parámetro de búsqueda `q` desde la URL (`GET`).
- Si `q` tiene valor, ejecuta un filtro OR con `Q()`:
  ```python
  qs = qs.filter(Q(nombre_razon_social__icontains=query) | Q(documento__icontains=query) | Q(email__icontains=query))
  ```
- Renderiza `clientes/lista.html`.

#### 2. `cliente_detalle(request, pk)` (Líneas 20-35)
- Carga el cliente por su `pk` (`get_object_or_404`).
- Recupera todos los vehículos del cliente mediante `cliente.vehiculos.all()`.
- Consulta el historial de órdenes de trabajo (`OrdenTrabajo.objects.filter(vehiculo__cliente=cliente)`) y facturas emitidas (`Factura.objects.filter(cliente=cliente)`).
- Renderiza una vista 360° en `clientes/detalle.html`.

#### 3. `cliente_crear(request)` y `cliente_editar(request, pk)` (Líneas 39-68)
- Valida que el usuario tenga privilegios (`if not request.user.es_administrador:`).
- Procesa el formulario (`ClienteForm`).
- **Registro de Auditoría**: Tras guardar, crea un registro en la tabla `Auditoria`:
  ```python
  Auditoria.objects.create(
      tabla='cliente', 
      registro_id=cliente.pk, 
      accion='CREAR' if nuevo else 'MODIFICAR',
      usuario=request.user.username, 
      valores_nuevos={'nombre': cliente.nombre_razon_social}
  )
  ```
- Redirige al detalle del cliente recién procesado.

---

### D. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/clientes/urls.py)

- `''` -> `cliente_list` (`clientes:lista`)
- `'crear/'` -> `cliente_crear` (`clientes:crear`)
- `'<int:pk>/'` -> `cliente_detalle` (`clientes:detalle`)
- `'<int:pk>/editar/'` -> `cliente_editar` (`clientes:editar`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/clientes/lista.html` | `base.html` | `clientes`, `query` | Barra de búsqueda instantánea, botón "Nuevo Cliente", listado en tarjetas/tabla con contador de vehículos y accesos directos. |
| `templates/clientes/detalle.html` | `base.html` | `cliente`, `vehiculos`, `ordenes`, `facturas` | Perfil del cliente, pestañas con vehículos asociados (y botón para registrar nuevo vehículo asignado directamente), historial de órdenes de trabajo con estados y facturas pagadas/pendientes. |
| `templates/clientes/form.html` | `base.html` | `form`, `title`, `cliente` (opcional) | Formulario unificado para altas y modificaciones con preview de avatar. |

---

## 4. Opciones de Cambio y Reestructuración

### Opción 1: Implementar Búsqueda Asíncrona con HTMX
Para evitar recargar la página completa al buscar clientes, se puede agregar un endpoint parcial:
```html
<input type="text" name="q" 
       hx-get="{% url 'clientes:lista' %}" 
       hx-target="#tabla-clientes" 
       hx-trigger="keyup changed delay:300ms">
```
En `views.py`, si `request.headers.get('HX-Request')` es verdadero, devolver solo el sub-template `clientes/partials/tabla.html`.

### Opción 2: Soft Delete (Borrado Lógico)
En lugar de eliminar clientes con `delete()`, el sistema ya posee el campo `activo = models.BooleanField(default=True)`. Se puede crear un Custom Manager:
```python
class ActivosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

class Cliente(ModeloBase):
    ...
    objects = ActivosManager()
    all_objects = models.Manager()
```
