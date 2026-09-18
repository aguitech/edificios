"""
aguitech_city_v5 — 10 PLAZAS COMERCIALES AGUITECH (versión lujosa)
====================================================================

Cada plaza comercial incluye:
  - Estructura principal 3 pisos
  - Fachada mixta (espejo azul + vidrio + metal)
  - 30+ locales con marquesinas neón (10 por piso)
  - Negocio ancla en planta baja (cine/gimnasio/supermercado/restaurante/banco)
  - 3-4 espectaculares en azotea con logo A
  - Estacionamiento multi-nivel visible
  - Plaza interior con fuente + jardín neón
  - Escaleras eléctricas / entradas iluminadas
  - Iluminación LED perimetral
  - Antena de comunicaciones

Render  -> aguitech_city/imagenes/aguitech_city_v5.png  (1920x1080)
Blend   -> aguitech_city/aguitech_city_v5.blend
"""

import bpy
import math
import os
import sys
import traceback
import random

LOG_FILE = "/tmp/aguitech_city_v5.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")
        f.flush()

try: os.remove(LOG_FILE)
except FileNotFoundError: pass

log("=" * 70)
log("AGUITECH CITY v5 — 10 PLAZAS COMERCIALES")
log("=" * 70)
log(f"Blender {bpy.app.version_string}, Python {sys.version.split()[0]}")

def safe_run(label, fn):
    log(f"  {label}...")
    try:
        fn()
        log(f"  {label} OK")
    except Exception:
        log(f"  {label} ERROR:\n{traceback.format_exc()}")
        raise

# ╔════════════════════════════════════════════════════════════════════╗
# ║ RUTAS                                                              ║
# ╚════════════════════════════════════════════════════════════════════╝
SCRIPT_DIR  = "/Users/hectoraguilar/Projects/edificio/edificios/aguitech_city"
IMAGES_DIR  = os.path.join(SCRIPT_DIR, "imagenes")
BLEND_PATH  = os.path.join(SCRIPT_DIR, "aguitech_city_v5.blend")
RENDER_PATH = os.path.join(IMAGES_DIR, "aguitech_city_v5.png")

# ╔════════════════════════════════════════════════════════════════════╗
# ║ PALETA                                                             ║
# ╚════════════════════════════════════════════════════════════════════╝
COL_NEON_BLUE   = (0.10, 0.55, 1.00, 1)
COL_NEON_CYAN   = (0.30, 0.85, 1.00, 1)
COL_NEON_MAGENTA= (1.00, 0.18, 0.55, 1)
COL_NEON_PURPLE = (0.55, 0.25, 1.00, 1)
COL_NEON_PINK   = (1.00, 0.40, 0.75, 1)
COL_NEON_TEAL   = (0.10, 0.85, 0.75, 1)
COL_NEON_GREEN  = (0.20, 1.00, 0.50, 1)
COL_NEON_AMBER  = (1.00, 0.65, 0.10, 1)
COL_NEON_ORANGE = (1.00, 0.45, 0.10, 1)
COL_NEON_LIME   = (0.65, 1.00, 0.20, 1)
COL_MIRROR_BLUE = (0.06, 0.20, 0.45, 1)
COL_MIRROR_DARK = (0.04, 0.08, 0.18, 1)
COL_DARK_GLASS  = (0.04, 0.06, 0.10, 1)
COL_METAL_DARK  = (0.08, 0.09, 0.12, 1)
COL_METAL_LIGHT = (0.55, 0.58, 0.62, 1)
COL_CONCRETE    = (0.22, 0.23, 0.26, 1)
COL_ASPHALT     = (0.06, 0.06, 0.08, 1)
COL_GRASS       = (0.03, 0.10, 0.05, 1)
COL_LOGO_WHITE  = (0.95, 0.97, 1.00, 1)
COL_WARM_LED    = (1.00, 0.78, 0.35, 1)

_mat_cache = {}
def _rgb(c): return (c[0], c[1], c[2])

# ╔════════════════════════════════════════════════════════════════════╗
# ║ UTILIDADES                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def mat(name, base, rough=0.5, metal=0.0, emi=None, emi_s=0.0,
        alpha=1.0, ior=1.45):
    if name in _mat_cache: return _mat_cache[name]
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    ns = m.node_tree.nodes
    ls = m.node_tree.links
    for n in ns: ns.remove(n)
    bsdf = ns.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        m.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha
    if emi is not None:
        bsdf.inputs["Emission Color"].default_value = emi
        bsdf.inputs["Emission Strength"].default_value = emi_s
    out = ns.new("ShaderNodeOutputMaterial")
    ls.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _mat_cache[name] = m
    return m

def emissive(name, color, strength=5.0):
    return mat(name, color, 0.3, 0.0, color, strength)

def mirror(name, tint=COL_MIRROR_BLUE, rough=0.05):
    return mat(name, tint, rough, 0.95)

def assign(obj, m):
    if obj.data.materials:
        obj.data.materials[0] = m
    else:
        obj.data.materials.append(m)

def box(name, w, h, d, loc=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name; o.scale = (w, h, d)
    return o

def cyl(name, r, h, loc=(0,0,0), v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=v, location=loc)
    o = bpy.context.active_object
    o.name = name
    return o

def sphere(name, r, loc=(0,0,0), seg=32, rng=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=rng)
    o = bpy.context.active_object
    o.name = name
    return o

def torus(name, R, r, loc=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=64, minor_segments=24)
    o = bpy.context.active_object
    o.name = name
    return o

def cone(name, r1, r2, h, loc=(0,0,0), v=16):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, vertices=v, location=loc)
    o = bpy.context.active_object
    o.name = name
    return o

def bevel(o, w=0.02, s=2):
    m = o.modifiers.new(name="Bevel", type='BEVEL')
    m.width = w; m.segments = s; m.limit_method = 'ANGLE'

# ╔════════════════════════════════════════════════════════════════════╗
# ║ 01. LIMPIAR + TERRENO BASE                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(73)

def build_ground():
    """Terreno base amplio + avenida circular central."""
    ground = box("Ground", 500, 500, 0.1, loc=(0, 0, -0.05))
    assign(ground, mat("GroundMat", COL_ASPHALT, 0.9))

    # Anillo central (rotonda) donde confluyen las 10 plazas
    ring_outer = torus("RoundaboutOuter", 35, 4, loc=(0, 0, 0.05))
    assign(ring_outer, mat("RoundaboutMat", COL_ASPHALT, 0.85))

    # Anillo interior decorativo LED
    ring_led = torus("RoundaboutLED", 25, 0.5, loc=(0, 0, 0.10))
    assign(ring_led, emissive("RoundaboutLEDMat", COL_NEON_CYAN, 12.0))

    # 10 calles radiales desde la rotonda
    for i in range(10):
        ang = math.radians(i * 36)
        rad = math.radians(ang)
        cx = math.cos(rad) * 100
        cy = math.sin(rad) * 100
        # Dibujar línea de calle (plano emisivo)
        length = 100
        for t in [0.3, 0.5, 0.7]:
            sx = math.cos(rad) * length * t
            sy = math.sin(rad) * length * t
            mark = box(f"StreetMark_{i}_{t}", 8, 0.3, 0.05,
                       loc=(sx, sy, 0.06))
            assign(mark, emissive(f"StreetMarkMat_{i}_{t}",
                                    COL_NEON_AMBER, 1.5))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 02. COMPONENTES DE PLAZA                                            ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_storefront(pi, floor_idx, side, position):
    """Un local con marquesina neón y escaparate iluminado.
    pi = plaza index, floor_idx = 0/1/2, side = 'N'/'S'/'E'/'W'
    position = índice dentro del lado (0..n)
    """
    name = f"P{pi}_L{floor_idx}_{side}_{position}"
    # Dimensiones del local según piso
    if floor_idx == 0:
        w, h, d = 4, 4.5, 3  # planta baja más alta
    else:
        w, h, d = 4, 3.5, 3

    # Escaparate frontal emisivo (vidrio店内 iluminado)
    storefront_col = random.choice([
        COL_NEON_CYAN, COL_NEON_MAGENTA, COL_NEON_PINK,
        COL_NEON_AMBER, COL_NEON_PURPLE, COL_NEON_GREEN,
        COL_NEON_TEAL, COL_NEON_LIME, COL_NEON_ORANGE,
        COL_WARM_LED, COL_NEON_BLUE
    ])
    storefront = box(f"{name}_Store", w*0.9, 0.05, h*0.7,
                     loc=(position[0], position[1], position[2] + h*0.45))
    assign(storefront, emissive(f"{name}_StoreMat",
                                   storefront_col, random.uniform(2.5, 5.0)))

    # Marquesina sobre el escaparate
    marquee = box(f"{name}_Marquee", w*1.05, d*0.6, 0.4,
                   loc=(position[0], position[1] + d*0.4,
                        position[2] + h + 0.2))
    marq_col = random.choice([
        COL_NEON_BLUE, COL_NEON_MAGENTA, COL_NEON_PINK,
        COL_NEON_CYAN, COL_NEON_PURPLE, COL_NEON_AMBER
    ])
    assign(marquee, mat(f"{name}_MarqueeMat", marq_col, 0.5, 0.0,
                          marq_col, 4.5))

    # Texto/logo en marquesina (3-5 cubos pequeños)
    n_letters = random.randint(3, 5)
    for j in range(n_letters):
        lt = box(f"{name}_Let_{j}", 0.4, 0.05, 0.25,
                  loc=(position[0] - w*0.35 + j*(w*0.7/(n_letters-1)),
                       position[1] + d*0.4 + 0.05,
                       position[2] + h + 0.2))
        assign(lt, emissive(f"{name}_LetMat_{j}",
                              random.choice([COL_LOGO_WHITE, COL_NEON_AMBER]),
                              7.0))

    # Puerta (en locales de planta baja)
    if floor_idx == 0:
        door = box(f"{name}_Door", 0.8, 0.05, 1.5,
                   loc=(position[0], position[1] - d*0.4,
                        position[2] + 0.75))
        assign(door, mat(f"{name}_DoorMat",
                          random.choice([COL_DARK_GLASS, (0.10, 0.10, 0.12, 1)]),
                          0.2, 0.4, COL_WARM_LED, 0.5))


def build_floor(pi, floor_idx, plaza_w, plaza_d, plaza_h):
    """Construye un piso entero con locales a los 4 lados."""
    floor_z = floor_idx * 4.5  # cada piso 4.5m

    # 8 locales por lado (Norte/Sur) x 2 lados = 16
    # Más 8 por lado (Este/Oeste) x 2 lados = 16
    # Total: 32 locales por piso (≈30)
    n_per_side = 7
    store_d = 3.5
    total_w = n_per_side * 4 + (n_per_side + 1) * 0.3
    spacing_x = plaza_w / (n_per_side + 1)

    # Norte (y positivo)
    for k in range(n_per_side):
        x = -plaza_w/2 + spacing_x * (k + 1)
        y = plaza_d/2 - 0.1
        z = floor_z
        build_storefront(pi, floor_idx, 'N', (x, y, z))

    # Sur (y negativo)
    for k in range(n_per_side):
        x = -plaza_w/2 + spacing_x * (k + 1)
        y = -plaza_d/2 + 0.1
        z = floor_z
        build_storefront(pi, floor_idx, 'S', (x, y, z))

    # Este (x positivo)
    n_per_side_v = 5
    spacing_y = plaza_d / (n_per_side_v + 1)
    for k in range(n_per_side_v):
        x = plaza_w/2 - 0.1
        y = -plaza_d/2 + spacing_y * (k + 1)
        z = floor_z
        build_storefront(pi, floor_idx, 'E', (x, y, z))

    # Oeste (x negativo)
    for k in range(n_per_side_v):
        x = -plaza_w/2 + 0.1
        y = -plaza_d/2 + spacing_y * (k + 1)
        z = floor_z
        build_storefront(pi, floor_idx, 'W', (x, y, z))


def build_anchor_store(pi, plaza_w, plaza_d):
    """Negocio ancla en planta baja (más grande, con diseño distintivo)."""
    # Frente a la entrada principal de la plaza
    anchor_types = [
        ("CINEMA", COL_NEON_MAGENTA, "🎬"),
        ("GYM", COL_NEON_GREEN, "💪"),
        ("MERCADO", COL_NEON_AMBER, "🛒"),
        ("BANCO", COL_NEON_BLUE, "🏦"),
        ("RESTAURANT", COL_NEON_PINK, "🍽️"),
        ("DEPT_STORE", COL_NEON_PURPLE, "🛍️"),
        ("BOWLING", COL_NEON_TEAL, "🎳"),
        ("ELECTRONICS", COL_NEON_CYAN, "📱"),
        ("BOOKSTORE", COL_NEON_LIME, "📚"),
        ("ARCADE", COL_NEON_ORANGE, "🕹️"),
    ]
    anchor_name, anchor_col, _ = anchor_types[pi % len(anchor_types)]

    # Local ancla: ocupa el centro del lado norte
    w = plaza_w * 0.55
    h = 5
    d = 4
    body = box(f"P{pi}_Anchor", w, d, h, loc=(0, plaza_d/2 + d/2 - 0.1, h/2))
    assign(body, mat(f"P{pi}_AnchorMat",
                      random.choice([COL_DARK_GLASS, COL_METAL_DARK,
                                      (0.10, 0.12, 0.18, 1)]), 0.25, 0.7))

    # Pantalla LED gigante con el nombre
    screen = box(f"P{pi}_AnchorScreen", w*0.85, 0.05, h*0.6,
                  loc=(0, plaza_d/2 + d - 0.1, h*0.6))
    assign(screen, emissive(f"P{pi}_AnchorScreenMat", anchor_col, 9.0))

    # Logo grande en la pantalla
    n_letters = len(anchor_name)
    for j, ch in enumerate(anchor_name):
        lt = box(f"P{pi}_Anchor_Let_{j}", 0.6, 0.05, 1.2,
                  loc=(-w*0.35 + j*(w*0.7/(n_letters-1)),
                        plaza_d/2 + d - 0.08, h*0.6))
        assign(lt, emissive(f"P{pi}_Anchor_LetMat_{j}",
                              COL_LOGO_WHITE, 14.0))


def build_inner_courtyard(pi, plaza_w, plaza_d):
    """Plaza interior con fuente y jardín neón."""
    cx, cy = 0, 0

    # Patio central (hundido medio nivel)
    patio = box(f"P{pi}_Patio", plaza_w*0.4, plaza_d*0.4, 0.05,
                loc=(cx, cy, 0.025))
    assign(patio, mat(f"P{pi}_PatioMat",
                       random.choice([COL_CONCRETE, (0.30, 0.30, 0.32, 1)]), 0.6))

    # Fuente interior
    fuente_base = cyl(f"P{pi}_FuenteBase", 3.5, 0.4, loc=(cx, cy, 0.2), v=32)
    assign(fuente_base, mat(f"P{pi}_FuenteBaseMat", COL_METAL_DARK, 0.25, 0.85))

    # Piscina
    pool = cyl(f"P{pi}_Pool", 3.0, 0.08, loc=(cx, cy, 0.42), v=32)
    assign(pool, mat(f"P{pi}_PoolMat",
                     (0.02, 0.15, 0.30, 1), 0.05, 0.0,
                     COL_NEON_CYAN, 3.5))

    # Anillos concéntricos en la piscina
    for i, rad in enumerate([2.5, 2.0, 1.5, 1.0]):
        ring = torus(f"P{pi}_PoolRing_{i}", rad, 0.04, loc=(cx, cy, 0.45))
        ring.rotation_euler = (math.radians(90), 0, 0)
        col_r = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                COL_NEON_PINK, COL_NEON_BLUE])
        assign(ring, emissive(f"P{pi}_PoolRingMat_{i}", col_r, 7.0))

    # Chorro central
    jet = cone(f"P{pi}_Jet", 0.25, 0.08, 8, loc=(cx, cy, 4.5), v=20)
    assign(jet, mat(f"P{pi}_JetMat",
                     (0.50, 0.85, 1.0, 0.7), 0.08, 0.0,
                     COL_NEON_CYAN, 5.0))

    # Jardín neón perimetral
    garden_positions = []
    for ang_deg in range(0, 360, 30):
        rad = math.radians(ang_deg)
        r = (plaza_w + plaza_d) / 4 + 4
        gx = cx + math.cos(rad) * r
        gy = cy + math.sin(rad) * r
        garden_positions.append((gx, gy))

    for i, (gx, gy) in enumerate(garden_positions):
        # Tronco
        trunk = cyl(f"P{pi}_Tree_{i}_Trunk", 0.18, 2.5,
                     loc=(gx, gy, 1.25), v=8)
        assign(trunk, mat(f"P{pi}_Tree_{i}_TrunkMat",
                           (0.06, 0.05, 0.04, 1), 0.8, 0.0,
                           COL_NEON_CYAN, 0.3))
        # Copa
        crown = sphere(f"P{pi}_Tree_{i}_Crown", 1.4,
                        loc=(gx, gy, 3.0))
        crown.scale = (1, 1, 0.7)
        col = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                              COL_NEON_PURPLE, COL_NEON_PINK, COL_NEON_GREEN])
        assign(crown, emissive(f"P{pi}_Tree_{i}_CrownMat", col, 3.5))


def build_parking(pi, x, y, w, d):
    """Estacionamiento multi-nivel visible al lado de la plaza."""
    levels = 3
    for lvl in range(levels):
        # Plataforma
        platform = box(f"P{pi}_Park_{lvl}", w, d, 0.3,
                        loc=(x, y, 0.15 + lvl * 3))
        assign(platform, mat(f"P{pi}_Park_{lvl}_Mat", COL_CONCRETE, 0.85))

        # Barandilla LED
        for side_sign in (-1, 1):
            rail = box(f"P{pi}_Park_{lvl}_Rail_{side_sign}", w, 0.08, 0.6,
                        loc=(x, y + side_sign * d/2, 0.15 + lvl*3 + 0.5))
            assign(rail, emissive(f"P{pi}_Park_{lvl}_RailMat_{side_sign}",
                                    COL_NEON_AMBER, 5.0))

        # Columnas estructurales
        for cx in (-w/2 + 1, w/2 - 1):
            for cy in (-d/2 + 1, d/2 - 1):
                col = cyl(f"P{pi}_Park_{lvl}_Col_{cx}_{cy}", 0.20, 3,
                           loc=(x + cx, y + cy, lvl * 3 + 1.5))
                assign(col, mat(f"P{pi}_Park_{lvl}_ColMat",
                                 COL_CONCRETE, 0.7, 0.0, COL_NEON_BLUE, 0.2))

        # Algunos autos estacionados (3 por nivel)
        if lvl < 2:  # no en el último
            for j in range(3):
                ax = x - w/2 + 3 + j * (w-4)/2
                ay = y + random.choice([-d/4, d/4])
                car = box(f"P{pi}_Park_{lvl}_Car_{j}", 1.0, 1.8, 0.7,
                            loc=(ax, ay, 0.15 + lvl*3 + 0.55))
                car_col = random.choice([COL_NEON_BLUE, COL_NEON_CYAN,
                                          COL_NEON_MAGENTA, COL_NEON_PURPLE,
                                          COL_NEON_PINK, COL_WARM_LED])
                assign(car, mat(f"P{pi}_Park_{lvl}_CarMat_{j}",
                                 car_col, 0.3, 0.6, car_col, 0.3))
                # Faros
                for hy in (-0.6, 0.6):
                    hl = sphere(f"P{pi}_Park_{lvl}_HL_{j}_{hy}", 0.08,
                                 loc=(ax + 0.55, ay + hy, 0.15 + lvl*3 + 0.55))
                    assign(hl, emissive(f"P{pi}_Park_{lvl}_HLMat_{j}_{hy}",
                                          COL_WARM_LED, 25.0))


def build_billboard_on_roof(name_prefix, x, y, z, w=8, h=4):
    """Espectacular con pantalla LED sobre 2 postes."""
    # Pantalla
    screen = box(f"{name_prefix}_Screen", w, 0.15, h, loc=(x, y, z + h/2 + 0.5))
    sc_col = random.choice([COL_NEON_MAGENTA, COL_NEON_CYAN, COL_NEON_PINK,
                             COL_NEON_AMBER, COL_NEON_PURPLE, COL_NEON_GREEN])
    assign(screen, emissive(f"{name_prefix}_ScreenMat", sc_col, 7.5))

    # Marco
    frame = box(f"{name_prefix}_Frame", w+0.3, 0.20, h+0.3, loc=(x, y, z + h/2 + 0.5))
    assign(frame, mat(f"{name_prefix}_FrameMat", COL_METAL_DARK, 0.4, 0.8))

    # Logo "A"
    logo_size = min(w, h) * 0.4
    leg_l = box(f"{name_prefix}_A_L", 0.12, 0.18, logo_size,
                 loc=(x - w*0.10, y + 0.12, z + h/2 + 0.5))
    leg_l.rotation_euler = (0, 0, math.radians(-12))
    assign(leg_l, emissive(f"{name_prefix}_ALMat", COL_LOGO_WHITE, 12.0))
    leg_r = box(f"{name_prefix}_A_R", 0.12, 0.18, logo_size,
                 loc=(x + w*0.10, y + 0.12, z + h/2 + 0.5))
    leg_r.rotation_euler = (0, 0, math.radians(12))
    assign(leg_r, emissive(f"{name_prefix}_ARMat", COL_LOGO_WHITE, 12.0))
    cross = box(f"{name_prefix}_A_C", w*0.35, 0.18, 0.18,
                 loc=(x, y + 0.12, z + h/2 + 0.5 - logo_size*0.20))
    assign(cross, emissive(f"{name_prefix}_ACMat", COL_LOGO_WHITE, 12.0))

    # 2 postes
    for px_off in (-w/2 + 0.4, w/2 - 0.4):
        post = cyl(f"{name_prefix}_Post_{px_off}", 0.10, z + h/2,
                    loc=(x + px_off, y, (z + h/2)/2))
        assign(post, mat(f"{name_prefix}_PostMat", COL_METAL_DARK, 0.4, 0.9))


def build_plaza_structure(pi, x, y, plaza_w=40, plaza_d=30, plaza_h=13.5):
    """Construye UNA plaza comercial completa."""
    log(f"  → construyendo plaza {pi}...")

    # ─── Estructura principal (3 pisos) ───
    # Fachada exterior mixta: espejo azul + vidrio oscuro
    # Fachada norte
    body_n = box(f"P{pi}_BodyN", plaza_w, 0.5, plaza_h,
                  loc=(x, y + plaza_d/2, plaza_h/2))
    col_body = random.choice([COL_MIRROR_BLUE, COL_MIRROR_DARK,
                                (0.05, 0.15, 0.40, 1)])
    assign(body_n, mirror(f"P{pi}_BodyMatN", col_body, 0.06))
    bevel(body_n, 0.1, 3)

    # Fachada sur
    body_s = box(f"P{pi}_BodyS", plaza_w, 0.5, plaza_h,
                  loc=(x, y - plaza_d/2, plaza_h/2))
    assign(body_s, mirror(f"P{pi}_BodyMatS", col_body, 0.06))
    bevel(body_s, 0.1, 3)

    # Fachada este
    body_e = box(f"P{pi}_BodyE", 0.5, plaza_d, plaza_h,
                  loc=(x + plaza_w/2, y, plaza_h/2))
    assign(body_e, mirror(f"P{pi}_BodyMatE", col_body, 0.06))
    bevel(body_e, 0.1, 3)

    # Fachada oeste
    body_w = box(f"P{pi}_BodyW", 0.5, plaza_d, plaza_h,
                  loc=(x - plaza_w/2, y, plaza_h/2))
    assign(body_w, mirror(f"P{pi}_BodyMatW", col_body, 0.06))
    bevel(body_w, 0.1, 3)

    # ─── Franjas LED horizontales entre pisos ───
    for z_band in (4.5, 9.0):
        # 4 lados
        for side_name, dx, dy, dw, dd in [
            ("N", 0, plaza_d/2, plaza_w, 0.20),
            ("S", 0, -plaza_d/2, plaza_w, 0.20),
            ("E", plaza_w/2, 0, 0.20, plaza_d),
            ("W", -plaza_w/2, 0, 0.20, plaza_d),
        ]:
            band = box(f"P{pi}_Band_{z_band}_{side_name}", dw, dd, 0.25,
                        loc=(x + dx, y + dy, z_band))
            assign(band, emissive(f"P{pi}_BandMat_{z_band}_{side_name}",
                                    random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                    COL_NEON_PINK, COL_NEON_PURPLE]),
                                    10.0))

    # ─── Techo (azotea) ───
    roof = box(f"P{pi}_Roof", plaza_w+0.5, plaza_d+0.5, 0.4,
                loc=(x, y, plaza_h + 0.2))
    assign(roof, mat(f"P{pi}_RoofMat", COL_METAL_DARK, 0.4, 0.8))

    # Cornisa LED superior
    cornice = box(f"P{pi}_Cornice", plaza_w+0.8, plaza_d+0.8, 0.15,
                   loc=(x, y, plaza_h + 0.55))
    assign(cornice, emissive(f"P{pi}_CorniceMat", COL_NEON_CYAN, 9.0))

    # ─── 3 pisos con locales ───
    for floor_idx in range(3):
        build_floor(pi, floor_idx, plaza_w, plaza_d, plaza_h)

    # ─── Negocio ancla ───
    build_anchor_store(pi, plaza_w, plaza_d)

    # ─── Plaza interior ───
    build_inner_courtyard(pi, plaza_w, plaza_d)

    # ─── Entradas iluminadas (4 caras) ───
    for side, ex, ey in [
        ("N", x, y + plaza_d/2 + 0.5),
        ("S", x, y - plaza_d/2 - 0.5),
        ("E", x + plaza_w/2 + 0.5, y),
        ("W", x - plaza_w/2 - 0.5, y),
    ]:
        # Arco de entrada
        arch = torus(f"P{pi}_Arch_{side}", 1.5, 0.12,
                      loc=(ex, ey, 1.5))
        if side in ("N", "S"):
            arch.rotation_euler = (math.radians(90), 0, 0)
        else:
            arch.rotation_euler = (0, math.radians(90), 0)
        assign(arch, emissive(f"P{pi}_ArchMat_{side}",
                                random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                COL_NEON_PINK]),
                                8.0))

        # Letrero "ENTRADA" o "ENTRY"
        entry_sign = box(f"P{pi}_Entry_{side}", 2.5, 0.05, 0.4,
                          loc=(ex, ey + (0.3 if side == "N" else -0.3 if side == "S" else 0),
                                3.0))
        assign(entry_sign, emissive(f"P{pi}_EntryMat_{side}",
                                      random.choice([COL_NEON_GREEN, COL_NEON_AMBER]),
                                      7.0))

    # ─── Estacionamiento al lado ───
    build_parking(pi, x + plaza_w/2 + 12, y, 18, 12)

    # ─── Espectaculares en azotea (3 por plaza) ───
    roof_z = plaza_h + 1.0
    build_billboard_on_roof(f"P{pi}_BB1", x - plaza_w/3, y - plaza_d/4, roof_z, w=10, h=5)
    build_billboard_on_roof(f"P{pi}_BB2", x + plaza_w/3, y + plaza_d/4, roof_z, w=8, h=4)
    build_billboard_on_roof(f"P{pi}_BB3", x, y + plaza_d/3, roof_z, w=12, h=4)

    # ─── Antena de comunicaciones ───
    ant = cyl(f"P{pi}_Antenna", 0.08, 6, loc=(x, y, plaza_h + 4))
    assign(ant, emissive(f"P{pi}_AntennaMat", COL_NEON_CYAN, 8.0))
    tip = sphere(f"P{pi}_AntennaTip", 0.30, loc=(x, y, plaza_h + 7))
    assign(tip, emissive(f"P{pi}_AntennaTipMat", COL_WARM_LED, 25.0))

    # ─── Logo "A" gigante vertical en la fachada principal ───
    logo_z = plaza_h * 0.55
    size = plaza_h * 0.18
    leg_l = box(f"P{pi}_LogoA_L", 0.5, 0.20, size,
                 loc=(x - plaza_w*0.20, y + plaza_d/2 + 0.30, logo_z))
    leg_l.rotation_euler = (0, 0, math.radians(-12))
    assign(leg_l, emissive(f"P{pi}_LogoALMat", COL_LOGO_WHITE, 13.0))
    leg_r = box(f"P{pi}_LogoA_R", 0.5, 0.20, size,
                 loc=(x + plaza_w*0.20, y + plaza_d/2 + 0.30, logo_z))
    leg_r.rotation_euler = (0, 0, math.radians(12))
    assign(leg_r, emissive(f"P{pi}_LogoARMat", COL_LOGO_WHITE, 13.0))
    cross = box(f"P{pi}_LogoA_C", plaza_w*0.42, 0.20, 0.5,
                 loc=(x, y + plaza_d/2 + 0.30, logo_z - size*0.30))
    assign(cross, emissive(f"P{pi}_LogoACMat", COL_LOGO_WHITE, 13.0))


def build_all_plazas():
    """Construye las 10 plazas comerciales alrededor de la rotonda."""
    log("  → 10 plazas comerciales...")
    plaza_radius = 90  # radio del círculo donde se ubican
    for pi in range(10):
        ang = math.radians(pi * 36 + 18)  # offset para no chocar con calles
        x = math.cos(ang) * plaza_radius
        y = math.sin(ang) * plaza_radius
        # Tamaño aleatorio
        plaza_w = random.choice([38, 40, 42, 45])
        plaza_d = random.choice([28, 30, 32])
        # Altura base 3 pisos de 4.5m = 13.5m
        build_plaza_structure(pi, x, y, plaza_w, plaza_d, 13.5)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 03. ILUMINACIÓN                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_lighting():
    log("    → luces...")
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o, do_unlink=True)

    # Sol atardecer
    bpy.ops.object.light_add(type='SUN',
                              location=(50, 80, 60),
                              rotation=(math.radians(55), math.radians(15), 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 2.0
    sun.data.color = _rgb((1.0, 0.65, 0.40))

    # Ambient
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 120))
    amb = bpy.context.active_object
    amb.name = "HemiAmbient"
    amb.data.energy = 2000
    amb.data.color = _rgb((0.35, 0.40, 0.65))

    # Farolas perimetrales en la rotonda
    for ang_deg in range(0, 360, 15):
        rad = math.radians(ang_deg)
        r = 35
        bpy.ops.object.light_add(type='POINT',
                                  location=(math.cos(rad)*r, math.sin(rad)*r, 4))
        lamp = bpy.context.active_object
        lamp.data.energy = 80
        lamp.data.color = _rgb((1.0, 0.85, 0.55))

    # Rim lights
    for i, (loc, col) in enumerate([
        ((150, 150, 80), (1.0, 0.3, 0.7)),
        ((-150, 150, 80), (0.3, 0.6, 1.0)),
        ((150, -150, 80), (0.8, 0.4, 1.0)),
        ((-150, -150, 80), (0.4, 0.9, 0.9)),
    ]):
        bpy.ops.object.light_add(type='AREA', location=loc,
                                  rotation=(math.radians(70), 0, 0))
        rim = bpy.context.active_object
        rim.data.energy = 600
        rim.data.color = _rgb(col)
        rim.data.size = 35.0

    # Spots sobre las plazas (uno por plaza para iluminarlas)
    for pi in range(10):
        ang = math.radians(pi * 36 + 18)
        x = math.cos(ang) * 90
        y = math.sin(ang) * 90
        bpy.ops.object.light_add(type='SPOT',
                                  location=(x - 30, y - 30, 40),
                                  rotation=(math.radians(55),
                                            math.radians(45), 0))
        spot = bpy.context.active_object
        spot.data.energy = 800
        spot.data.color = _rgb((0.6, 0.85, 1.0))
        spot.data.spot_size = math.radians(35)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 04. CÁMARA + CIELO + RENDER                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_camera():
    bpy.ops.object.camera_add(
        location=(180, -180, 130),
        rotation=(math.radians(35), 0, math.radians(45)))
    cam = bpy.context.active_object
    cam.name = "CinematicCamera"
    cam.data.lens = 32
    cam.data.sensor_width = 36
    cam.data.clip_end = 1000
    bpy.context.scene.camera = cam

def build_sky():
    world = bpy.data.worlds.new("WorldAguitech_v5")
    bpy.context.scene.world = world
    world.use_nodes = True
    ns = world.node_tree.nodes
    ls = world.node_tree.links
    for n in ns: ns.remove(n)

    out = ns.new("ShaderNodeOutputWorld")
    bg = ns.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.03, 0.04, 0.10, 1)
    bg.inputs["Strength"].default_value = 0.30

    coord = ns.new("ShaderNodeTexCoord")
    mapping = ns.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    grad = ns.new("ShaderNodeTexGradient")
    grad.gradient_type = 'SPHERICAL'
    ramp = ns.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.95, 0.45, 0.20, 1)
    ramp.color_ramp.elements[1].color = (0.05, 0.07, 0.18, 1)
    mid = ramp.color_ramp.elements.new(0.5)
    mid.color = (0.55, 0.20, 0.50, 1)

    ls.new(coord.outputs["Object"], mapping.inputs["Vector"])
    ls.new(mapping.outputs["Vector"], grad.inputs["Vector"])
    ls.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    ls.new(ramp.outputs["Color"], bg.inputs["Color"])
    ls.new(bg.outputs["Background"], out.inputs["Surface"])

    # Volumétrico
    vol = ns.new("ShaderNodeVolumeScatter")
    vol.inputs["Color"].default_value = (0.08, 0.12, 0.25, 1)
    vol.inputs["Density"].default_value = 0.016
    vol.inputs["Anisotropy"].default_value = 0.5
    try:
        ls.new(vol.outputs["Volume"], out.inputs["Volume"])
    except Exception:
        pass

def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    try:
        scene.eevee.use_volumetric_lights = True
        scene.eevee.volumetric_light_clamp = 18
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = 1.3
        scene.eevee.bloom_threshold = 0.8
        scene.eevee.bloom_radius = 8.0
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 1.5
        scene.eevee.gtao_factor = 0.7
        scene.eevee.use_ssr = True
    except Exception:
        pass
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = RENDER_PATH
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'


# ╔════════════════════════════════════════════════════════════════════╗
# ║ EJECUCIÓN                                                          ║
# ╚════════════════════════════════════════════════════════════════════╝
try:
    safe_run("01 clear_scene", clear_scene)
    safe_run("02 build_sky", build_sky)
    safe_run("03 build_ground", build_ground)
    safe_run("04 build_all_plazas", build_all_plazas)
    safe_run("05 build_lighting", build_lighting)
    safe_run("06 setup_camera", setup_camera)
    safe_run("07 setup_render", setup_render)

    log("\n>>> Guardando .blend...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log(f">>> .blend guardado en {BLEND_PATH}")

    log("\n>>> Renderizando...")
    bpy.ops.render.render(write_still=True)
    log(f">>> Render guardado en {RENDER_PATH}")

    log("\n" + "=" * 70)
    log("AGUITECH CITY v5 — COMPLETADO")
    log("=" * 70)

except Exception:
    log(f"\nFATAL:\n{traceback.format_exc()}")
    raise
