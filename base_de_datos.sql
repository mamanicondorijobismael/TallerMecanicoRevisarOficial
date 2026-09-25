    -- =============================================================================
    -- ESQUEMA DDL DE BASE DE DATOS - SISTEMA TALLER MECÁNICO Y GOMERÍA (TALLERGES)
    -- Compatible con SQLite 3 / PostgreSQL 14+ / MySQL 8.0+
    -- =============================================================================

    -- 1. TABLA: accounts_usuario
    CREATE TABLE IF NOT EXISTS accounts_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        password VARCHAR(128) NOT NULL,
        last_login DATETIME NULL,
        is_superuser BOOLEAN NOT NULL DEFAULT 0,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(254) NOT NULL UNIQUE,
        nombre_completo VARCHAR(150) NOT NULL,
        rol VARCHAR(20) NOT NULL DEFAULT 'MECANICO',
        telefono VARCHAR(20) NOT NULL DEFAULT '',
        foto VARCHAR(100) NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        is_staff BOOLEAN NOT NULL DEFAULT 0,
        date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ultimo_acceso DATETIME NULL
    );

    CREATE INDEX IF NOT EXISTS idx_usuario_rol ON accounts_usuario(rol);
    CREATE INDEX IF NOT EXISTS idx_usuario_active ON accounts_usuario(is_active);


    -- 2. TABLA: clientes_cliente
    CREATE TABLE IF NOT EXISTS clientes_cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        nombre_razon_social VARCHAR(100) NOT NULL,
        documento VARCHAR(20) NOT NULL UNIQUE,
        telefono VARCHAR(20) NOT NULL DEFAULT '',
        email VARCHAR(254) NOT NULL DEFAULT '',
        direccion TEXT NOT NULL DEFAULT '',
        foto VARCHAR(100) NULL,
        activo BOOLEAN NOT NULL DEFAULT 1
    );

    CREATE INDEX IF NOT EXISTS idx_cliente_documento ON clientes_cliente(documento);
    CREATE INDEX IF NOT EXISTS idx_cliente_nombre ON clientes_cliente(nombre_razon_social);


    -- 3. TABLA: vehiculos_vehiculo
    CREATE TABLE IF NOT EXISTS vehiculos_vehiculo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        patente VARCHAR(15) NOT NULL UNIQUE,
        marca VARCHAR(50) NOT NULL,
        modelo VARCHAR(50) NOT NULL,
        anio INTEGER NOT NULL,
        vin VARCHAR(30) NOT NULL DEFAULT '',
        color VARCHAR(30) NOT NULL DEFAULT '',
        kilometraje_actual INTEGER NOT NULL DEFAULT 0,
        foto VARCHAR(100) NULL,
        activo BOOLEAN NOT NULL DEFAULT 1,
        cliente_id INTEGER NOT NULL,
        FOREIGN KEY (cliente_id) REFERENCES clientes_cliente(id) ON DELETE RESTRICT
    );

    CREATE INDEX IF NOT EXISTS idx_vehiculo_patente ON vehiculos_vehiculo(patente);
    CREATE INDEX IF NOT EXISTS idx_vehiculo_cliente ON vehiculos_vehiculo(cliente_id);


    -- 4. TABLA: inventario_categoriaproducto
    CREATE TABLE IF NOT EXISTS inventario_categoriaproducto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        nombre VARCHAR(50) NOT NULL UNIQUE,
        tipo VARCHAR(20) NOT NULL DEFAULT 'REPUESTO',
        descripcion TEXT NOT NULL DEFAULT '',
        icono VARCHAR(50) NOT NULL DEFAULT 'box'
    );


    -- 5. TABLA: inventario_productobase
    CREATE TABLE IF NOT EXISTS inventario_productobase (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        codigo_sku VARCHAR(50) NOT NULL UNIQUE,
        nombre VARCHAR(150) NOT NULL,
        descripcion TEXT NOT NULL DEFAULT '',
        precio_costo DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        precio_venta DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        stock_actual INTEGER NOT NULL DEFAULT 0,
        stock_minimo INTEGER NOT NULL DEFAULT 5,
        tipo_producto VARCHAR(20) NOT NULL,
        imagen VARCHAR(100) NULL,
        activo BOOLEAN NOT NULL DEFAULT 1,
        categoria_id INTEGER NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES inventario_categoriaproducto(id) ON DELETE RESTRICT
    );

    CREATE INDEX IF NOT EXISTS idx_producto_sku ON inventario_productobase(codigo_sku);
    CREATE INDEX IF NOT EXISTS idx_producto_tipo ON inventario_productobase(tipo_producto);


    -- 6. TABLA: inventario_repuestogenerico
    CREATE TABLE IF NOT EXISTS inventario_repuestogenerico (
        producto_id INTEGER PRIMARY KEY,
        marca_repuesto VARCHAR(50) NOT NULL DEFAULT '',
        numero_parte VARCHAR(100) NOT NULL DEFAULT '',
        compatible_con TEXT NOT NULL DEFAULT '',
        FOREIGN KEY (producto_id) REFERENCES inventario_productobase(id) ON DELETE CASCADE
    );


    -- 7. TABLA: inventario_neumatico
    CREATE TABLE IF NOT EXISTS inventario_neumatico (
        producto_id INTEGER PRIMARY KEY,
        marca_neumatico VARCHAR(50) NOT NULL,
        modelo_neumatico VARCHAR(50) NOT NULL DEFAULT '',
        ancho INTEGER NOT NULL,
        perfil INTEGER NOT NULL,
        diametro INTEGER NOT NULL,
        indice_carga VARCHAR(10) NOT NULL DEFAULT '',
        indice_velocidad VARCHAR(5) NOT NULL DEFAULT '',
        tipo VARCHAR(20) NOT NULL DEFAULT 'ALL_SEASON',
        estado VARCHAR(10) NOT NULL DEFAULT 'NUEVO',
        profundidad_restante DECIMAL(4, 1) NULL,
        FOREIGN KEY (producto_id) REFERENCES inventario_productobase(id) ON DELETE CASCADE
    );


    -- 8. TABLA: ordenes_ordentrabajo
    CREATE TABLE IF NOT EXISTS ordenes_ordentrabajo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        numero_orden VARCHAR(20) NOT NULL UNIQUE,
        estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        kilometraje INTEGER NOT NULL DEFAULT 0,
        diagnostico TEXT NOT NULL DEFAULT '',
        observaciones TEXT NOT NULL DEFAULT '',
        fecha_prometida DATETIME NULL,
        fecha_cierre DATETIME NULL,
        creado_por_id INTEGER NULL,
        mecanico_id INTEGER NULL,
        vehiculo_id INTEGER NOT NULL,
        FOREIGN KEY (creado_por_id) REFERENCES accounts_usuario(id) ON DELETE SET NULL,
        FOREIGN KEY (mecanico_id) REFERENCES accounts_usuario(id) ON DELETE SET NULL,
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos_vehiculo(id) ON DELETE RESTRICT
    );

    CREATE INDEX IF NOT EXISTS idx_orden_numero ON ordenes_ordentrabajo(numero_orden);
    CREATE INDEX IF NOT EXISTS idx_orden_estado ON ordenes_ordentrabajo(estado);
    CREATE INDEX IF NOT EXISTS idx_orden_vehiculo ON ordenes_ordentrabajo(vehiculo_id);


    -- 9. TABLA: ordenes_detalleservicio (Mano de obra)
    CREATE TABLE IF NOT EXISTS ordenes_detalleservicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion VARCHAR(200) NOT NULL,
        cantidad DECIMAL(8, 2) NOT NULL DEFAULT 1.00,
        precio_unitario DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        orden_id INTEGER NOT NULL,
        FOREIGN KEY (orden_id) REFERENCES ordenes_ordentrabajo(id) ON DELETE CASCADE
    );


    -- 10. TABLA: ordenes_detalleproducto (Repuestos / Insumos)
    CREATE TABLE IF NOT EXISTS ordenes_detalleproducto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cantidad INTEGER NOT NULL DEFAULT 1,
        precio_unitario DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
        orden_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        FOREIGN KEY (orden_id) REFERENCES ordenes_ordentrabajo(id) ON DELETE CASCADE,
        FOREIGN KEY (producto_id) REFERENCES inventario_productobase(id) ON DELETE RESTRICT
    );


    -- 11. TABLA: inventario_movimientostock
    CREATE TABLE IF NOT EXISTS inventario_movimientostock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_movimiento VARCHAR(20) NOT NULL,
        cantidad INTEGER NOT NULL,
        stock_resultante INTEGER NOT NULL,
        motivo VARCHAR(200) NOT NULL,
        usuario VARCHAR(150) NOT NULL DEFAULT '',
        precio_unitario DECIMAL(12, 2) NULL,
        fecha_movimiento DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        orden_id INTEGER NULL,
        producto_id INTEGER NOT NULL,
        FOREIGN KEY (orden_id) REFERENCES ordenes_ordentrabajo(id) ON DELETE SET NULL,
        FOREIGN KEY (producto_id) REFERENCES inventario_productobase(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_mov_fecha ON inventario_movimientostock(fecha_movimiento);
    CREATE INDEX IF NOT EXISTS idx_mov_producto ON inventario_movimientostock(producto_id);


    -- 12. TABLA: facturas_factura
    CREATE TABLE IF NOT EXISTS facturas_factura (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        numero_factura VARCHAR(20) NOT NULL UNIQUE,
        fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        subtotal DECIMAL(12, 2) NOT NULL,
        iva_porcentaje DECIMAL(5, 2) NOT NULL DEFAULT 21.00,
        iva_monto DECIMAL(12, 2) NOT NULL,
        total DECIMAL(12, 2) NOT NULL,
        estado_pago VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        notas TEXT NOT NULL DEFAULT '',
        cliente_id INTEGER NOT NULL,
        orden_id INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (cliente_id) REFERENCES clientes_cliente(id) ON DELETE RESTRICT,
        FOREIGN KEY (orden_id) REFERENCES ordenes_ordentrabajo(id) ON DELETE RESTRICT
    );


    -- 13. TABLA: facturas_pago
    CREATE TABLE IF NOT EXISTS facturas_pago (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        monto DECIMAL(12, 2) NOT NULL,
        metodo_pago VARCHAR(30) NOT NULL DEFAULT 'EFECTIVO',
        referencia VARCHAR(100) NOT NULL DEFAULT '',
        fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        usuario VARCHAR(150) NOT NULL DEFAULT '',
        factura_id INTEGER NOT NULL,
        FOREIGN KEY (factura_id) REFERENCES facturas_factura(id) ON DELETE CASCADE
    );


    -- 14. TABLA: reservas_reserva (Citas)
    CREATE TABLE IF NOT EXISTS reservas_reserva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_hora DATETIME NOT NULL,
        servicio_solicitado VARCHAR(200) NOT NULL,
        estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        notas TEXT NOT NULL DEFAULT '',
        cliente_id INTEGER NOT NULL,
        vehiculo_id INTEGER NOT NULL,
        orden_generada_id INTEGER NULL UNIQUE,
        FOREIGN KEY (cliente_id) REFERENCES clientes_cliente(id) ON DELETE RESTRICT,
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos_vehiculo(id) ON DELETE RESTRICT,
        FOREIGN KEY (orden_generada_id) REFERENCES ordenes_ordentrabajo(id) ON DELETE SET NULL
    );


    -- 15. TABLA: mantenimiento_tiposervicio
    CREATE TABLE IF NOT EXISTS mantenimiento_tiposervicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        nombre VARCHAR(100) NOT NULL UNIQUE,
        descripcion TEXT NOT NULL DEFAULT '',
        precio_base DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        intervalo_km INTEGER NULL,
        intervalo_meses INTEGER NULL,
        activo BOOLEAN NOT NULL DEFAULT 1
    );


    -- 16. TABLA: mantenimiento_alertamantenimiento
    CREATE TABLE IF NOT EXISTS mantenimiento_alertamantenimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
        km_estimado INTEGER NULL,
        fecha_estimada DATE NULL,
        notas TEXT NOT NULL DEFAULT '',
        tipo_servicio_id INTEGER NOT NULL,
        vehiculo_id INTEGER NOT NULL,
        FOREIGN KEY (tipo_servicio_id) REFERENCES mantenimiento_tiposervicio(id) ON DELETE CASCADE,
        FOREIGN KEY (vehiculo_id) REFERENCES vehiculos_vehiculo(id) ON DELETE CASCADE
    );


    -- 17. TABLA: core_auditoria
    CREATE TABLE IF NOT EXISTS core_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla VARCHAR(50) NOT NULL,
        registro_id INTEGER NOT NULL,
        accion VARCHAR(20) NOT NULL,
        usuario VARCHAR(150) NOT NULL,
        valores_anteriores TEXT NULL, -- Formato JSON
        valores_nuevos TEXT NULL,      -- Formato JSON
        fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(39) NULL
    );
