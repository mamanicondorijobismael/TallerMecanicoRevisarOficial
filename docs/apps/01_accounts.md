# 01. Documentación Técnica y Explicación de Código: App `accounts`

La aplicación `accounts` gestiona la autenticación, roles de usuario (Dueño, Administrador, Mecánico), perfiles, gestión de contraseñas, auditoría de accesos y el Dashboard principal con KPIs del taller mecánico.

---

## 1. Librerías y Módulos Utilizados

A continuación se detalla cada librería y función importada en los archivos de la app:

| Librería / Módulo | Funciones / Clases | Propósito y Utilidad en la App |
| :--- | :--- | :--- |
| `django.contrib.auth.models` | `AbstractBaseUser`, `BaseUserManager`, `PermissionsMixin` | Permite crear un modelo de usuario personalizado (`Usuario`) con soporte para roles, permisos de Django y hashing seguro de contraseñas. |
| `django.contrib.auth` | `login`, `logout`, `authenticate` | `authenticate` valida credenciales contra la BD; `login` crea la sesión en cookies/servidor; `logout` destruye la sesión activa. |
| `django.contrib.auth.decorators` | `login_required` | Decorador que protege vistas para que solo usuarios autenticados puedan ejecutarlas. Si no está logueado, redirige al login. |
| `django.contrib.auth.forms` | `UserCreationForm`, `PasswordChangeForm`, `SetPasswordForm` | Formularios estándar de Django para crear usuarios, cambiar la contraseña del usuario logueado o resetearla como admin. |
| `django.contrib` | `messages` | Permite enviar notificaciones flash al frontend (ej. `messages.success()`, `messages.error()`). |
| `django.shortcuts` | `render`, `redirect`, `get_object_or_404` | `render` une un template HTML con un contexto; `redirect` envía una redirección HTTP 302; `get_object_or_404` busca un registro o lanza un error 404 si no existe. |
| `django.db.models` | `Sum`, `Count`, `Q`, `F`, `TextChoices` | Agregaciones numéricas (`Sum`, `Count`), consultas complejas con operadores OR/AND (`Q`), referencias directas a columnas en BD (`F`), y enumeraciones legibles (`TextChoices`). |
| `django.utils` | `timezone` | Manejo de fechas y horas conscientes de la zona horaria configurada en Django (`timezone.now()`). |
| `datetime` | `timedelta` | Cálculo de intervalos de tiempo (ej. `hoy - timedelta(days=30)` para filtrar los últimos 30 días). |
| `decimal` | `Decimal` | Manejo de cálculos financieros y monetarios con precisión exacta sin pérdida de decimales por punto flotante. |

---

## 2. Explicación Detallada del Código por Archivo

### A. [models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/accounts/models.py)

#### Gestor de Usuarios (`UsuarioManager`)
```python
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, nombre_completo, password=None, **extra_fields):
```
- **Líneas 7-14**: Método para crear usuarios normales. Valida que `username` no esté vacío, normaliza el correo electrónico (minúsculas en el dominio con `normalize_email`), crea la instancia, encripta la contraseña con `user.set_password(password)` y guarda en base de datos.
- **Líneas 16-20 (`create_superuser`)**: Método invocado por `python manage.py createsuperuser`. Fuerza `is_staff=True`, `is_superuser=True` y `rol='DUENO'`, garantizando acceso total.

#### Modelo de Usuario Personalizado (`Usuario`)
```python
class Usuario(AbstractBaseUser, PermissionsMixin):
    class Rol(models.TextChoices):
        DUENO = 'DUENO', 'Dueno'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        MECANICO = 'MECANICO', 'Mecanico'
```
- **Líneas 24-27**: Define la enumeración de roles disponibles en el sistema con `models.TextChoices`.
- **Líneas 29-39**: Campos del usuario:
  - `username` y `email`: Únicos en el sistema para evitar duplicados.
  - `nombre_completo`: Nombre real del empleado/dueño.
  - `rol`: Almacena el rol con valor por defecto `MECANICO`.
  - `telefono`, `foto`: Datos de contacto y multimedia (subida a `media/usuarios/`).
  - `is_active`, `is_staff`, `date_joined`, `ultimo_acceso`: Flags de estado del usuario.
- **Líneas 42-43**: Define `USERNAME_FIELD = 'username'` como identificador de inicio de sesión y `REQUIRED_FIELDS` requeridos en CLI.
- **Líneas 53-63 (Properties de Permisos)**:
  - `@property es_dueno`: Retorna `True` si el rol es `DUENO` o si es superusuario.
  - `@property es_administrador`: Retorna `True` si es `ADMINISTRADOR`, `DUENO` o superusuario.
  - `@property es_mecanico`: Retorna `True` ya que en el taller todos los roles pueden atender órdenes operativas.

---

### B. [forms.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/accounts/forms.py)

- **`UsuarioCreationForm(UserCreationForm)`**: Formulario que extiende del formulario de creación con doble campo de contraseña. Aplica clases CSS (`form-input`) mediante el diccionario `widgets` para que coincida con el diseño de Tailwind/CSS del frontend. En `save(commit=True)` asigna manualmente `telefono`, `rol` y `foto`.
- **`UsuarioChangeForm(forms.ModelForm)`**: Formulario para editar usuarios existentes sin obligar a cambiar la contraseña en cada guardado.

---

### C. [views.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/accounts/views.py)

- **`_asegurar_usuarios()` (Líneas 24-43)**: Función auxiliar de resiliencia que asegura que los usuarios esenciales de demostración/administración existan siempre en el entorno de desarrollo.
- **`login_view(request)` (Líneas 46-83)**:
  - Si el usuario ya está autenticado, redirige al `dashboard`.
  - En método `POST`, extrae `username` y `password`, y llama a `authenticate(request, username, password)`.
  - Si las credenciales son válidas y `user.is_active` es verdadero, inicia sesión con `login(request, user)` y redirige al dashboard o al parámetro `next`.
  - Si falla, emite un mensaje de error mediante `messages.error()`.
- **`logout_view(request)` (Líneas 86-89)**: Llama a `logout(request)` y redirige al login con notificación informativa.
- **`dashboard(request)` (Líneas 92-165)**:
  - Vista central del sistema. Calcula en tiempo real los KPIs:
    - `ordenes_activas`: Órdenes en estado `PENDIENTE`, `EN_PROCESO` o `PAUSADA`.
    - `ordenes_completadas_mes`: Órdenes finalizadas dentro del período seleccionado (por defecto 30 días).
    - `ingresos_total`, `costos_total`, `ganancia_neta`, `ticket_promedio`.
    - `stock_critico_count` y `productos_criticos`: Repuestos cuyo `stock_actual <= stock_minimo`.
    - `alertas_count`: Alertas de mantenimiento pendientes para vehículos registrados.
    - `reservas_proximas`, `clientes_total`, `vehiculos_total`.
  - Inyecta todo al template `accounts/dashboard.html`.
- **`usuario_lista`, `usuario_crear`, `usuario_editar`, `perfil`, `cambiar_password`**: Vistas CRUD para administración de personal y seguridad de cuenta personal.

---

### D. [urls.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/apps/accounts/urls.py)

Mapea los endpoints:
- `''` -> `dashboard` (Nombre: `dashboard`)
- `'login/'` -> `login_view` (Nombre: `login`)
- `'logout/'` -> `logout_view` (Nombre: `logout`)
- `'usuarios/'` -> `usuario_lista` (Nombre: `usuario_lista`)
- `'usuarios/crear/'` -> `usuario_crear` (Nombre: `usuario_crear`)
- `'usuarios/<int:pk>/editar/'` -> `usuario_editar` (Nombre: `usuario_editar`)
- `'perfil/'` -> `perfil` (Nombre: `perfil`)
- `'cambiar-password/'` -> `cambiar_password` (Nombre: `cambiar_password`)

---

## 3. Templates Utilizados y Contexto

| Template | Hereda de | Contexto Inyectado | Elementos Clave del Template |
| :--- | :--- | :--- | :--- |
| `templates/accounts/login.html` | No hereda (Full Page) | `None` (Usa form POST directo) | Formulario con CSRF token (`{% csrf_token %}`), inputs de usuario/contraseña, alertas de error. |
| `templates/accounts/dashboard.html` | `base.html` | `ordenes_activas`, `ingresos_total`, `ganancia_neta`, `stock_critico_count`, `productos_criticos`, `alertas_recientes`, `reservas_proximas`, etc. | Tarjetas de métricas (KPIs), tablas de órdenes recientes, badges de estado, alertas de stock bajo y gráficos. |
| `templates/accounts/usuarios_lista.html` | `base.html` | `usuarios` | Tabla con lista de empleados, avatares, roles con badges de color y botones de acción (editar / resetear contraseña). |
| `templates/accounts/usuario_form.html` | `base.html` | `form`, `title`, `usuario` | Formulario de creación y edición de usuario con soporte para subida de imagen (`enctype="multipart/form-data"`). |
| `templates/accounts/perfil.html` | `base.html` | `form` | Vista de datos personales del usuario en sesión. |
| `templates/accounts/cambiar_password.html` | `base.html` | `form`, `title` | Formulario de actualización de contraseña con validaciones de longitud y complejidad. |

---

## 4. Opciones de Cambio y Reestructuración

Si en el futuro se desea modificar la arquitectura de esta aplicación, aquí tienes las mejores alternativas:

### Opción 1: Migrar a Vistas Basadas en Clases (CBV)
Si prefieres el estándar formal de Django:
```python
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

class UsuarioListView(ListView):
    model = Usuario
    template_name = 'accounts/usuarios_lista.html'
    context_object_name = 'usuarios'
```

### Opción 2: Implementar Autenticación por Tokens o JWT para App Móvil
Si los mecánicos van a usar una app móvil en Flutter o React Native, se puede integrar `django-rest-framework-simplejwt`:
```bash
pip install djangorestframework-simplejwt
```
Configurando en `settings.py` y creando endpoints en `api_urls.py` con `TokenObtainPairView`.

### Opción 3: Desacoplar Permisos mediante Django Groups o Rules
Actualmente los permisos se verifican mediante `@property es_administrador` en el modelo. Se puede evolucionar hacia `django.contrib.auth.models.Group` o la librería `django-rules` para permisos granulares basados en reglas de negocio.
