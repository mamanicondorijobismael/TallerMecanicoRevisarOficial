"""
seed_datos.py — Datos de demostración completos para El Taller del Maestro
Ejecutar: entorno\Scripts\python.exe seed_datos.py
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta, datetime

# ── Setup Django ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

# ── Imports de modelos ────────────────────────────────────────────────────────
from django.utils import timezone
from apps.accounts.models import Rol, Usuario
from apps.clientes.models import Cliente
from apps.vehiculos.models import Vehiculo
from apps.inventario.models import (
    CategoriaProducto, ProductoBase, RepuestoGenerico,
    Neumatico, Llanta, MovimientoStock
)
from apps.ordenes.models import OrdenTrabajo, DetalleServicio, DetalleProducto, RepuestoExterno
from apps.recibos.models import Recibo, Pago

HOY = date.today()


def log(msg): print(f"  ✓ {msg}")
def seccion(msg): print(f"\n{'─'*60}\n  {msg}\n{'─'*60}")


# ══════════════════════════════════════════════════════════════════════════════
# 1. CATEGORÍAS DE INVENTARIO
# ══════════════════════════════════════════════════════════════════════════════
seccion("1. Categorías de inventario")

cats_repuesto = [
    {'nombre': 'Filtros',          'codigo_prefijo': 'FIL', 'tipo': 'REPUESTO'},
    {'nombre': 'Frenos',           'codigo_prefijo': 'FRE', 'tipo': 'REPUESTO'},
    {'nombre': 'Lubricantes',      'codigo_prefijo': 'LUB', 'tipo': 'REPUESTO'},
    {'nombre': 'Motor',            'codigo_prefijo': 'MOT', 'tipo': 'REPUESTO'},
    {'nombre': 'Suspensión',       'codigo_prefijo': 'SUS', 'tipo': 'REPUESTO'},
    {'nombre': 'Eléctrico',        'codigo_prefijo': 'ELE', 'tipo': 'REPUESTO'},
    {'nombre': 'Transmisión',      'codigo_prefijo': 'TRA', 'tipo': 'REPUESTO'},
    {'nombre': 'Refrigeración',    'codigo_prefijo': 'REF', 'tipo': 'REPUESTO'},
]
cats_neu = [
    {'nombre': 'Neumáticos Turismo',  'codigo_prefijo': 'NEU', 'tipo': 'NEUMATICO'},
    {'nombre': 'Neumáticos 4x4',      'codigo_prefijo': 'N4X', 'tipo': 'NEUMATICO'},
]
cats_lla = [
    {'nombre': 'Llantas de Aleación', 'codigo_prefijo': 'LLA', 'tipo': 'LLANTA'},
    {'nombre': 'Llantas de Acero',    'codigo_prefijo': 'LAC', 'tipo': 'LLANTA'},
]

cat_obj = {}
for c in cats_repuesto + cats_neu + cats_lla:
    obj, created = CategoriaProducto.objects.get_or_create(
        nombre=c['nombre'],
        defaults={'codigo_prefijo': c['codigo_prefijo'], 'tipo': c['tipo']}
    )
    cat_obj[c['nombre']] = obj
    if created: log(f"Categoría: {c['nombre']}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. INVENTARIO — REPUESTOS
# ══════════════════════════════════════════════════════════════════════════════
seccion("2. Repuestos")

repuestos_data = [
    # (nombre, cat, costo, venta, stock, min_stock, marca, parte, compatible)
    ('Filtro de Aceite Toyota',         'Filtros',    35, 70,   12, 5, 'Genuine',   'TO-15600-87703', 'Toyota Corolla, Yaris 2015-2024'),
    ('Filtro de Aire Universal',        'Filtros',    45, 85,    8, 4, 'Mann',       'C-2652',         'Toyota, Nissan, Honda universal'),
    ('Filtro de Combustible Nissan',    'Filtros',    55, 100,   6, 3, 'Genuine',   'NI-16400-BN300', 'Nissan Sentra, Tiida 2008-2020'),
    ('Filtro de Polen Honda',           'Filtros',    40, 75,    4, 3, 'Bosch',      'BH-1457429191',  'Honda Civic, CR-V 2012-2022'),
    ('Pastillas de Freno Delanteras',   'Frenos',    120, 230,   6, 3, 'Brembo',    'P-23052',        'Toyota Corolla 2010-2022, Yaris 2014-2022'),
    ('Pastillas de Freno Traseras',     'Frenos',     90, 170,   4, 2, 'Brembo',    'P-50064',        'Toyota Corolla 2010-2022'),
    ('Disco de Freno Delantero',        'Frenos',    180, 340,   4, 2, 'DBA',        'DBA42720S',      'Toyota Corolla 2014-2022'),
    ('Líquido de Frenos DOT4',          'Frenos',     25, 55,   15, 5, 'Castrol',   'CAS-DOT4-500',   'Universal'),
    ('Aceite 10W-40 Semisintético 1L',  'Lubricantes',32, 65,   30, 8, 'Castrol',   'CAE-10W40-1L',   'Universal gasolina'),
    ('Aceite 5W-30 Full Sintético 1L',  'Lubricantes',48, 90,   20, 6, 'Mobil1',    'MOB-5W30-1L',    'Motores modernos turbo'),
    ('Aceite de Transmisión ATF',       'Lubricantes',55, 100,   8, 4, 'Castrol',   'ATF-DEXIII',     'Cajas automáticas'),
    ('Aceite de Dirección Hidráulica',  'Lubricantes',30, 60,   10, 4, 'Total',     'TOT-PSF',        'Universal'),
    ('Bujías NGK (juego x4)',           'Motor',      80, 150,   8, 3, 'NGK',        'BKR6E-11',       'Toyota, Nissan 4 cilindros'),
    ('Banda de Distribución',           'Motor',     150, 280,   4, 2, 'Gates',     'T218',           'Toyota 4A-FE, 5A-FE'),
    ('Bomba de Agua Toyota',            'Motor',     220, 420,   3, 2, 'GMB',        'GWT-105A',       'Toyota Corolla 2000-2010'),
    ('Kit Correa Accesorios',           'Motor',     185, 350,   3, 2, 'Gates',     'K025695XS',      'Toyota Corolla 2014-2022'),
    ('Amortiguador Delantero D.',       'Suspensión',280, 520,   4, 2, 'Monroe',    'MT-37176',       'Toyota Corolla 2007-2013'),
    ('Amortiguador Trasero D.',         'Suspensión',240, 460,   4, 2, 'Monroe',    'MT-71534',       'Toyota Corolla 2007-2013'),
    ('Terminal de Dirección',           'Suspensión', 85, 160,   6, 3, 'Moog',      'TO-ES-2769',     'Toyota Corolla, Yaris'),
    ('Rotula Inferior',                 'Suspensión',120, 230,   4, 2, 'Moog',      'TO-BJ-9816',     'Toyota Corolla 2001-2013'),
    ('Batería 12V 60Ah',               'Eléctrico', 350, 650,   5, 2, 'Bosch',     'BAT-S4-005',     'Universal autos medianos'),
    ('Alternador Remanufacturado',      'Eléctrico', 450, 850,   2, 1, 'Remy',      'ALT-91337',      'Toyota Corolla 2000-2008'),
    ('Sensor Oxígeno Upstream',        'Eléctrico', 180, 340,   3, 1, 'Denso',     'DEN-234-4209',   'Toyota/Lexus 1996-2004'),
    ('Bomba de Combustible',           'Eléctrico', 290, 550,   2, 1, 'Delphi',    'FE0115',         'Toyota Corolla 2003-2013'),
    ('Kit Embrague Completo',          'Transmisión',580, 1100,  2, 1, 'LUK',       'LUK-620-3072',   'Toyota Corolla 1.8 2000-2007'),
    ('Termostato Motor',               'Refrigeración',45, 90,   8, 3, 'Stant',    'STA-14878',      'Toyota 1ZZ, 2ZZ 2000-2008'),
    ('Radiador Completo Aluminio',     'Refrigeración',480, 900,  2, 1, 'Koyo',    'PL010890',       'Toyota Corolla 2001-2008'),
    ('Manguera Superior Radiador',     'Refrigeración',35, 70,   6, 3, 'Gates',    'GAT-21505',      'Toyota Corolla 2001-2008'),
]

prod_obj = {}
for nombre, cat_nombre, costo, venta, stock, min_stock, marca, parte, compat in repuestos_data:
    if ProductoBase.objects.filter(nombre=nombre).exists():
        pb = ProductoBase.objects.get(nombre=nombre)
        prod_obj[nombre] = pb
        continue
    import re
    marca_sub = re.sub(r'[^A-Z0-9]', '', marca.upper())[:8] if marca else 'GEN'
    prefijo = cat_obj[cat_nombre].codigo_prefijo.strip().upper()
    base_pat = f"{prefijo}-{marca_sub}-"
    last_cnt = ProductoBase.objects.filter(codigo_sku__startswith=base_pat).count()
    sku_val = f"{base_pat}{str(last_cnt + 1).zfill(3)}"

    pb = ProductoBase(
        categoria=cat_obj[cat_nombre],
        codigo_sku=sku_val,
        nombre=nombre,
        descripcion=f'{nombre} — Repuesto de calidad certificada',
        precio_costo=Decimal(str(costo)),
        precio_venta=Decimal(str(venta)),
        stock_actual=stock,
        stock_minimo=min_stock,
        tipo_producto='REPUESTO',
        aplicacion=compat,
    )
    pb.save()
    RepuestoGenerico.objects.create(
        producto=pb,
        marca_repuesto=marca,
        numero_parte=parte,
        compatible_con=compat,
    )
    MovimientoStock.objects.create(
        producto=pb,
        tipo_movimiento='ENTRADA',
        cantidad=stock,
        stock_resultante=stock,
        motivo='Stock inicial de apertura',
        precio_unitario=Decimal(str(costo)),
        usuario='admin',
    )
    prod_obj[nombre] = pb
    log(f"Repuesto: {pb.codigo_sku} — {nombre}")

# ══════════════════════════════════════════════════════════════════════════════
# 3. INVENTARIO — NEUMÁTICOS
# ══════════════════════════════════════════════════════════════════════════════
seccion("3. Neumáticos")

neumaticos_data = [
    # (nombre, cat, costo, venta, stock, min, marca, modelo, ancho, perfil, diametro, tipo)
    ('Bridgestone Turanza 205/55R16',  'Neumáticos Turismo',  280, 520, 8, 4, 'Bridgestone', 'Turanza T005',   205, 55, 16, 'VERANO'),
    ('Michelin Primacy 195/65R15',     'Neumáticos Turismo',  250, 470, 6, 3, 'Michelin',    'Primacy 4',      195, 65, 15, 'ALL_SEASON'),
    ('Pirelli Cinturato 205/55R16',    'Neumáticos Turismo',  260, 490, 4, 2, 'Pirelli',     'Cinturato P7',   205, 55, 16, 'VERANO'),
    ('Goodyear EfficientGrip 185/65R15','Neumáticos Turismo', 220, 420, 6, 3, 'Goodyear',    'EfficientGrip',  185, 65, 15, 'ALL_SEASON'),
    ('Yokohama Geolandar 265/70R17',   'Neumáticos 4x4',      380, 710, 4, 2, 'Yokohama',    'Geolandar H/T',  265, 70, 17, 'HT'),
    ('BF Goodrich All Terrain 265/65R17','Neumáticos 4x4',    420, 780, 4, 2, 'BF Goodrich', 'All-Terrain KO2',265, 65, 17, 'AT'),
    ('Maxxis Bravo 245/70R16',         'Neumáticos 4x4',      310, 580, 4, 2, 'Maxxis',      'Bravo AT-771',   245, 70, 16, 'AT'),
]

for nombre, cat_nombre, costo, venta, stock, min_stock, marca, modelo, ancho, perfil, diam, tipo in neumaticos_data:
    if ProductoBase.objects.filter(nombre=nombre).exists():
        prod_obj[nombre] = ProductoBase.objects.get(nombre=nombre)
        continue
    prefijo = cat_obj[cat_nombre].codigo_prefijo.strip().upper() if cat_obj.get(cat_nombre) else 'NEU'
    sub_neu = f"{ancho}{perfil}R{diam}-{tipo}"
    base_pat = f"{prefijo}-{sub_neu}-"
    last_cnt = ProductoBase.objects.filter(codigo_sku__startswith=base_pat).count()
    sku_val = f"{base_pat}{str(last_cnt + 1).zfill(3)}"

    pb = ProductoBase(
        categoria=cat_obj[cat_nombre],
        codigo_sku=sku_val,
        nombre=nombre,
        descripcion=f'{marca} {modelo} — Neumático de alto rendimiento',
        precio_costo=Decimal(str(costo)),
        precio_venta=Decimal(str(venta)),
        stock_actual=stock,
        stock_minimo=min_stock,
        tipo_producto='NEUMATICO',
    )
    pb.save()
    Neumatico.objects.create(
        producto=pb,
        marca_neumatico=marca,
        modelo_neumatico=modelo,
        ancho=ancho, perfil=perfil, diametro=diam,
        tipo=tipo,
        estado='NUEVO',
        indice_carga='91', indice_velocidad='V',
    )
    MovimientoStock.objects.create(
        producto=pb, tipo_movimiento='ENTRADA',
        cantidad=stock, stock_resultante=stock,
        motivo='Stock inicial', precio_unitario=Decimal(str(costo)), usuario='admin',
    )
    prod_obj[nombre] = pb
    log(f"Neumático: {pb.codigo_sku} — {nombre}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. INVENTARIO — LLANTAS
# ══════════════════════════════════════════════════════════════════════════════
seccion("4. Llantas / Rines")

llantas_data = [
    # (nombre, cat, costo, venta, stock, min, marca, subfam, rin, ancho, apernadura, offset, color)
    ('Llanta Aleación 15" 4x100',    'Llantas de Aleación', 320, 600, 4, 2, 'OZ Racing',  'ALU', 15, Decimal('6.5'), '4x100',   40, 'Plata'),
    ('Llanta Aleación 16" 5x114.3',  'Llantas de Aleación', 380, 720, 4, 2, 'BBS',        'ALU', 16, Decimal('7.0'), '5x114.3', 45, 'Negro Mate'),
    ('Llanta Aleación 17" 5x114.3',  'Llantas de Aleación', 480, 900, 4, 2, 'Enkei',      'ALU', 17, Decimal('7.5'), '5x114.3', 48, 'Plata'),
    ('Llanta Acero 15" 5x100',       'Llantas de Acero',    180, 340, 4, 2, 'Genérica',   'ACE', 15, Decimal('6.0'), '5x100',   35, 'Blanco'),
    ('Llanta Acero 14" 4x100',       'Llantas de Acero',    150, 290, 4, 2, 'Genérica',   'ACE', 14, Decimal('5.5'), '4x100',   35, 'Blanco'),
]

for nombre, cat_nombre, costo, venta, stock, min_stock, marca, subfam, rin, ancho_p, apert, offset, color in llantas_data:
    if ProductoBase.objects.filter(nombre=nombre).exists():
        prod_obj[nombre] = ProductoBase.objects.get(nombre=nombre)
        continue
    prefijo = cat_obj[cat_nombre].codigo_prefijo.strip().upper() if cat_obj.get(cat_nombre) else 'LLA'
    import re
    ap_clean = re.sub(r'[^A-Z0-9]', '', apert.upper()) or 'STD'
    sub_lla = f"{rin}IN-{subfam}-{ap_clean}"
    base_pat = f"{prefijo}-{sub_lla}-"
    last_cnt = ProductoBase.objects.filter(codigo_sku__startswith=base_pat).count()
    sku_val = f"{base_pat}{str(last_cnt + 1).zfill(3)}"

    pb = ProductoBase(
        categoria=cat_obj[cat_nombre],
        codigo_sku=sku_val,
        nombre=nombre,
        descripcion=f'{marca} Rin {rin}" {apert} — {color}',
        precio_costo=Decimal(str(costo)),
        precio_venta=Decimal(str(venta)),
        stock_actual=stock,
        stock_minimo=min_stock,
        tipo_producto='LLANTA',
    )
    pb.save()
    Llanta.objects.create(
        producto=pb,
        marca_llanta=marca,
        subfamilia=subfam,
        rin=rin,
        ancho_pulgadas=ancho_p,
        apernadura=apert,
        offset_et=offset,
        color=color,
    )
    MovimientoStock.objects.create(
        producto=pb, tipo_movimiento='ENTRADA',
        cantidad=stock, stock_resultante=stock,
        motivo='Stock inicial', precio_unitario=Decimal(str(costo)), usuario='admin',
    )
    prod_obj[nombre] = pb
    log(f"Llanta: {pb.codigo_sku} — {nombre}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. CLIENTES
# ══════════════════════════════════════════════════════════════════════════════
seccion("5. Clientes")

clientes_data = [
    ('Carlos Alberto Mendoza',    '12345678',   '+591 70012345', 'cmendoza@gmail.com',    'Av. 6 de Agosto 1234, La Paz'),
    ('María Elena Quispe',        '23456789',   '+591 71123456', 'mquispe@hotmail.com',   'Calle Mercado 567, Cochabamba'),
    ('Roberto Luis Flores',       '34567890',   '+591 72234567', 'rflores@empresa.com',   'Av. Blanco Galindo Km 5, Cochabamba'),
    ('Ana Sofía Torrico',         '45678901',   '+591 73345678', 'atorrico@yahoo.com',    'Calle Sucre 890, Oruro'),
    ('Empresa Logística Andina',  '78901234-5', '+591 74456789', 'logistica@andina.bo',   'Zona Sur, Calle 21 de Calacoto, La Paz'),
    ('Juan Pablo Mamani',         '56789012',   '+591 75567890', 'jpmamani@gmail.com',    'Villa Adela, La Paz'),
    ('Lucía Fernández Vda. Roca', '67890123',   '+591 76678901', 'lfernandez@outlook.com','Sopocachi, La Paz'),
    ('Distribuidora Norte S.R.L.','89012345-6', '+591 77789012', 'norte@distribuidora.bo','El Alto, Zona 16 de Julio'),
    ('Diego Alejandro Soria',     '90123456',   '+591 78890123', 'dsoria@gmail.com',      'Quillacollo, Cochabamba'),
    ('Patricia Velarde Chávez',   '01234567',   '+591 79901234', 'pvelarde@gmail.com',    'Av. Circunvalación 456, Santa Cruz'),
]

cli_obj = {}
for nombre, doc, tel, email, dir_ in clientes_data:
    obj, created = Cliente.objects.get_or_create(
        documento=doc,
        defaults={'nombre_razon_social': nombre, 'telefono': tel, 'email': email, 'direccion': dir_}
    )
    cli_obj[nombre] = obj
    if created: log(f"Cliente: {nombre}")

# ══════════════════════════════════════════════════════════════════════════════
# 6. VEHÍCULOS
# ══════════════════════════════════════════════════════════════════════════════
seccion("6. Vehículos")

vehiculos_data = [
    # (cliente, placa, marca, modelo, anio, vin, color, km)
    ('Carlos Alberto Mendoza',    '1234-ABC', 'Toyota',    'Corolla',       2018, 'JT2AE09W2N3056781', 'PLATA',    68000),
    ('Carlos Alberto Mendoza',    '5678-DEF', 'Toyota',    'Yaris',         2021, 'JTDBT923291234567', 'BLANCO',   22000),
    ('María Elena Quispe',        '9012-GHI', 'Nissan',    'Sentra',        2019, '3N1AB7AP5KL234567', 'NEGRO',    45000),
    ('Roberto Luis Flores',       '3456-JKL', 'Honda',     'CR-V',          2020, '2HKRW2H5XLH123456', 'GRIS',    38500),
    ('Roberto Luis Flores',       '7890-MNO', 'Toyota',    'Hilux',         2017, 'MR0EX32G9H8012345', 'BLANCO',  115000),
    ('Ana Sofía Torrico',         '2345-PQR', 'Hyundai',   'Tucson',        2022, 'KM8J3CA45NU123456', 'ROJO',    15200),
    ('Empresa Logística Andina',  '6789-STU', 'Toyota',    'Land Cruiser',  2016, 'JTEBU5JR7G5234567', 'NEGRO',   180000),
    ('Empresa Logística Andina',  '0123-VWX', 'Mitsubishi','L200',          2019, 'MMBJNKB40KD012345', 'BLANCO',  95000),
    ('Juan Pablo Mamani',         '4567-YZA', 'Suzuki',    'Swift',         2020, 'TSMEYA41S00123456', 'AZUL',    28000),
    ('Lucía Fernández Vda. Roca', '8901-BCD', 'Mazda',     'CX-5',          2021, 'JM3KFBEM1M0123456', 'GRIS',   30000),
    ('Distribuidora Norte S.R.L.','2345-EFG', 'Isuzu',     'D-Max',         2018, 'JACCS58R2J7012345', 'BLANCO',  142000),
    ('Diego Alejandro Soria',     '6789-HIJ', 'Volkswagen','Gol',           2017, '9BWZZZ377HT012345', 'ROJO',    76000),
    ('Patricia Velarde Chávez',   '0123-KLM', 'Kia',       'Sportage',      2023, 'KNDPM3AC5P7012345', 'NEGRO',    8000),
]

veh_obj = {}
for cli_nombre, placa, marca, modelo, anio, vin, color, km in vehiculos_data:
    obj, created = Vehiculo.objects.get_or_create(
        placa=placa,
        defaults={
            'cliente': cli_obj[cli_nombre],
            'marca': marca, 'modelo': modelo, 'anio': anio,
            'vin': vin, 'color': color, 'kilometraje_actual': km,
        }
    )
    veh_obj[placa] = obj
    if created: log(f"Vehículo: {marca} {modelo} [{placa}] — {cli_nombre}")

# ══════════════════════════════════════════════════════════════════════════════
# 7. USUARIOS (mecánicos para asignar órdenes)
# ══════════════════════════════════════════════════════════════════════════════
seccion("7. Verificando usuarios del taller")

admin_u = Usuario.objects.filter(username='Job').first()
mec1 = Usuario.objects.filter(username='mecanico1').first()
mec2 = Usuario.objects.filter(username='mecanico2').first()
sup_u = Usuario.objects.filter(username='supervisor').first()

if not admin_u:
    print("  ⚠ No se encontró usuario 'admin'. Ejecuta primero el sistema para crear usuarios base.")
    sys.exit(1)

log(f"Admin: {admin_u.nombre_completo}")
if mec1: log(f"Mecánico 1: {mec1.nombre_completo}")
if mec2: log(f"Mecánico 2: {mec2.nombre_completo}")


# ══════════════════════════════════════════════════════════════════════════════
# 8. ÓRDENES DE TRABAJO — HISTORIAL COMPLETO
# ══════════════════════════════════════════════════════════════════════════════
seccion("8. Historial de Órdenes de Trabajo")

# Helper para crear órdenes con fecha retroactiva
def crear_orden(placa, mecanico, creado_por, estado, diagnostico, observaciones,
                km, dias_atras, servicios, productos_inv, repuestos_ext, fecha_prometida_dias=2):

    veh = veh_obj.get(placa)
    if not veh:
        print(f"  ⚠ Vehículo {placa} no encontrado")
        return None

    fecha_base = timezone.now() - timedelta(days=dias_atras)

    orden = OrdenTrabajo(
        vehiculo=veh,
        mecanico=mecanico,
        creado_por=creado_por,
        estado=estado,
        kilometraje=km,
        diagnostico=diagnostico,
        observaciones=observaciones,
        fecha_prometida=fecha_base + timedelta(days=fecha_prometida_dias),
    )
    if estado in ['COMPLETADA', 'COBRADA']:
        orden.fecha_cierre = fecha_base + timedelta(days=1)
    orden.save()
    # Forzar fecha de creación retroactiva
    OrdenTrabajo.objects.filter(pk=orden.pk).update(fecha_creacion=fecha_base)

    # Detalles de servicios (mano de obra)
    for desc, cant, precio in servicios:
        DetalleServicio.objects.create(
            orden=orden, descripcion=desc,
            cantidad=Decimal(str(cant)), precio_unitario=Decimal(str(precio))
        )

    # Productos del inventario
    for nombre_prod, cant in productos_inv:
        pb = prod_obj.get(nombre_prod)
        if pb:
            DetalleProducto.objects.create(
                orden=orden, producto=pb,
                cantidad=cant, precio_unitario=pb.precio_venta
            )
            # Descontar stock
            pb.stock_actual = max(0, pb.stock_actual - cant)
            pb.save(update_fields=['stock_actual'])
            MovimientoStock.objects.create(
                producto=pb, tipo_movimiento='SALIDA',
                cantidad=-cant, stock_resultante=pb.stock_actual,
                motivo=f'Uso en OT #{orden.numero_orden}',
                orden=orden, precio_unitario=pb.precio_venta,
                usuario=mecanico.nombre_completo if mecanico else 'Sistema',
            )

    # Repuestos externos
    for desc, prov, cant, precio in repuestos_ext:
        RepuestoExterno.objects.create(
            orden=orden, descripcion=desc,
            proveedor=prov, cantidad=cant,
            precio_unitario=Decimal(str(precio))
        )

    return orden


def cobrar_orden(orden, usuario_cobro):
    """Genera recibo y pago completo para una orden cobrada."""
    if hasattr(orden, 'recibo') and orden.recibo:
        return orden.recibo
    recibo = Recibo.objects.create(
        orden=orden,
        cliente=orden.vehiculo.cliente,
        subtotal=orden.subtotal,
        iva_porcentaje=Decimal('0'),
        iva_monto=Decimal('0'),
        total=orden.total,
    )
    Pago.objects.create(
        recibo=recibo,
        monto=recibo.total,
        metodo_pago='EFECTIVO',
        usuario=usuario_cobro.nombre_completo,
    )
    recibo.estado_pago = 'PAGADA'
    recibo.save(update_fields=['estado_pago'])
    return recibo


# ── LOTE 1: Órdenes COBRADAS (historial de hace 3 meses) ─────────────────────
ordenes_cobradas = [
    {
        'placa': '1234-ABC', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 65000, 'dias_atras': 85,
        'diagnostico': 'Mantenimiento preventivo 65.000 km. Cambio de aceite y filtros programado.',
        'observaciones': 'Cliente solicita revisión general de frenos también.',
        'servicios': [
            ('Cambio de aceite 10W-40 (incluye filtro)', 1, 80),
            ('Revisión y limpieza de frenos', 1, 60),
            ('Rotación de neumáticos', 1, 40),
        ],
        'productos_inv': [
            ('Aceite 10W-40 Semisintético 1L', 4),
            ('Filtro de Aceite Toyota', 1),
            ('Filtro de Aire Universal', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '9012-GHI', 'mecanico': mec2, 'creado_por': sup_u or admin_u,
        'estado': 'COBRADA', 'km': 43500, 'dias_atras': 72,
        'diagnostico': 'Pastillas de freno delanteras con desgaste crítico. Discos con leve rajadura.',
        'observaciones': 'Se reemplazaron pastillas y discos. Frenos traseros en buen estado.',
        'servicios': [
            ('Cambio pastillas y discos delanteros', 1, 150),
            ('Purga y recambio líquido de frenos', 1, 55),
        ],
        'productos_inv': [
            ('Pastillas de Freno Delanteras', 1),
            ('Disco de Freno Delantero', 2),
            ('Líquido de Frenos DOT4', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '7890-MNO', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 112000, 'dias_atras': 60,
        'diagnostico': 'Correa de distribución con micro-fisuras visibles. Cambio urgente recomendado.',
        'observaciones': 'Se reemplazó banda de distribución y se revisó bomba de agua. Se recomendó cambio de bomba preventivo.',
        'servicios': [
            ('Cambio de banda de distribución (incluye tensores)', 1, 220),
            ('Revisión y ajuste de válvulas', 1, 90),
        ],
        'productos_inv': [
            ('Banda de Distribución', 1),
        ],
        'repuestos_ext': [
            ('Kit tensores y polea banda distribución', 'Autoparts Central', 1, 180),
        ],
    },
    {
        'placa': '3456-JKL', 'mecanico': mec2, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 37000, 'dias_atras': 50,
        'diagnostico': 'Mantenimiento 37.000 km. Cliente refiere consumo excesivo de aceite.',
        'observaciones': 'Sin fuga visible. Posible desgaste de sellos. Se recomienda monitorear por 5000km.',
        'servicios': [
            ('Cambio de aceite 5W-30 sintético', 1, 95),
            ('Cambio filtros (aceite, aire, combustible, polen)', 1, 55),
            ('Diagnóstico electrónico OBD2', 1, 70),
        ],
        'productos_inv': [
            ('Aceite 5W-30 Full Sintético 1L', 4),
            ('Filtro de Aceite Toyota', 1),
            ('Filtro de Aire Universal', 1),
            ('Filtro de Polen Honda', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '8901-BCD', 'mecanico': mec1, 'creado_por': sup_u or admin_u,
        'estado': 'COBRADA', 'km': 29000, 'dias_atras': 42,
        'diagnostico': 'Vibración en volante a más de 80 km/h. Balanceo y alineación necesarios.',
        'observaciones': 'Se realizó balanceo 4 neumáticos y alineación computarizada.',
        'servicios': [
            ('Balanceo 4 neumáticos (con pesas)', 1, 80),
            ('Alineación computarizada 4 ruedas', 1, 100),
            ('Revisión de terminales y rótulas', 1, 50),
        ],
        'productos_inv': [],
        'repuestos_ext': [],
    },
    {
        'placa': '6789-STU', 'mecanico': mec2, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 178000, 'dias_atras': 35,
        'diagnostico': 'Cambio de amortiguadores delanteros. Cliente reporta golpeteo en suspensión.',
        'observaciones': 'Amortiguadores traseros aún con vida útil. Se reemplazaron los 2 delanteros.',
        'servicios': [
            ('Cambio de amortiguadores delanteros (par)', 1, 180),
            ('Revisión completa de suspensión', 1, 80),
            ('Alineación post-reparación', 1, 100),
        ],
        'productos_inv': [
            ('Amortiguador Delantero D.', 2),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '4567-YZA', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 25000, 'dias_atras': 28,
        'diagnostico': 'Revisión general pre-viaje. Cambio aceite y revisión de seguridad.',
        'observaciones': 'Todo en orden. Bujías revisadas, filtros reemplazados.',
        'servicios': [
            ('Servicio de mantenimiento básico', 1, 70),
            ('Revisión de seguridad pre-viaje', 1, 50),
        ],
        'productos_inv': [
            ('Aceite 10W-40 Semisintético 1L', 3),
            ('Filtro de Aceite Toyota', 1),
            ('Bujías NGK (juego x4)', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '2345-EFG', 'mecanico': mec2, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 139000, 'dias_atras': 20,
        'diagnostico': 'Embrague con patinaje. Cliente reporta dificultad para meter cambios.',
        'observaciones': 'Se reemplazó kit completo de embrague: plato, disco y collarín.',
        'servicios': [
            ('Cambio de embrague completo (incluye mano de obra)', 1, 350),
            ('Ajuste de horquilla y cable embrague', 1, 50),
        ],
        'productos_inv': [
            ('Kit Embrague Completo', 1),
        ],
        'repuestos_ext': [
            ('Collarín de embrague Isuzu D-Max', 'Mecánica del Norte', 1, 220),
        ],
    },
]

ordenes_obj = {}
for od in ordenes_cobradas:
    if OrdenTrabajo.objects.filter(vehiculo=veh_obj.get(od['placa']), kilometraje=od['km']).exists():
        ot = OrdenTrabajo.objects.filter(vehiculo=veh_obj.get(od['placa']), kilometraje=od['km']).first()
        log(f"OT ya existe: {ot.numero_orden}")
        ordenes_obj[od['placa']] = ot
        continue

    ot = crear_orden(
        placa=od['placa'], mecanico=od['mecanico'],
        creado_por=od['creado_por'], estado=od['estado'],
        diagnostico=od['diagnostico'], observaciones=od['observaciones'],
        km=od['km'], dias_atras=od['dias_atras'],
        servicios=od['servicios'],
        productos_inv=od['productos_inv'],
        repuestos_ext=od['repuestos_ext'],
    )
    if ot:
        recibo = cobrar_orden(ot, admin_u)
        ordenes_obj[od['placa'] + str(od['dias_atras'])] = ot
        log(f"OT COBRADA: {ot.numero_orden} — {od['placa']} — Bs {ot.total:.0f} → Rec: {recibo.numero_recibo}")


# ── LOTE 2: Órdenes EN_PROCESO y COMPLETADA (semana pasada) ──────────────────
ordenes_activas_data = [
    {
        'placa': '5678-DEF', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'EN_PROCESO', 'km': 21500, 'dias_atras': 2,
        'diagnostico': 'Luz Check Engine encendida. Código P0171 — mezcla pobre banco 1.',
        'observaciones': 'Se está diagnosticando sensor MAP y oxígeno.',
        'servicios': [
            ('Diagnóstico electrónico avanzado OBD2', 1, 90),
        ],
        'productos_inv': [],
        'repuestos_ext': [],
    },
    {
        'placa': '0123-VWX', 'mecanico': mec2, 'creado_por': sup_u or admin_u,
        'estado': 'ESPERA_REPUESTOS', 'km': 93500, 'dias_atras': 4,
        'diagnostico': 'Radiador con micro-fisura en aleta. Pérdida de refrigerante en frío.',
        'observaciones': 'Se pidió radiador al proveedor. Estimado de llegada: 2 días.',
        'servicios': [
            ('Cambio de radiador y mangueras', 1, 220),
            ('Recarga de refrigerante y purga sistema', 1, 60),
        ],
        'productos_inv': [],
        'repuestos_ext': [],
    },
    {
        'placa': '6789-HIJ', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'COMPLETADA', 'km': 75000, 'dias_atras': 3,
        'diagnostico': 'Mantenimiento 75.000 km. Cambio de aceite, filtros y bujías.',
        'observaciones': 'Revisión completada. Listo para entrega.',
        'servicios': [
            ('Cambio de aceite y filtro', 1, 70),
            ('Cambio de bujías (x4)', 1, 60),
            ('Limpieza de inyectores', 1, 120),
        ],
        'productos_inv': [
            ('Aceite 10W-40 Semisintético 1L', 4),
            ('Filtro de Aceite Toyota', 1),
            ('Bujías NGK (juego x4)', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '2345-PQR', 'mecanico': mec2, 'creado_por': admin_u,
        'estado': 'PENDIENTE', 'km': 15000, 'dias_atras': 1,
        'diagnostico': 'Cliente solicita revisión de frenos y cambio de pastillas traseras.',
        'observaciones': 'Vehículo recién ingresado. Pendiente de asignación a bahía.',
        'servicios': [],
        'productos_inv': [],
        'repuestos_ext': [],
    },
    {
        'placa': '0123-KLM', 'mecanico': mec1, 'creado_por': sup_u or admin_u,
        'estado': 'PENDIENTE', 'km': 7800, 'dias_atras': 0,
        'diagnostico': 'Revisión general a los 8.000 km. Primera revisión post-compra.',
        'observaciones': 'Garantía de fábrica vigente. Se realizará solo revisión sin cargo.',
        'servicios': [
            ('Revisión general garantía 8.000 km', 1, 0),
        ],
        'productos_inv': [],
        'repuestos_ext': [],
    },
]

for od in ordenes_activas_data:
    if OrdenTrabajo.objects.filter(vehiculo=veh_obj.get(od['placa']), kilometraje=od['km']).exists():
        log(f"OT ya existe para {od['placa']}")
        continue
    ot = crear_orden(
        placa=od['placa'], mecanico=od['mecanico'],
        creado_por=od['creado_por'], estado=od['estado'],
        diagnostico=od['diagnostico'], observaciones=od['observaciones'],
        km=od['km'], dias_atras=od['dias_atras'],
        servicios=od['servicios'],
        productos_inv=od['productos_inv'],
        repuestos_ext=od['repuestos_ext'],
    )
    if ot:
        log(f"OT {od['estado']}: {ot.numero_orden} — {od['placa']}")


# ── LOTE 3: Segunda visita del mismo cliente ──────────────────────────────────
segunda_visita = [
    {
        'placa': '1234-ABC', 'mecanico': mec2, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 68000, 'dias_atras': 15,
        'diagnostico': 'Revisión posterior. Terminal de dirección con juego excesivo.',
        'observaciones': 'Se reemplazó terminal izquierdo. Alineación post-reparación realizada.',
        'servicios': [
            ('Cambio de terminal de dirección izquierdo', 1, 80),
            ('Alineación computarizada', 1, 100),
        ],
        'productos_inv': [
            ('Terminal de Dirección', 1),
        ],
        'repuestos_ext': [],
    },
    {
        'placa': '3456-JKL', 'mecanico': mec1, 'creado_por': admin_u,
        'estado': 'COBRADA', 'km': 38500, 'dias_atras': 10,
        'diagnostico': 'Calefacción no calienta. Termostato posiblemente bloqueado en abierto.',
        'observaciones': 'Termostato reemplazado. Sistema de refrigeración revisado y purgado.',
        'servicios': [
            ('Cambio de termostato', 1, 90),
            ('Purga sistema de refrigeración', 1, 40),
        ],
        'productos_inv': [
            ('Termostato Motor', 1),
        ],
        'repuestos_ext': [
            ('Refrigerante Toyota Rosa 1L', 'Repuestos Toyota Oficial', 2, 55),
        ],
    },
]

for od in segunda_visita:
    if OrdenTrabajo.objects.filter(vehiculo=veh_obj.get(od['placa']), kilometraje=od['km']).exists():
        log(f"OT ya existe para {od['placa']}")
        continue
    ot = crear_orden(
        placa=od['placa'], mecanico=od['mecanico'],
        creado_por=od['creado_por'], estado=od['estado'],
        diagnostico=od['diagnostico'], observaciones=od['observaciones'],
        km=od['km'], dias_atras=od['dias_atras'],
        servicios=od['servicios'],
        productos_inv=od['productos_inv'],
        repuestos_ext=od['repuestos_ext'],
    )
    if ot:
        recibo = cobrar_orden(ot, admin_u)
        log(f"OT COBRADA (2a visita): {ot.numero_orden} — {od['placa']} — Bs {ot.total:.0f}")


# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
seccion("✅ RESUMEN FINAL")

print(f"  Categorías:       {CategoriaProducto.objects.count()}")
print(f"  Productos inv.:   {ProductoBase.objects.count()} ({RepuestoGenerico.objects.count()} repuestos, {Neumatico.objects.count()} neumáticos, {Llanta.objects.count()} llantas)")
print(f"  Movimientos stk:  {MovimientoStock.objects.count()}")
print(f"  Clientes:         {Cliente.objects.count()}")
print(f"  Vehículos:        {Vehiculo.objects.count()}")
print(f"  Órdenes totales:  {OrdenTrabajo.objects.count()}")
print(f"    COBRADAS:       {OrdenTrabajo.objects.filter(estado='COBRADA').count()}")
print(f"    COMPLETADAS:    {OrdenTrabajo.objects.filter(estado='COMPLETADA').count()}")
print(f"    EN PROCESO:     {OrdenTrabajo.objects.filter(estado='EN_PROCESO').count()}")
print(f"    ESPERA REP.:    {OrdenTrabajo.objects.filter(estado='ESPERA_REPUESTOS').count()}")
print(f"    PENDIENTES:     {OrdenTrabajo.objects.filter(estado='PENDIENTE').count()}")
print(f"  Recibos:          {Recibo.objects.count()}")
print(f"  Pagos:            {Pago.objects.count()}")
print(f"\n  🎉 Seed completado exitosamente!\n")

