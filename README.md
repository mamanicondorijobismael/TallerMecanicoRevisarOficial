# Proyecto Taller Mecánico

Sistema integral para la gestión de un taller mecánico desarrollado con Django. Permite gestionar clientes, vehículos, inventario de repuestos, reparaciones, citas, y facturación.

## Características
- Gestión de Clientes y Vehículos.
- Control de Inventario y Repuestos.
- Gestión de Citas y Reservas.
- Facturación y Reportes.
- Panel de Administración.

## Requisitos
- Python 3.x
- Django 4.x o superior

## Instalación y Configuración

1. Crear y activar un entorno virtual:
```bash
python -m venv entorno
entorno\Scripts\activate
```

2. Instalar los requerimientos:
```bash
pip install -r requirements.txt
```

3. Aplicar migraciones:
```bash
python manage.py migrate
```

4. Crear un superusuario (opcional):
```bash
python manage.py createsuperuser
```

5. Ejecutar el servidor local:
```bash
python manage.py runserver
```

El proyecto estará disponible en `http://127.0.0.1:8000/`.
