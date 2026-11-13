# 10. Documentación Técnica y Explicación de Código: `core` y `configuracion`

Este documento explica la infraestructura central del proyecto: el módulo base (`core`), la clase abstracta transversal `ModeloBase`, el archivo de configuración global (`configuracion/settings.py`), el enrutador maestro (`configuracion/urls.py`) y la plantilla maestra de interfaz de usuario (`templates/base.html`).

---

## 1. Módulo Central `core`

### A. [core/models.py](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/core/models.py)

#### 1. Clase Abstracta `ModeloBase`
```python
class ModeloBase(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Ultima modificacion')

    class Meta:
        abstract = True
```
- **¿Qué hace?**: Es la clase base abstracta de la que heredan los modelos principales del sistema (`Cliente`, `Vehiculo`, `ProductoBase`, `CategoriaProducto`, `OrdenTrabajo`, `Recibo`).
- `auto_now_add=True`: Guarda automáticamente la fecha y hora exacta en el momento en que se inserta el registro por primera vez.
- `auto_now=True`: Se actualiza automáticamente cada vez que se llama al método `.save()`.
- `abstract = True`: Indica a Django que no debe crear una tabla física `core_modelobase` en la base de datos, sino transferir estos dos campos a todas las clases hijas.

---

## 2. Configuración Global del Proyecto (`configuracion/settings.py`)

A continuación se explican los bloques clave de configuración:

- **`BASE_DIR`**: Ruta absoluta raíz del proyecto calculada con `pathlib.Path(__file__).resolve().parent.parent`.
- **`SECRET_KEY`**: Clave criptográfica utilizada por Django para firmar cookies de sesión y tokens CSRF.
- **`INSTALLED_APPS`**: Lista de aplicaciones activas. Contiene las 6 aplicaciones oficiales de Django (`admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`) más las aplicaciones del taller:
  ```python
  'core', 'apps.accounts', 'apps.clientes', 'apps.vehiculos', 'apps.inventario', 
  'apps.ordenes', 'apps.recibos', 'apps.reportes'
  ```
- **`MIDDLEWARE`**: Cadena de procesamiento de peticiones:
  - `SecurityMiddleware`: Protecciones HTTP básicas.
  - `SessionMiddleware`: Asocia solicitudes con la sesión del usuario.
  - `CsrfViewMiddleware`: Protección contra ataques Cross-Site Request Forgery en formularios POST.
  - `AuthenticationMiddleware`: Inyecta el objeto `request.user` en cada petición.
  - `MessageMiddleware`: Permite el paso de mensajes flash a las vistas y plantillas.
- **`TEMPLATES`**: Configura el motor de renderizado de plantillas `DjangoTemplates`. Define `DIRS = [BASE_DIR / 'templates']` y procesadores de contexto que exponen variables globales (`request`, `user`, `messages`, `MEDIA_URL`).
- **`AUTH_USER_MODEL = 'accounts.Usuario'`**: Le indica a Django que reemplace el modelo de usuario estándar por nuestro modelo personalizado con soporte de roles.
- **`TIME_ZONE = 'America/Argentina/Buenos_Aires'` y `LANGUAGE_CODE = 'es-ar'`**: Configuración regional para formatos de fecha, hora y moneda.
- **`IVA_PORCENTAJE = 21`**: Tasa estándar de impuesto al valor agregado utilizada en la app de órdenes y recibos.
- **`SESSION_COOKIE_AGE = 1800` y `SESSION_SAVE_EVERY_REQUEST = True`**: Cierra la sesión automáticamente tras 30 minutos de inactividad por seguridad operativa.

---

## 3. Enrutador Principal (`configuracion/urls.py`)

Centraliza el prefijo de rutas de cada módulo del sistema:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('vehiculos/', include('apps.vehiculos.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('ordenes/', include('apps.ordenes.urls')),
    path('recibos/', include('apps.recibos.urls')),
    path('reportes/', include('apps.reportes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
- Vincula la raíz vacía `''` con `accounts.urls` (donde reside el dashboard y login).
- Añade `static(settings.MEDIA_URL, ...)` para servir archivos multimedia (fotos de clientes, vehículos, repuestos) en modo de desarrollo.

---

## 4. Estructura y Funcionamiento de la Plantilla Maestra (`templates/base.html`)

`templates/base.html` es el esqueleto visual de toda la aplicación. Provee:

1. **Header y Navegación Lateral (Sidebar)**:
   - Menú responsivo con enlaces activos a cada app según el rol del usuario logueado (`{% if user.es_administrador %}`, `{% if user.es_dueno %}`).
   - Información del usuario en sesión (`{{ user.nombre_completo }}`) y avatar.
2. **Contenedor de Mensajes Flash**:
   - Itera sobre `{% for message in messages %}` mostrando toasts/alertas automáticas con estilos acordes (éxito en verde, error en rojo, info en azul).
3. **Bloques Heredables (`{% block %}`)**:
   - `{% block title %}`: Título dinámico de la pestaña del navegador.
   - `{% block extra_head %}`: Espacio para inyectar scripts o estilos específicos de cada página (ej. Chart.js en reportes).
   - `{% block content %}`: Contenedor principal donde cada plantilla hija inyecta su contenido específico.
   - `{% block extra_js %}`: Espacio para scripts interactivos al pie de la página.

---

## 5. Opciones de Cambio y Reestructuración

### Opción 1: Variables de Entorno con `python-dotenv` / `django-environ`
Para no almacenar credenciales o la `SECRET_KEY` directamente en el código:
```python
import environ
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
```

### Opción 2: Base de Datos de Producción (PostgreSQL)
```python
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres:password@localhost:5432/taller_db')
}
```

### Opción 3: Despliegue con Servidor de Producción (Gunicorn + WhiteNoise)
Para servir archivos estáticos sin depender del servidor de desarrollo de Django:
```bash
pip install whitenoise gunicorn
```
Añadir `'whitenoise.middleware.WhiteNoiseMiddleware'` a `MIDDLEWARE` en `settings.py`.
