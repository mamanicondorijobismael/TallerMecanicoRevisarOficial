-- =============================================================================
-- SCRIPT COMPLETO DE BASE DE DATOS — TALLER MECÁNICO
-- Motor: SQLite3 (compatible con PostgreSQL con ajustes menores)
-- Generado: Octubre 2026
-- NOTA: Sin módulo de Auditoría (eliminado)
-- =============================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- =============================================================================
-- PASO 1: ELIMINAR TABLAS EXISTENTES (orden inverso de dependencias)
-- =============================================================================

DROP TABLE IF EXISTS "recibos_pago";
DROP TABLE IF EXISTS "recibos_recibo";
DROP TABLE IF EXISTS "facturas_pago";     -- retrocompatibilidad
DROP TABLE IF EXISTS "facturas_factura";  -- retrocompatibilidad
DROP TABLE IF EXISTS "ordenes_repuestoexterno";
DROP TABLE IF EXISTS "ordenes_detalleproducto";
DROP TABLE IF EXISTS "ordenes_detalleservicio";
DROP TABLE IF EXISTS "inventario_movimientostock";
DROP TABLE IF EXISTS "ordenes_ordentrabajo";
DROP TABLE IF EXISTS "inventario_neumatico";
DROP TABLE IF EXISTS "inventario_repuestogenerico";
DROP TABLE IF EXISTS "inventario_productobase";
DROP TABLE IF EXISTS "inventario_categoriaproducto";
DROP TABLE IF EXISTS "vehiculos_vehiculo";
DROP TABLE IF EXISTS "clientes_cliente";
DROP TABLE IF EXISTS "accounts_usuario_groups";
DROP TABLE IF EXISTS "accounts_usuario_user_permissions";
DROP TABLE IF EXISTS "accounts_usuario";
DROP TABLE IF EXISTS "accounts_rol";
DROP TABLE IF EXISTS "core_auditoria";   -- por si existía antes

-- Tablas Django estándar
DROP TABLE IF EXISTS "django_migrations";
DROP TABLE IF EXISTS "django_content_type";
DROP TABLE IF EXISTS "auth_permission";
DROP TABLE IF EXISTS "auth_group";
DROP TABLE IF EXISTS "auth_group_permissions";
DROP TABLE IF EXISTS "django_admin_log";
DROP TABLE IF EXISTS "django_session";


-- =============================================================================
-- PASO 2: TABLAS DJANGO ESTÁNDAR
-- =============================================================================

CREATE TABLE IF NOT EXISTS "django_migrations" (
    "id"      INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app"     VARCHAR(255) NOT NULL,
    "name"    VARCHAR(255) NOT NULL,
    "applied" DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS "django_content_type" (
    "id"       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app_label" VARCHAR(100) NOT NULL,
    "model"    VARCHAR(100) NOT NULL,
    UNIQUE ("app_label", "model")
);

CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id"              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name"            VARCHAR(255) NOT NULL,
    "content_type_id" INTEGER NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename"        VARCHAR(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);

CREATE TABLE IF NOT EXISTS "auth_group" (
    "id"   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id"            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "group_id"      INTEGER NOT NULL REFERENCES "auth_group" ("id"),
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("group_id", "permission_id")
);

CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key"  VARCHAR(40) NOT NULL PRIMARY KEY,
    "session_data" TEXT NOT NULL,
    "expire_date"  DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS "django_session_expire_date" ON "django_session" ("expire_date");


-- =============================================================================
-- PASO 3: MÓDULO ACCOUNTS — Roles y Usuarios
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLA: accounts_rol
-- Control granular de privilegios por módulo y acción
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "accounts_rol" (
    "id"                          INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nombre"                      VARCHAR(50)  NOT NULL UNIQUE,
    "codigo"                      VARCHAR(30)  NOT NULL UNIQUE,
    "descripcion"                 TEXT         NOT NULL DEFAULT '',

    -- Panel de Control
    "puede_ver_dashboard"         BOOL NOT NULL DEFAULT 1,

    -- Clientes
    "puede_ver_clientes"          BOOL NOT NULL DEFAULT 1,
    "puede_crear_clientes"        BOOL NOT NULL DEFAULT 0,
    "puede_editar_clientes"       BOOL NOT NULL DEFAULT 0,
    "puede_eliminar_clientes"     BOOL NOT NULL DEFAULT 0,

    -- Vehículos
    "puede_ver_vehiculos"         BOOL NOT NULL DEFAULT 1,
    "puede_crear_vehiculos"       BOOL NOT NULL DEFAULT 0,
    "puede_editar_vehiculos"      BOOL NOT NULL DEFAULT 0,
    "puede_eliminar_vehiculos"    BOOL NOT NULL DEFAULT 0,

    -- Órdenes de Trabajo
    "puede_ver_ordenes"               BOOL NOT NULL DEFAULT 1,
    "puede_crear_ordenes"             BOOL NOT NULL DEFAULT 0,
    "puede_editar_ordenes"            BOOL NOT NULL DEFAULT 0,
    "puede_cambiar_estado_ordenes"    BOOL NOT NULL DEFAULT 0,
    "puede_eliminar_ordenes"          BOOL NOT NULL DEFAULT 0,

    -- Inventario
    "puede_ver_inventario"        BOOL NOT NULL DEFAULT 1,
    "puede_crear_inventario"      BOOL NOT NULL DEFAULT 0,
    "puede_editar_inventario"     BOOL NOT NULL DEFAULT 0,
    "puede_eliminar_inventario"   BOOL NOT NULL DEFAULT 0,
    "puede_ajustar_stock"         BOOL NOT NULL DEFAULT 0,

    -- Comprobantes / Facturación
    "puede_ver_comprobantes"      BOOL NOT NULL DEFAULT 0,
    "puede_crear_comprobantes"    BOOL NOT NULL DEFAULT 0,
    "puede_cobrar_comprobantes"   BOOL NOT NULL DEFAULT 0,
    "puede_anular_comprobantes"   BOOL NOT NULL DEFAULT 0,

    -- Reportes
    "puede_ver_reportes"          BOOL NOT NULL DEFAULT 0,
    "puede_ver_cierre_diario"     BOOL NOT NULL DEFAULT 0,

    -- Gestión y Seguridad
    "puede_gestionar_usuarios"    BOOL NOT NULL DEFAULT 0,
    "puede_gestionar_roles"       BOOL NOT NULL DEFAULT 0,

    "fecha_creacion"              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion"          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLA: accounts_usuario
-- Extiende AbstractBaseUser de Django
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "accounts_usuario" (
    "id"             INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password"       VARCHAR(128) NOT NULL,
    "last_login"     DATETIME,
    "is_superuser"   BOOL     NOT NULL DEFAULT 0,
    "username"       VARCHAR(50)  NOT NULL UNIQUE,
    "email"          VARCHAR(254) NOT NULL UNIQUE,
    "nombre_completo" VARCHAR(150) NOT NULL,
    "telefono"       VARCHAR(20)  NOT NULL DEFAULT '',
    "foto"           VARCHAR(100),
    "is_active"      BOOL     NOT NULL DEFAULT 1,
    "is_staff"       BOOL     NOT NULL DEFAULT 0,
    "date_joined"    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ultimo_acceso"  DATETIME,
    "rol_id"         INTEGER  REFERENCES "accounts_rol" ("id") ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS "accounts_usuario_groups" (
    "id"       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "usuario_id" INTEGER NOT NULL REFERENCES "accounts_usuario" ("id"),
    "group_id" INTEGER NOT NULL REFERENCES "auth_group" ("id"),
    UNIQUE ("usuario_id", "group_id")
);

CREATE TABLE IF NOT EXISTS "accounts_usuario_user_permissions" (
    "id"            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "usuario_id"    INTEGER NOT NULL REFERENCES "accounts_usuario" ("id"),
    "permission_id" INTEGER NOT NULL REFERENCES "auth_permission" ("id"),
    UNIQUE ("usuario_id", "permission_id")
);

CREATE INDEX IF NOT EXISTS "accounts_usuario_rol_id" ON "accounts_usuario" ("rol_id");


-- =============================================================================
-- PASO 4: MÓDULO CLIENTES
-- =============================================================================

CREATE TABLE IF NOT EXISTS "clientes_cliente" (
    "id"                 INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nombre_razon_social" VARCHAR(100) NOT NULL,
    "documento"          VARCHAR(20)  NOT NULL UNIQUE,
    "telefono"           VARCHAR(20)  NOT NULL DEFAULT '',
    "email"              VARCHAR(254) NOT NULL DEFAULT '',
    "direccion"          TEXT         NOT NULL DEFAULT '',
    "foto"               VARCHAR(100),
    "activo"             BOOL     NOT NULL DEFAULT 1,
    "fecha_creacion"     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS "clientes_cliente_documento" ON "clientes_cliente" ("documento");
CREATE INDEX IF NOT EXISTS "clientes_cliente_nombre"    ON "clientes_cliente" ("nombre_razon_social");


-- =============================================================================
-- PASO 5: MÓDULO VEHÍCULOS
-- =============================================================================

CREATE TABLE IF NOT EXISTS "vehiculos_vehiculo" (
    "id"                  INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "cliente_id"          INTEGER  NOT NULL REFERENCES "clientes_cliente" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "placa"               VARCHAR(10)  NOT NULL UNIQUE,
    "marca"               VARCHAR(30)  NOT NULL,
    "modelo"              VARCHAR(50)  NOT NULL,
    "anio"                INTEGER,
    "vin"                 VARCHAR(50)  UNIQUE,
    "color"               VARCHAR(20)  NOT NULL DEFAULT 'BLANCO',
    "kilometraje_actual"  INTEGER  NOT NULL DEFAULT 0,
    "foto"                VARCHAR(100),
    "activo"              BOOL     NOT NULL DEFAULT 1,
    "fecha_creacion"      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion"  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("color" IN ('BLANCO','NEGRO','GRIS','PLATA','ROJO','AZUL','VERDE','AMARILLO','NARANJA','MARRON','OTRO'))
);

CREATE INDEX IF NOT EXISTS "vehiculos_vehiculo_placa"      ON "vehiculos_vehiculo" ("placa");
CREATE INDEX IF NOT EXISTS "vehiculos_vehiculo_cliente_id" ON "vehiculos_vehiculo" ("cliente_id");


-- =============================================================================
-- PASO 6: MÓDULO INVENTARIO
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLA: inventario_categoriaproducto
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "inventario_categoriaproducto" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nombre"          VARCHAR(50)  NOT NULL UNIQUE,
    "codigo_prefijo"  VARCHAR(10)  NOT NULL DEFAULT 'GEN',
    "tipo"            VARCHAR(20)  NOT NULL DEFAULT 'REPUESTO',
    "descripcion"     TEXT         NOT NULL DEFAULT '',
    "icono"           VARCHAR(50)  NOT NULL DEFAULT 'box',
    "fecha_creacion"  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("tipo" IN ('REPUESTO', 'NEUMATICO'))
);

-- -----------------------------------------------------------------------------
-- TABLA: inventario_productobase
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "inventario_productobase" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "categoria_id"    INTEGER  NOT NULL REFERENCES "inventario_categoriaproducto" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "codigo_sku"      VARCHAR(50)  NOT NULL UNIQUE,
    "nombre"          VARCHAR(150) NOT NULL,
    "descripcion"     TEXT         NOT NULL DEFAULT '',
    "precio_costo"    DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK ("precio_costo" >= 0),
    "precio_venta"    DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK ("precio_venta" >= 0),
    "stock_actual"    INTEGER  NOT NULL DEFAULT 0 CHECK ("stock_actual" >= 0),
    "stock_minimo"    INTEGER  NOT NULL DEFAULT 5  CHECK ("stock_minimo" >= 0),
    "tipo_producto"   VARCHAR(20)  NOT NULL,
    "imagen"          VARCHAR(100),
    "activo"          BOOL     NOT NULL DEFAULT 1,
    "fecha_creacion"  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("tipo_producto" IN ('REPUESTO', 'NEUMATICO'))
);

CREATE INDEX IF NOT EXISTS "inventario_productobase_sku"  ON "inventario_productobase" ("codigo_sku");
CREATE INDEX IF NOT EXISTS "inventario_productobase_tipo" ON "inventario_productobase" ("tipo_producto");
CREATE INDEX IF NOT EXISTS "inventario_productobase_cat"  ON "inventario_productobase" ("categoria_id");

-- -----------------------------------------------------------------------------
-- TABLA: inventario_repuestogenerico (extensión 1-a-1 de ProductoBase)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "inventario_repuestogenerico" (
    "producto_id"    INTEGER  NOT NULL PRIMARY KEY REFERENCES "inventario_productobase" ("id") ON DELETE CASCADE,
    "marca_repuesto" VARCHAR(50)  NOT NULL DEFAULT '',
    "numero_parte"   VARCHAR(100) NOT NULL DEFAULT '',
    "compatible_con" TEXT         NOT NULL DEFAULT ''
);

-- -----------------------------------------------------------------------------
-- TABLA: inventario_neumatico (extensión 1-a-1 de ProductoBase)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "inventario_neumatico" (
    "producto_id"         INTEGER  NOT NULL PRIMARY KEY REFERENCES "inventario_productobase" ("id") ON DELETE CASCADE,
    "marca_neumatico"     VARCHAR(50)  NOT NULL,
    "modelo_neumatico"    VARCHAR(50)  NOT NULL DEFAULT '',
    "ancho"               INTEGER  NOT NULL,
    "perfil"              INTEGER  NOT NULL,
    "diametro"            INTEGER  NOT NULL,
    "indice_carga"        VARCHAR(10)  NOT NULL DEFAULT '',
    "indice_velocidad"    VARCHAR(5)   NOT NULL DEFAULT '',
    "tipo"                VARCHAR(20)  NOT NULL DEFAULT 'ALL_SEASON',
    "estado"              VARCHAR(10)  NOT NULL DEFAULT 'NUEVO',
    "profundidad_restante" DECIMAL(4,1),
    CHECK ("tipo"   IN ('VERANO','INVIERNO','ALL_SEASON','OFF_ROAD')),
    CHECK ("estado" IN ('NUEVO','USADO'))
);


-- =============================================================================
-- PASO 7: MÓDULO ÓRDENES DE TRABAJO
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLA: ordenes_ordentrabajo
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "ordenes_ordentrabajo" (
    "id"               INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "numero_orden"     VARCHAR(20)  NOT NULL UNIQUE,
    "vehiculo_id"      INTEGER  NOT NULL REFERENCES "vehiculos_vehiculo" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "mecanico_id"      INTEGER  REFERENCES "accounts_usuario" ("id") ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
    "creado_por_id"    INTEGER  REFERENCES "accounts_usuario" ("id") ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
    "estado"           VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE',
    "kilometraje"      INTEGER  NOT NULL DEFAULT 0,
    "diagnostico"      TEXT     NOT NULL DEFAULT '',
    "observaciones"    TEXT     NOT NULL DEFAULT '',
    "fecha_prometida"  DATETIME,
    "fecha_cierre"     DATETIME,
    "fecha_creacion"   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("estado" IN ('PENDIENTE','EN_PROCESO','PAUSADA','COMPLETADA','COBRADA','CANCELADA'))
);

CREATE INDEX IF NOT EXISTS "ordenes_ot_numero"     ON "ordenes_ordentrabajo" ("numero_orden");
CREATE INDEX IF NOT EXISTS "ordenes_ot_estado"     ON "ordenes_ordentrabajo" ("estado");
CREATE INDEX IF NOT EXISTS "ordenes_ot_vehiculo"   ON "ordenes_ordentrabajo" ("vehiculo_id");
CREATE INDEX IF NOT EXISTS "ordenes_ot_mecanico"   ON "ordenes_ordentrabajo" ("mecanico_id");

-- -----------------------------------------------------------------------------
-- TABLA: inventario_movimientostock (aquí porque FK a ordenes)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "inventario_movimientostock" (
    "id"               INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "producto_id"      INTEGER  NOT NULL REFERENCES "inventario_productobase" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "tipo_movimiento"  VARCHAR(20)  NOT NULL,
    "cantidad"         INTEGER  NOT NULL,
    "stock_resultante" INTEGER  NOT NULL,
    "motivo"           VARCHAR(200) NOT NULL,
    "orden_id"         INTEGER  REFERENCES "ordenes_ordentrabajo" ("id") ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED,
    "usuario"          VARCHAR(150) NOT NULL DEFAULT '',
    "precio_unitario"  DECIMAL(12,2),
    "fecha_movimiento" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("tipo_movimiento" IN ('ENTRADA','SALIDA','AJUSTE','VENTA_DIRECTA'))
);

CREATE INDEX IF NOT EXISTS "inventario_mov_producto" ON "inventario_movimientostock" ("producto_id");
CREATE INDEX IF NOT EXISTS "inventario_mov_fecha"    ON "inventario_movimientostock" ("fecha_movimiento");

-- -----------------------------------------------------------------------------
-- TABLA: ordenes_detalleservicio
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "ordenes_detalleservicio" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "orden_id"        INTEGER  NOT NULL REFERENCES "ordenes_ordentrabajo" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "descripcion"     VARCHAR(200) NOT NULL,
    "cantidad"        DECIMAL(8,2) NOT NULL DEFAULT 1.00 CHECK ("cantidad" >= 0),
    "precio_unitario" DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK ("precio_unitario" >= 0)
);

CREATE INDEX IF NOT EXISTS "ordenes_servicio_orden" ON "ordenes_detalleservicio" ("orden_id");

-- -----------------------------------------------------------------------------
-- TABLA: ordenes_detalleproducto
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "ordenes_detalleproducto" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "orden_id"        INTEGER  NOT NULL REFERENCES "ordenes_ordentrabajo" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "producto_id"     INTEGER  NOT NULL REFERENCES "inventario_productobase" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "cantidad"        INTEGER  NOT NULL DEFAULT 1 CHECK ("cantidad" >= 1),
    "precio_unitario" DECIMAL(12,2) NOT NULL DEFAULT 0.00
);

CREATE INDEX IF NOT EXISTS "ordenes_prod_orden"   ON "ordenes_detalleproducto" ("orden_id");
CREATE INDEX IF NOT EXISTS "ordenes_prod_producto" ON "ordenes_detalleproducto" ("producto_id");

-- -----------------------------------------------------------------------------
-- TABLA: ordenes_repuestoexterno
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "ordenes_repuestoexterno" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "orden_id"        INTEGER  NOT NULL REFERENCES "ordenes_ordentrabajo" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "descripcion"     VARCHAR(200) NOT NULL,
    "proveedor"       VARCHAR(100) NOT NULL DEFAULT '',
    "cantidad"        INTEGER  NOT NULL DEFAULT 1 CHECK ("cantidad" >= 1),
    "precio_unitario" DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK ("precio_unitario" >= 0)
);

CREATE INDEX IF NOT EXISTS "ordenes_repext_orden" ON "ordenes_repuestoexterno" ("orden_id");


-- =============================================================================
-- PASO 8: MÓDULO RECIBOS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLA: recibos_recibo
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "recibos_recibo" (
    "id"              INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "numero_recibo"   VARCHAR(20)  NOT NULL UNIQUE,
    "orden_id"        INTEGER  NOT NULL UNIQUE REFERENCES "ordenes_ordentrabajo" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "cliente_id"      INTEGER  NOT NULL REFERENCES "clientes_cliente" ("id") ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
    "fecha_emision"   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "subtotal"        DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    "iva_porcentaje"  DECIMAL(5,2)  NOT NULL DEFAULT 21.00,
    "iva_monto"       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    "total"           DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    "estado_pago"     VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE',
    "notas"           TEXT         NOT NULL DEFAULT '',
    "fecha_creacion"  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fecha_modificacion" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ("estado_pago" IN ('PENDIENTE','PARCIAL','PAGADA','ANULADA'))
);

CREATE INDEX IF NOT EXISTS "recibos_recibo_cliente" ON "recibos_recibo" ("cliente_id");
CREATE INDEX IF NOT EXISTS "recibos_recibo_estado"  ON "recibos_recibo" ("estado_pago");

-- -----------------------------------------------------------------------------
-- TABLA: recibos_pago
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS "recibos_pago" (
    "id"          INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
    "recibo_id"   INTEGER  NOT NULL REFERENCES "recibos_recibo" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "monto"       DECIMAL(12,2) NOT NULL CHECK ("monto" > 0),
    "metodo_pago" VARCHAR(30)  NOT NULL DEFAULT 'EFECTIVO',
    "referencia"  VARCHAR(100) NOT NULL DEFAULT '',
    "fecha"       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usuario"     VARCHAR(150) NOT NULL DEFAULT '',
    CHECK ("metodo_pago" IN ('EFECTIVO'))
);

CREATE INDEX IF NOT EXISTS "recibos_pago_recibo" ON "recibos_pago" ("recibo_id");


-- =============================================================================
-- PASO 9: DATOS INICIALES — Roles
-- =============================================================================

INSERT OR IGNORE INTO "accounts_rol" (
    nombre, codigo, descripcion,
    puede_ver_dashboard,
    puede_ver_clientes, puede_crear_clientes, puede_editar_clientes, puede_eliminar_clientes,
    puede_ver_vehiculos, puede_crear_vehiculos, puede_editar_vehiculos, puede_eliminar_vehiculos,
    puede_ver_ordenes, puede_crear_ordenes, puede_editar_ordenes, puede_cambiar_estado_ordenes, puede_eliminar_ordenes,
    puede_ver_inventario, puede_crear_inventario, puede_editar_inventario, puede_eliminar_inventario, puede_ajustar_stock,
    puede_ver_comprobantes, puede_crear_comprobantes, puede_cobrar_comprobantes, puede_anular_comprobantes,
    puede_ver_reportes, puede_ver_cierre_diario,
    puede_gestionar_usuarios, puede_gestionar_roles
) VALUES
-- DUEÑO: Acceso total
(
    'Dueño / Gerencia General', 'DUENO',
    'Acceso total y sin restricciones a todos los módulos, reportes y configuración.',
    1,
    1,1,1,1,
    1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,
    1,1,
    1,1
),
-- ADMINISTRADOR
(
    'Administrador del Taller', 'ADMINISTRADOR',
    'Gestión operativa, comercial y de personal.',
    1,
    1,1,1,1,
    1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,1,
    1,1,1,1,
    1,1,
    1,1
),
-- RECEPCIONISTA
(
    'Recepción y Asesoría de Servicio', 'RECEPCIONISTA',
    'Atención al cliente, ingreso de vehículos, generación de órdenes y cobros.',
    1,
    1,1,1,0,
    1,1,1,0,
    1,1,1,0,0,
    1,0,0,0,0,
    1,1,1,0,
    0,0,
    0,0
),
-- MECANICO
(
    'Mecánico / Operario', 'MECANICO',
    'Operaciones de taller: visualización y actualización de estado en órdenes de trabajo.',
    1,
    1,0,0,0,
    1,0,0,0,
    1,0,0,1,0,
    1,0,0,0,0,
    0,0,0,0,
    0,0,
    0,0
);


-- =============================================================================
-- PASO 10: DATOS INICIALES — Usuarios
-- NOTA: Las contraseñas están hasheadas en formato Django PBKDF2 (password: admin123)
-- Para producción cambiar contraseñas con: manage.py changepassword <usuario>
-- =============================================================================

INSERT OR IGNORE INTO "accounts_usuario" (
    username, email, nombre_completo, password,
    is_active, is_staff, is_superuser,
    rol_id, date_joined
) VALUES
(
    'admin', 'admin@taller.com', 'Administrador Principal',
    'pbkdf2_sha256$720000$placeholder$hashedpassword_admin123',
    1, 1, 1,
    (SELECT id FROM accounts_rol WHERE codigo = 'DUENO'),
    CURRENT_TIMESTAMP
),
(
    'supervisor', 'supervisor@taller.com', 'Carlos Supervilla',
    'pbkdf2_sha256$720000$placeholder$hashedpassword_admin123',
    1, 0, 0,
    (SELECT id FROM accounts_rol WHERE codigo = 'ADMINISTRADOR'),
    CURRENT_TIMESTAMP
),
(
    'recepcionista', 'recepcion@taller.com', 'María González',
    'pbkdf2_sha256$720000$placeholder$hashedpassword_admin123',
    1, 0, 0,
    (SELECT id FROM accounts_rol WHERE codigo = 'RECEPCIONISTA'),
    CURRENT_TIMESTAMP
),
(
    'mecanico1', 'mecanico1@taller.com', 'Juan Rodríguez',
    'pbkdf2_sha256$720000$placeholder$hashedpassword_admin123',
    1, 0, 0,
    (SELECT id FROM accounts_rol WHERE codigo = 'MECANICO'),
    CURRENT_TIMESTAMP
),
(
    'mecanico2', 'mecanico2@taller.com', 'Pedro Ramírez',
    'pbkdf2_sha256$720000$placeholder$hashedpassword_admin123',
    1, 0, 0,
    (SELECT id FROM accounts_rol WHERE codigo = 'MECANICO'),
    CURRENT_TIMESTAMP
);

-- NOTA IMPORTANTE: Los usuarios creados aquí NO tendrán password funcional.
-- Django genera el hash en Python. Para activar los usuarios correctamente,
-- el sistema los auto-sincroniza en el primer login vía _asegurar_roles_y_usuarios().
-- Contraseña por defecto para todos: admin123


-- =============================================================================
-- PASO 11: REGISTRO DE MIGRACIONES APLICADAS
-- =============================================================================

INSERT OR IGNORE INTO "django_migrations" (app, name, applied) VALUES
    ('contenttypes', '0001_initial',                            CURRENT_TIMESTAMP),
    ('contenttypes', '0002_remove_content_type_name',           CURRENT_TIMESTAMP),
    ('auth',         '0001_initial',                            CURRENT_TIMESTAMP),
    ('auth',         '0002_alter_permission_name_max_length',   CURRENT_TIMESTAMP),
    ('auth',         '0003_alter_user_email_max_length',        CURRENT_TIMESTAMP),
    ('auth',         '0004_alter_user_username_opts',           CURRENT_TIMESTAMP),
    ('auth',         '0005_alter_user_last_login_null',         CURRENT_TIMESTAMP),
    ('auth',         '0006_require_contenttypes_0002',          CURRENT_TIMESTAMP),
    ('auth',         '0007_alter_validators_add_error_messages',CURRENT_TIMESTAMP),
    ('auth',         '0008_alter_user_username_max_length',     CURRENT_TIMESTAMP),
    ('auth',         '0009_alter_user_last_name_max_length',    CURRENT_TIMESTAMP),
    ('auth',         '0010_alter_group_name_max_length',        CURRENT_TIMESTAMP),
    ('auth',         '0011_update_proxy_permissions',           CURRENT_TIMESTAMP),
    ('auth',         '0012_alter_user_first_name_max_length',   CURRENT_TIMESTAMP),
    ('accounts',     '0001_initial',                            CURRENT_TIMESTAMP),
    ('accounts',     '0002_rol_alter_usuario_rol',              CURRENT_TIMESTAMP),
    ('accounts',     '0003_remove_rol_puede_ver_auditoria',     CURRENT_TIMESTAMP),
    ('clientes',     '0001_initial',                            CURRENT_TIMESTAMP),
    ('vehiculos',    '0001_initial',                            CURRENT_TIMESTAMP),
    ('inventario',   '0001_initial',                            CURRENT_TIMESTAMP),
    ('ordenes',      '0001_initial',                            CURRENT_TIMESTAMP),
    ('recibos',      '0001_initial',                            CURRENT_TIMESTAMP),
    ('core',         '0001_initial',                            CURRENT_TIMESTAMP),
    ('core',         '0002_delete_auditoria',                   CURRENT_TIMESTAMP),
    ('sessions',     '0001_initial',                            CURRENT_TIMESTAMP),
    ('admin',        '0001_initial',                            CURRENT_TIMESTAMP),
    ('admin',        '0002_logentry_remove_auto_add',           CURRENT_TIMESTAMP),
    ('admin',        '0003_logentry_add_action_flag_choices',   CURRENT_TIMESTAMP);


-- =============================================================================
-- FIN DEL SCRIPT
-- =============================================================================
-- Total de tablas de negocio: 15
-- Total de tablas Django:     7
-- Total general:              22
-- =============================================================================
