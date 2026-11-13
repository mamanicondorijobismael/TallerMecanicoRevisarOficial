# 🧪 Guía Práctica de Verificación y Pruebas — El Taller del Maestro

Esta guía te permite verificar paso a paso en el navegador que todas las funcionalidades, validaciones y reglas de negocio solicitadas se estén cumpliendo correctamente.

---

## 📑 Índice de Pruebas

1. [Prueba 1: Generación Automática del SKU (3 Partes)](#-prueba-1-generación-automática-del-sku-3-partes)
2. [Prueba 2: Clientes Deshabilitados y Desplegables](#-prueba-2-clientes-deshabilitados-y-desplegables)
3. [Prueba 3: Vehículos Deshabilitados y Lista Flotante de OT](#-prueba-3-vehículos-deshabilitados-y-lista-flotante-de-ot)
4. [Prueba 4: Métodos de Pago en Recibos (Solo Efectivo)](#-prueba-4-métodos-de-pago-en-recibos-solo-efectivo)
5. [Prueba 5: Gestión de Usuarios (Sin Modales Raros)](#-prueba-5-gestión-de-usuarios-sin-modales-raros)
6. [Prueba 6: Vista Limpia de Inventario y Categorías de Llantas](#-prueba-6-vista-limpia-de-inventario-y-categorías-de-llantas)
7. [Prueba 7: Órdenes de Trabajo, KM y Kanban](#-prueba-7-órdenes-de-trabajo-km-y-kanban)
8. [Prueba 8: Reportes Simplificados y Repuestos Comprados](#-prueba-8-reportes-simplificados-y-repuestos-comprados)

---

## 🔹 Prueba 1: Generación Automática del SKU (3 Partes en Pantalla y Backend)

> **Regla:** El SKU debe generarse según `[FAMILIA]-[SUBFAMILIA/ESPECIFICACIÓN]-[CORRELATIVO]`.
> **En Pantalla:** A medida que seleccionás la categoría o escribís la marca/medida, el SKU se autocompleta en vivo en el campo y podés presionar el botón *"Autogenerar ahora"* para recalcularlo.

### Caso 1A: Repuesto con marca (En vivo en pantalla)
1. Ingresá a **Inventario** → clic en **"Nuevo Repuesto"** (`/inventario/repuestos/nuevo/`).
   *(Hacé `Ctrl + Shift + R` para cargar el nuevo JavaScript sin caché).*
2. Seleccioná:
   - **Categoría:** `[FRE] Frenos`
   - **Fabricante / Marca:** Escribí `Brembo`
3. **Observá la pantalla en tiempo real:**
   - En el campo **Código SKU**, verás que automáticamente se completa con:
     $$\mathbf{FRE-BREMBO-001}$$
   - Aparece abajo el mensaje verde de confirmación: `✓ SKU sugerido: FRE-BREMBO-001`.
   - Si cambiás la marca a `Bosch`, se actualiza en vivo a `FRE-BOSCH-001`.
   - Si hacés clic en el botón superior **"Autogenerar ahora"**, consulta al servidor el correlativo exacto disponible.
4. Completá Nombre `Pastillas Delanteras`, Costo `150`, Venta `280`, Stock `5` y hacé clic en **"Guardar Repuesto"**.
5. **Resultado esperado:** El producto queda guardado con su código SKU: `FRE-BREMBO-001`.

### Caso 1B: Repuesto genérico (sin marca)
1. Creá un nuevo repuesto con Categoría `[FIL] Filtros` y dejá el Fabricante / Marca vacío.
2. **Observá la pantalla:** Se autocompleta como:
   $$\mathbf{FIL-GEN-001}$$
3. Guardá y confirmá en el catálogo.

### Caso 1C: Neumático (En vivo en pantalla)
1. Ingresá a **"Nuevo Neumático"** (`/inventario/neumaticos/nuevo/`).
2. Completá las medidas:
   - **Ancho:** `205`, **Perfil:** `55`, **Rin:** `16`.
   - **Tipo de Neumático:** Seleccioná `AT (All Terrain)`.
3. **Observá el campo Código SKU:**
   - Se autocompleta inmediatamente en pantalla como:
     $$\mathbf{NEU-20555R16-AT-001}$$
4. Guardá y confirmá en el catálogo.

### Caso 1D: Llanta (En vivo en pantalla)
1. Ingresá a **"Nueva Llanta"** (`/inventario/llantas/nueva/`).
2. Completá:
   - **Rin:** `17`, **Material / Subfamilia:** `Aluminio / Aleación` (`ALU`).
   - **Apernadura:** `5x114.3`.
3. **Observá el campo Código SKU:**
   - Se autocompleta en pantalla como:
     $$\mathbf{LLA-17IN-ALU-5X1143-001}$$
4. Guardá y confirmá en el catálogo.
4. **Resultado esperado:** El SKU generado debe ser:
   $$\mathbf{LLA-17IN-ALU-5X1143-001}$$

---

## 🔹 Prueba 2: Clientes Deshabilitados y Desplegables

> **Regla:** Si un cliente está deshabilitado, no puede aparecer en el desplegable de asignación para crear nuevos autos.

1. Ingresá a **Clientes** (`/clientes/`).
2. Creá un cliente de prueba llamado `Cliente Inactivo Test` con DNI `99999999`.
3. Ingresá a su ficha o editalo:
   - En el formulario de edición, desmarcá el switch **"Cliente Habilitado"** (o eliminalo si ya tiene historial para que quede desactivado).
   - Guardá los cambios.
4. Recargá la lista de clientes (`/clientes/`).
   - **Verificación 2.1:** Comprobá que `Cliente Inactivo Test` ya **NO aparece** en la lista de clientes activos (no se reactiva solo).
5. Ahora andá a **Vehículos** → clic en **"Nuevo Vehículo"** (`/vehiculos/nuevo/`).
6. Abrí la lista desplegable de **Propietario**:
   - **Verificación 2.2:** Comprobá que `Cliente Inactivo Test` **NO aparece** entre las opciones seleccionables.

---

## 🔹 Prueba 3: Vehículos Deshabilitados y Lista Flotante de OT

> **Regla:** Si un auto está deshabilitado (o su dueño está inactivo), no puede crearse una orden de trabajo ni aparecer en la lista desplegable ni en el buscador flotante AJAX.

1. Creá un vehículo de prueba con placa `TEST-001` asignado a un cliente activo.
2. Editá el vehículo `TEST-001` (`/vehiculos/<id>/editar/`):
   - Desmarcá el switch **"Vehículo Habilitado"** y guardá.
3. Ahora andá a **Órdenes de Trabajo** → clic en **"Nueva Orden"** (`/ordenes/nuevo/`).
4. **Verificación en el desplegable `<select>`:**
   - Abrí el campo **"Vehículo / Placa"**.
   - Comprobá que `TEST-001` **NO aparece**.
5. **Verificación en el buscador flotante AJAX:**
   - Escribí `TEST` en el campo de búsqueda rápida *"Buscar por placa, modelo o cliente..."*.
   - Comprobá que el auto deshabilitado **NO es devuelto ni filtrado**.
6. **Verificación de URL directa:**
   - Intentá ingresar manualmente a `/ordenes/nuevo/?vehiculo_id=<ID_DEL_AUTO_DESHABILITADO>`.
   - Comprobá que el sistema muestra una advertencia bloqueando la asignación: *"El vehículo indicado no existe o se encuentra deshabilitado"*.

---

## 🔹 Prueba 4: Métodos de Pago en Recibos (Solo Efectivo)

> **Regla:** Quitar QR y Tarjeta; los recibos y pagos deben ser simples y operar exclusivamente en Efectivo.

1. Ingresá a una Orden de Trabajo que esté en estado **COMPLETADA** (o completá una en `/ordenes/`).
2. Hacé clic en el botón dorado **"Generar Recibo"**.
3. Se abrirá la ficha del recibo (`/recibos/<id>/`).
4. Hacé clic en **"Registrar Pago / Abono"**:
   - **Verificación 4.1:** En el formulario modal de cobro, el campo **Método de Pago** debe decir fijamente **"Efectivo"** (no hay selectores de QR ni Tarjetas).
5. Ingresá el monto y confirmá el pago.
6. Hacé clic en **"Imprimir / PDF"**:
   - **Verificación 4.2:** El recibo impreso debe mostrar un diseño limpio, minimalista, con desglose de ítems, el cobro asentado como **Efectivo** y casillas de firma.

---

## 🔹 Prueba 5: Gestión de Usuarios (Sin Modales Raros)

> **Regla:** El botón "Nuevo Usuario" debe dirigir a una página completa dedicada, sin modales superpuestos.

1. Con usuario Administrador/Dueño, hacé clic en el menú superior **Admin** → **Personal & Usuarios** (`/usuarios/`).
2. Hacé clic en el botón dorado **"Nuevo Usuario"**:
   - **Verificación 5.1:** La navegación debe llevarte directamente a la URL `/usuarios/nuevo/`.
   - **Verificación 5.2:** La pantalla debe ser un formulario estructurado full-page (`usuario_form.html`) con campos para Nombre, Username, Email, Rol, Contraseña y Foto, con sus botones Cancelar y Guardar.
3. Al guardar un usuario nuevo, debe redirigirte al listado con mensaje de confirmación verde.

---

## 🔹 Prueba 6: Vista Limpia de Inventario y Categorías de Llantas

> **Regla:** Quitar banner gigante rojo y tarjeta Stock Crítico aislada; mantener 4 KPIs limpios; incluir categorías de llantas.

1. Ingresá a **Inventario** (`/inventario/`):
   - **Verificación 6.1 (Importante: presionar `Ctrl + Shift + R` para limpiar caché del navegador):**
     - La parte superior debe mostrar únicamente 4 tarjetas KPI:
       1. **Total Catálogo**
       2. **Repuestos**
       3. **Neumáticos**
       4. **Llantas**
     - **NO debe existir** ningún banner rojo invasivo ni tarjeta gigante de stock crítico arriba.
     - Cada producto que esté en stock crítico tiene su indicador discreto dentro de su propia tarjeta.
2. Ingresá a **Categorías** (`/inventario/categorias/`):
   - **Verificación 6.2:** La pantalla debe tener **3 columnas organizadas**:
     1. Categorías de Repuestos (Filtros, Frenos, Lubricantes, etc.)
     2. Categorías de Neumáticos (Turismo, 4x4, etc.)
     3. Categorías de Llantas (Aleación, Acero)

---

## 🔹 Prueba 7: Órdenes de Trabajo, KM y Kanban

> **Regla:** Formulario full-page, autocompletado de KM con toggle de edición, y Kanban operativo.

1. Ingresá a **"Nueva Orden"** (`/ordenes/nuevo/`).
2. Seleccioná un vehículo del desplegable:
   - **Verificación 7.1:** El campo **Kilometraje** se completa automáticamente con el último KM del auto y queda en modo solo lectura (fondo gris claro).
   - Hacé clic en **"¿Actualizar KM?"**: el campo debe desbloquearse para permitir ingresar un nuevo valor.
3. Guardá la orden e ingresá a su detalle (`/ordenes/<id>/`):
   - **Mano de obra simple:** En "Agregar Servicio", el campo solicita directamente **Monto (Bs)** (sin multiplicar por horas).
   - **Repuestos externos:** En "Repuesto Externo", se solicita descripción, cantidad y precio sin pedir proveedor de forma obligatoria.
4. Ingresá al **Tablero Kanban** (`/ordenes/kanban/`):
   - **Verificación 7.2:** Se visualizan las 5 columnas (`Pendiente`, `En Proceso`, `Espera Repuestos`, `Completada`, `Entregada`).
   - Las tarjetas tienen indicadores de plazo de entrega (verde, amarillo si faltan <6h, rojo si está vencida).

---

## 🔹 Prueba 8: Reportes Simplificados y Repuestos Comprados

> **Regla:** Informes limpios con balance general, recaudaciones y compras de repuestos registradas con trazabilidad de usuario.

1. Ingresá a **Reportes** → **Cierre Diario** (`/reportes/diario/`).
2. **Verificación 8.1:** La cabecera muestra 4 KPIs financieros simples:
   - Recibos Emitidos (Bs)
   - Cobros Recaudados (Bs)
   - **Repuestos Comprados (Bs)**
   - Balance Neto del Día (Bs)
3. **Verificación 8.2 (Trazabilidad):**
   - En la tabla de **"Repuestos y Mercadería Comprada / Ingresada"**, cada movimiento muestra qué producto ingresó, cantidad, costo unitario, total y la insignia azul del **Usuario responsable** que registró el ingreso.
4. Hacé clic en **"PDF"** o **"Imprimir"**: comprobá que genera un documento limpio y formateado listo para archivar.

---

## 💡 Comandos de Soporte

Si necesitás re-cargar todos los datos de demostración limpios en cualquier momento:
```powershell
entorno\Scripts\python.exe seed_datos.py
```
*(o hacé doble clic sobre el archivo `ejecutar_seed.bat` en la raíz del proyecto).*

Para verificar que Django no tiene advertencias ni errores:
```powershell
entorno\Scripts\python.exe manage.py check
```
*(debe indicar: `System check identified no issues (0 silenced)`).*

