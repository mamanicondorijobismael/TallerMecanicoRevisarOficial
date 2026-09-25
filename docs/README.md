# 📚 Manual y Documentación Técnica del Sistema Taller Mecánico y Gomería

Bienvenido a la documentación técnica, arquitectónica y didáctica del sistema de gestión para **Taller Mecánico y Gomería** desarrollado con **Django**.

Cada aplicación del proyecto cuenta con su propio documento exhaustivo donde se detalla:
- **Librerías y módulos utilizados** y para qué sirve cada función importada.
- **Explicación detallada del código** (`models.py`, `views.py`, `forms.py`, `urls.py`, etc.).
- **Templates utilizados**, variables de contexto inyectadas y componentes UI.
- **Opciones de cambio y reestructuración** para escalar o modificar la arquitectura.

---

## 📑 Índice de Módulos y Aplicaciones

| # | Módulo / Aplicación | Documento Técnico | Responsabilidad Principal |
| :-: | :--- | :--- | :--- |
| **01** | **Accounts** | [01_accounts.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/01_accounts.md) | Autenticación, roles de usuario (`DUENO`, `ADMINISTRADOR`, `MECANICO`), perfiles, seguridad y Dashboard principal con KPIs. |
| **02** | **Clientes** | [02_clientes.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/02_clientes.md) | Directorio de clientes, documentos (DNI/CUIT), datos de contacto, historial de vehículos y facturas asociadas. |
| **03** | **Vehículos** | [03_vehiculos.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/03_vehiculos.md) | Registro de patentes, marcas, modelos, VIN, odómetro/kilometraje actual y vinculación con clientes. |
| **04** | **Inventario** | [04_inventario.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/04_inventario.md) | Repuestos, neumáticos con medidas técnicas, categorías, stock actual/mínimo, alertas críticas, movimientos de stock y ventas de mostrador. |
| **05** | **Órdenes de Trabajo** | [05_ordenes.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/05_ordenes.md) | Ciclo de vida de órdenes de taller, asignación de mecánicos, mano de obra, consumo de repuestos, cálculo de IVA y descuento automático de stock. |
| **06** | **Mantenimiento** | [06_mantenimiento.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/06_mantenimiento.md) | Planes preventivos (cambios de aceite, rotación, distribución) y alertas programadas por fecha/kilometraje. |
| **07** | **Reservas** | [07_reservas.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/07_reservas.md) | Agenda de citas y turnos programados con posibilidad de conversión directa en órdenes de trabajo. |
| **08** | **Facturas** | [08_facturas.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/08_facturas.md) | Facturación de órdenes completadas, cálculo tributario, control de estados de cobro y registro de pagos múltiples. |
| **09** | **Reportes** | [09_reportes.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/09_reportes.md) | Informes gerenciales, métricas financieras (ingresos, costos, margen neto), gráficos de ventas, cierres diarios y backups automáticos. |
| **10** | **Core y Configuración** | [10_core_configuracion.md](file:///c:/Users/PC-Solution%2030-9-24/Proyectos/proyecto_taller_mecanico/docs/apps/10_core_configuracion.md) | Modelo abstracto base (`ModeloBase`), tabla transversal de auditoría, configuración de Django (`settings.py`), URLs maestras y plantilla base. |

---

## 🛠️ Stack Tecnológico General

- **Lenguaje**: Python 3.10+
- **Framework Web**: Django 5.x
- **Base de Datos**: SQLite (Entorno local con backups automáticos en `backups/`) / Compatible con PostgreSQL para producción.
- **Frontend**: Django Templates + Vanilla CSS / Tailwind UI + Chart.js para visualizaciones estadísticas.
- **Seguridad**: Autenticación nativa con hashing PBKDF2/Argon2, CSRF protection y sesiones con expiración por inactividad.
