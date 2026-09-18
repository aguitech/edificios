"""
aguitech_city_v3 — VERSIÓN ÉPICA con mucha más carnita
=======================================================

Mejoras vs v2:
  - Fuente central 3x más grande con múltiples chorros + anillos concéntricos
  - DOBLE de edificios: 22 rascacielos (antes 10) — anillo interno + externo + skyline
  - TODOS los edificios con vidrio espejo azul reflectivo (PBR metalness alto)
  - 12 drones (antes 6)
  - 3 robots de delivery (antes 1)
  - Avenida con viaducto doble (sobre y bajo nivel)
  - 16 árboles neón (antes 9)
  - Pantallas LED publicitarias más grandes y variadas
  - Holograma "A" en 5 torres (antes 3)
  - Iluminación volumétrica más densa

Render  -> aguitech_city/imagenes/aguitech_city_v3.png
Blend   -> aguitech_city/aguitech_city_v3.blend
"""

import bpy
import math
import os
import sys
import traceback
import random

LOG_FILE = "/tmp/aguitech_city_v3.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")
        f.flush()

try:
    os.remove(LOG_FILE)
except FileNotFoundError:
    pass

log("=" * 70)
log("AGUITECH CITY v3 — INICIANDO (versión ÉPICA)")
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
BLEND_PATH  = os.path.join(SCRIPT_DIR, "aguitech_city_v3.blend")
RENDER_PATH = os.path.join(IMAGES_DIR, "aguitech_city_v3.png")

# ╔════════════════════════════════════════════════════════════════════╗
# ║ PALETA AGUITECH v3 — más azul espejo, más neón                     ║
# ╚════════════════════════════════════════════════════════════════════╝
COL_NEON_BLUE   = (0.10, 0.55, 1.00, 1)
COL_NEON_CYAN   = (0.30, 0.85, 1.00, 1)
COL_NEON_MAGENTA= (1.00, 0.18, 0.55, 1)
COL_NEON_PURPLE = (0.55, 0.25, 1.00, 1)
COL_MIRROR_BLUE = (0.06, 0.20, 0.45, 1)    # vidrio espejo azul base
COL_MIRROR_DARK = (0.04, 0.08, 0.18, 1)
COL_DARK_GLASS  = (0.04, 0.06, 0.10, 1)
COL_METAL_DARK  = (0.08, 0.09, 0.12, 1)
COL_METAL_LIGHT = (0.55, 0.58, 0.62, 1)
COL_CONCRETE    = (0.22, 0.23, 0.26, 1)
COL_LOGO_WHITE  = (0.95, 0.97, 1.00, 1)
COL_WARM_LED    = (1.00, 0.78, 0.35, 1)
COL_TEAL        = (0.10, 0.85, 0.75, 1)     # acento turquesa
COL_PINK        = (1.00, 0.40, 0.75, 1)     # acento rosado

_mat_cache = {}

def _rgb(color_rgba):
    """Convierte (r,g,b,a) → (r,g,b) para luces/sun de Blender."""
    return (color_rgba[0], color_rgba[1], color_rgba[2])

# ╔════════════════════════════════════════════════════════════════════╗
# ║ UTILIDADES                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def make_material(name, base_color, roughness=0.5, metallic=0.0,
                  emissive=None, emissive_strength=0.0, alpha=1.0,
                  ior=1.45, transmission=0.0):
    """Crea un material PBR con nodos Principled BSDF."""
    if name in _mat_cache:
        return _mat_cache[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in nodes:
        nodes.remove(n)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["IOR"].default_value = ior
    if transmission > 0:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha

    if emissive is not None:
        bsdf.inputs["Emission Color"].default_value = emissive
        bsdf.inputs["Emission Strength"].default_value = emissive_strength

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    _mat_cache[name] = mat
    return mat


def make_mirror_glass(name, tint=COL_MIRROR_BLUE, roughness=0.05):
    """Vidrio espejo azul: alta metalness, baja rugosidad, tint azul."""
    return make_material(name, tint, roughness=roughness, metallic=0.95,
                         ior=1.6)


def make_emissive(name, color, strength=5.0):
    return make_material(name, color, 0.3, 0.0, color, strength)


def assign(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def add_box(name, w, h, d, location=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w, h, d)
    return obj


def add_cylinder(name, r, h, location=(0,0,0), vertices=32, rot_x=0):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=h, vertices=vertices, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if rot_x:
        obj.rotation_euler = (math.radians(rot_x), 0, 0)
    return obj


def add_bevel(obj, width=0.02, segments=2):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'


def add_uv_sphere(name, r, location=(0,0,0), segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location,
                                          segments=segments, ring_count=rings)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_torus(name, major_r, minor_r, location=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        location=location, major_segments=64, minor_segments=24)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_cone(name, r1, r2, h, location=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cone_add(
        radius1=r1, radius2=r2, depth=h, vertices=vertices,
        location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj


# ╔════════════════════════════════════════════════════════════════════╗
# ║ LIMPIAR ESCENA                                                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(73)  # semilla épica


# ╔════════════════════════════════════════════════════════════════════╗
# ║ TERRENO Y CALLES (más grandes)                                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_ground():
    """Plaza expandida + calles con líneas + pasto perimetral."""
    # Plaza central (más grande)
    plaza = add_box("Plaza", 120, 120, 0.2, location=(0, 0, -0.1))
    assign(plaza, make_material("PlazaMat",
        (0.08, 0.08, 0.11, 1), roughness=0.35, metallic=0.0))

    # Avenida horizontal (frente al observador) — más ancha
    ave_h = add_box("AvenidaH", 120, 14, 0.05, location=(0, 35, 0.01))
    assign(ave_h, make_material("AsfaltoMat",
        (0.06, 0.06, 0.08, 1), roughness=0.85))

    # Avenida vertical (izquierda)
    ave_v = add_box("AvenidaV", 14, 120, 0.05, location=(-45, 0, 0.01))
    assign(ave_v, make_material("AsfaltoMat",
        (0.06, 0.06, 0.08, 1), roughness=0.85))

    # Líneas centrales de las avenidas (pintura amarilla emisiva)
    for y in (33, 37):
        ln = add_box(f"LineaH_{y}", 120, 0.2, 0.06, location=(0, y, 0.05))
        assign(ln, make_emissive(f"LineaMat_{y}",
                                  (1.0, 0.85, 0.10, 1), 1.5))

    # Pasto perimetral más grande
    grass = add_box("Pasto", 150, 150, 0.02, location=(0, 0, -0.15))
    assign(grass, make_material("PastoMat",
        (0.03, 0.10, 0.05, 1), roughness=0.95))

    # Aceras elevadas con luz LED inferior alrededor de la plaza
    for side in (-1, 1):
        for axis in ('x', 'y'):
            if axis == 'x':
                curb = add_box(f"Curb_{axis}_{side}", 120, 0.5, 0.15,
                               location=(0, side * 30, 0.05))
            else:
                curb = add_box(f"Curb_{axis}_{side}", 0.5, 60, 0.15,
                               location=(side * 30, 0, 0.05))
            assign(curb, make_emissive(f"CurbMat_{axis}_{side}",
                                        COL_NEON_CYAN, 3.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ TORRE HQ AGUITECH (más alta y dramática)                           ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_hq_tower():
    """Torre principal con logo 'A' gigante y pantallas LED."""
    base_x, base_y = -12, -12
    w, d = 10, 10

    # Base (zócalo)
    base = add_box("HQ_Base", w+0.8, d+0.8, 3, location=(base_x, base_y, 1.5))
    assign(base, make_material("HQ_BaseMat",
        COL_METAL_DARK, 0.4, 0.7,
        COL_NEON_BLUE, 1.5))
    add_bevel(base, 0.05, 3)

    # Tronco principal (4 secciones para más drama)
    sections = [
        (w,    d,    18, 12, COL_MIRROR_BLUE),     # sección 1: espejo azul
        (w-0.3, d-0.3, 22, 32, COL_MIRROR_DARK),  # sección 2: espejo más oscuro
        (w-0.8, d-0.8, 20, 54, COL_MIRROR_BLUE),  # sección 3: vuelve a azul claro
        (w-1.5, d-1.5, 16, 72, COL_METAL_DARK),   # sección 4: remate metálico
    ]
    for i, (sw, sd, sh, z, color) in enumerate(sections):
        sec = add_box(f"HQ_Sec{i+1}", sw, sd, sh, location=(base_x, base_y, z))
        # Vidrio espejo azul con alta metalness
        assign(sec, make_material(f"HQ_Sec{i+1}Mat",
            color, 0.08, 0.95,    # mirror
            COL_NEON_BLUE, 0.8))
        add_bevel(sec, 0.02, 3)

    # Franjas LED horizontales entre secciones
    for z in (11.95, 31.95, 53.95, 71.95):
        band = add_box(f"HQ_Band_{z}", w+0.7, d+0.7, 0.2,
                       location=(base_x, base_y, z))
        assign(band, make_emissive(f"HQ_BandMat_{z}", COL_NEON_CYAN, 10.0))

    # Logo "A" gigante (más alto y ancho)
    a_color = COL_LOGO_WHITE
    logo_z = 88
    # Pierna izquierda
    leg_l = add_box("HQ_A_Left", 0.7, 0.25, 11,
                    location=(base_x-2.0, base_y+d/2+0.05, logo_z))
    leg_l.rotation_euler = (0, 0, math.radians(-12))
    assign(leg_l, make_emissive("LogoA_Mat", a_color, 15.0))

    # Pierna derecha
    leg_r = add_box("HQ_A_Right", 0.7, 0.25, 11,
                    location=(base_x+2.0, base_y+d/2+0.05, logo_z))
    leg_r.rotation_euler = (0, 0, math.radians(12))
    assign(leg_r, make_emissive("LogoA_Mat2", a_color, 15.0))

    # Travesaño
    cross = add_box("HQ_A_Cross", 3.5, 0.25, 0.8,
                    location=(base_x, base_y+d/2+0.05, logo_z - 4))
    assign(cross, make_emissive("LogoA_CrossMat", a_color, 15.0))

    # Punta superior (antena alta con luz)
    antenna = add_cylinder("HQ_Antenna", 0.1, 12, location=(base_x, base_y, 82))
    assign(antenna, make_emissive("AntennaMat", COL_NEON_CYAN, 12.0))
    ant_tip = add_uv_sphere("HQ_AntennaTip", 0.4, (base_x, base_y, 88))
    assign(ant_tip, make_emissive("AntennaTipMat", COL_WARM_LED, 20.0))

    # 3 pantallas LED publicitarias (en caras del cubo)
    screens = [
        ("HQ_Screen_S", 0.1, w-0.5, 11, base_x, base_y-d/2-0.05, 35),  # sur
        ("HQ_Screen_W", d-0.5, 0.1, 11, base_x-w/2-0.05, base_y, 35),  # oeste
        ("HQ_Screen_N", 0.1, w-0.5, 11, base_x, base_y+d/2+0.05, 35),  # norte
    ]
    for name, sw, sd, sh, sx, sy, sz in screens:
        screen = add_box(name, sw, sd, sh, location=(sx, sy, sz))
        col = random.choice([COL_NEON_MAGENTA, COL_NEON_CYAN, COL_NEON_PURPLE])
        assign(screen, make_emissive(f"{name}Mat", col, 7.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ EDIFICIO SATÉLITE — VERSIÓN ESPEJO AZUL                            ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_satellite_tower(name, x, y, w, d, h, led_color=COL_NEON_BLUE,
                          with_logo=False, logo_height=None,
                          with_screen=False):
    """Rascacielos con vidrio espejo azul + ventanas emisivas + banda LED.
    OPTIMIZADO: usa planos con textura procedural de rejilla en vez de
    cientos de cubos individuales.
    """
    # Cuerpo principal — espejo azul reflectivo
    body = add_box(f"{name}_Body", w, d, h, location=(x, y, h/2))
    tint = random.choice([COL_MIRROR_BLUE, COL_MIRROR_DARK,
                          (0.05, 0.15, 0.40, 1),
                          (0.08, 0.25, 0.50, 1)])
    assign(body, make_material(f"{name}_Mat",
        tint, 0.08, 0.92,
        led_color, 0.5))
    add_bevel(body, 0.015, 2)

    # Plafones emisivos en 2 caras (norte y este) con rejilla procedural
    # Cada plafón es 1 solo plano que parece muchas ventanas
    for face_name, dx, dy, dw, dd in [
        ("N", 0, d/2 + 0.02, w*0.95, 0.05),   # norte
        ("E", w/2 + 0.02, 0, 0.05, d*0.95),   # este
    ]:
        panel = add_box(f"{name}_Panel_{face_name}", dw, dd, h*0.92,
                         location=(x + dx, y + dy, h*0.5))
        col = random.choice([led_color, COL_NEON_CYAN, COL_NEON_MAGENTA,
                              COL_TEAL, COL_WARM_LED, COL_PINK])
        assign(panel, make_emissive(f"{name}_PanelMat_{face_name}",
                                     col, random.uniform(3.5, 6.0)))

    # Banda LED superior
    top_band = add_box(f"{name}_TopBand", w+0.2, d+0.2, 0.2,
                       location=(x, y, h - 0.1))
    assign(top_band, make_emissive(f"{name}_TopBandMat",
                                   led_color, 10.0))

    # Antena con luz
    if h > 12:
        ant = add_cylinder(f"{name}_Antenna", 0.05, h*0.15,
                           location=(x, y, h + h*0.075))
        assign(ant, make_emissive(f"{name}_AntMat",
                                   random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                  COL_NEON_PURPLE]),
                                   random.uniform(5.0, 8.0)))
        tip = add_uv_sphere(f"{name}_AntTip", 0.2,
                            location=(x, y, h + h*0.15))
        assign(tip, make_emissive(f"{name}_AntTipMat",
                                   COL_WARM_LED, 18.0))

    # Logo opcional "A"
    if with_logo:
        logo_z = logo_height or h * 0.55
        size = h * 0.20
        leg_l = add_box(f"{name}_A_Left", 0.35, 0.12, size,
                        location=(x - w*0.25, y + d/2 + 0.06, logo_z))
        leg_l.rotation_euler = (0, 0, math.radians(-12))
        assign(leg_l, make_emissive(f"{name}_LogoMat", COL_LOGO_WHITE, 9.0))

        leg_r = add_box(f"{name}_A_Right", 0.35, 0.12, size,
                        location=(x + w*0.25, y + d/2 + 0.06, logo_z))
        leg_r.rotation_euler = (0, 0, math.radians(12))
        assign(leg_r, make_emissive(f"{name}_LogoMat2", COL_LOGO_WHITE, 9.0))

        cross = add_box(f"{name}_A_Cross", w*0.55, 0.12, 0.4,
                        location=(x, y + d/2 + 0.06, logo_z - size*0.30))
        assign(cross, make_emissive(f"{name}_LogoCross",
                                     COL_LOGO_WHITE, 9.0))

    # Pantalla LED publicitaria (opcional)
    if with_screen:
        screen = add_box(f"{name}_Screen", w*0.7, 0.05, h*0.20,
                         location=(x, y - d/2 - 0.03, h*0.45))
        assign(screen, make_emissive(f"{name}_ScreenMat",
                                      random.choice([COL_NEON_MAGENTA,
                                                     COL_NEON_CYAN,
                                                     COL_PINK]),
                                      6.0))


def build_satellite_district():
    """22 rascacielos: anillo interno + externo + skyline lejano."""
    # Anillo interno (más cerca de HQ)
    inner_ring = [
        ( 18, -12, 5,  5, 28, COL_NEON_BLUE,   True,  True),   # logo + screen
        ( 30, -15, 4,  4, 22, COL_NEON_CYAN,   False, False),
        ( 40,  -8, 6,  5, 32, COL_NEON_MAGENTA, True,  True),
        (-32, -18, 5,  5, 26, COL_NEON_PURPLE,  False, True),
        (-38,  12, 4,  4, 20, COL_NEON_BLUE,   False, False),
        (-40,  25, 6,  4, 30, COL_NEON_CYAN,    True,  False),
    ]
    for (x, y, w, d, h, col, logo, screen) in inner_ring:
        build_satellite_tower(f"Inner_{x}_{y}", x, y, w, d, h, col,
                              with_logo=logo, with_screen=screen)

    # Anillo medio
    mid_ring = [
        ( 22,  35, 5,  5, 26, COL_NEON_BLUE,   False, True),
        (-22,  40, 4,  4, 22, COL_NEON_CYAN,   True,  False),
        ( 50, -25, 4,  5, 28, COL_NEON_PURPLE,  True,  True),
        (-50, -28, 5,  4, 30, COL_NEON_MAGENTA, False, True),
        ( 50,  20, 5,  5, 26, COL_NEON_CYAN,   True,  False),
        (-48,  35, 4,  5, 24, COL_NEON_BLUE,   False, True),
    ]
    for (x, y, w, d, h, col, logo, screen) in mid_ring:
        build_satellite_tower(f"Mid_{x}_{y}", x, y, w, d, h, col,
                              with_logo=logo, with_screen=screen)

    # Anillo externo (skyline lejano, más alto y dramático)
    outer_ring = [
        ( 60, -45, 5,  5, 38, COL_NEON_BLUE,    True,  False),
        (-60, -50, 6,  5, 42, COL_NEON_CYAN,    True,  True),
        ( 65,  45, 5,  5, 36, COL_NEON_MAGENTA, False, True),
        (-65,  50, 4,  5, 40, COL_NEON_PURPLE,  True,  True),
        ( 50,  60, 5,  4, 32, COL_NEON_BLUE,    False, False),
        (-50,  60, 4,  5, 34, COL_NEON_CYAN,    True,  False),
        ( 75,   0, 4,  4, 28, COL_NEON_MAGENTA, False, True),
        (-72,   0, 5,  4, 30, COL_NEON_PURPLE,  True,  False),
        ( 35, -60, 4,  4, 26, COL_NEON_BLUE,    False, False),
        (-35, -60, 5,  4, 28, COL_NEON_CYAN,    True,  False),
    ]
    for (x, y, w, d, h, col, logo, screen) in outer_ring:
        build_satellite_tower(f"Outer_{x}_{y}", x, y, w, d, h, col,
                              with_logo=logo, with_screen=screen)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ SKYBRIDGE DOBLE                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_skybridge():
    """Puente elevado entre HQ y torre Inner_18_-12."""
    # Viga estructural
    beam = add_box("Skybridge", 32, 2.5, 1.5, location=(3, -12, 18))
    assign(beam, make_material("SkybridgeMat",
        COL_METAL_LIGHT, 0.3, 0.9,
        COL_NEON_CYAN, 1.2))
    add_bevel(beam, 0.05, 3)

    # Pasarela de vidrio
    floor = add_box("SkybridgeFloor", 31.5, 2.3, 0.12, location=(3, -12, 17.3))
    assign(floor, make_material("SkyFloorMat",
        (0.04, 0.10, 0.22, 1), 0.15, 0.0,
        COL_NEON_CYAN, 2.5))

    # Barandillas LED a los lados
    for sign in (-1.3, 1.3):
        rail = add_box(f"SkybridgeRail_{sign}", 31.5, 0.1, 0.7,
                       location=(3, -12 + sign, 18.6))
        assign(rail, make_emissive(f"SkyRailMat_{sign}",
                                    COL_NEON_BLUE, 8.0))

    # Pilares de soporte
    for px in (-12, 3, 18):
        pil = add_cylinder(f"SkybridgePillar_{px}", 0.5, 18,
                           location=(px, -12, 9))
        assign(pil, make_material("PillarMat",
            COL_CONCRETE, 0.7, 0.0,
            COL_NEON_BLUE, 0.6))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ FUENTE CENTRAL — VERSIÓN ÉPICA                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_central_fountain():
    """Fuente GRANDOTA con múltiples chorros y anillos concéntricos."""
    cx, cy = 0, 0

    # ── Base escalonada: 5 niveles (más grande) ──
    base_levels = [
        (8.0, 0.5, 0.25),
        (6.8, 0.5, 0.65),
        (5.6, 0.5, 1.05),
        (4.4, 0.5, 1.45),
        (3.2, 0.5, 1.85),
    ]
    for i, (r, h, z) in enumerate(base_levels):
        ring = add_cylinder(f"FountainRing{i}", r, h,
                            location=(cx, cy, z), vertices=64)
        assign(ring, make_material(f"FountainRingMat{i}",
            COL_METAL_DARK, 0.20, 0.85,
            random.choice([COL_NEON_BLUE, COL_NEON_CYAN, COL_NEON_MAGENTA]),
            3.0))

    # ── Piscina de agua principal (disco) ──
    pool = add_cylinder("FountainPool", 3.1, 0.08,
                        location=(cx, cy, 2.20), vertices=64)
    assign(pool, make_material("WaterMat",
        (0.02, 0.12, 0.30, 1), 0.05, 0.0,
        COL_NEON_CYAN, 4.0))

    # ── Anillos concéntricos emisivos en el agua ──
    for i, (rad, col) in enumerate([
        (2.5, COL_NEON_BLUE),
        (2.0, COL_NEON_CYAN),
        (1.5, COL_NEON_MAGENTA),
        (1.0, COL_NEON_PURPLE),
    ]):
        ring = add_torus(f"WaterRing_{i}", rad, 0.04,
                          location=(cx, cy, 2.22))
        ring.rotation_euler = (math.radians(90), 0, 0)
        assign(ring, make_emissive(f"WaterRingMat_{i}", col, 8.0))

    # ── Chorro CENTRAL gigante ──
    jet_main = add_cone("FountainJetMain", 0.25, 0.08, 14,
                         location=(cx, cy, 9), vertices=24)
    assign(jet_main, make_material("WaterJetMainMat",
        (0.50, 0.85, 1.0, 0.75), 0.08, 0.0,
        COL_NEON_CYAN, 5.0))

    # ── 8 chorros secundarios en círculo (radio 2.5) ──
    for i in range(8):
        ang = math.radians(i * 45)
        jx = cx + math.cos(ang) * 2.5
        jy = cy + math.sin(ang) * 2.5
        jet = add_cone(f"JetSec_{i}", 0.15, 0.04, 8,
                       location=(jx, jy, 4.8), vertices=16)
        # Inclinar hacia afuera
        jet.rotation_euler = (0, 0, ang + math.radians(90))
        col = random.choice([COL_NEON_CYAN, COL_NEON_BLUE,
                              COL_NEON_MAGENTA, COL_TEAL])
        assign(jet, make_material(f"JetSecMat_{i}",
            (0.50, 0.85, 1.0, 0.65), 0.08, 0.0,
            col, 4.5))

    # ── 16 chorros pequeños exteriores (radio 4.5) ──
    for i in range(16):
        ang = math.radians(i * 22.5)
        jx = cx + math.cos(ang) * 4.5
        jy = cy + math.sin(ang) * 4.5
        jet = add_cone(f"JetOuter_{i}", 0.10, 0.03, 5,
                       location=(jx, jy, 3.0), vertices=12)
        jet.rotation_euler = (0, 0, ang + math.radians(90))
        col = random.choice([COL_NEON_CYAN, COL_NEON_BLUE, COL_NEON_MAGENTA])
        assign(jet, make_material(f"JetOuterMat_{i}",
            (0.50, 0.85, 1.0, 0.55), 0.10, 0.0,
            col, 3.5))

    # ── Columnas estructurales decorativas (4) ──
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        px = cx + math.cos(ang) * 5.5
        py = cy + math.sin(ang) * 5.5
        col = add_cylinder(f"FountainColumn_{i}", 0.30, 4.0,
                           location=(px, py, 2.5), vertices=12)
        assign(col, make_material(f"FountainColumnMat_{i}",
            COL_METAL_LIGHT, 0.25, 0.85,
            COL_NEON_BLUE, 1.5))
        # LED superior en cada columna
        led = add_uv_sphere(f"ColumnLed_{i}", 0.20,
                             location=(px, py, 4.6))
        col_led = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                  COL_NEON_PURPLE, COL_WARM_LED])
        assign(led, make_emissive(f"ColumnLedMat_{i}", col_led, 12.0))

    # ── Holograma del logo "A" GIGANTE flotando arriba ──
    holo_z = 16
    # Marco del holograma (cilindro semitransparente)
    holo_frame = add_cylinder("HoloFrame", 2.0, 0.05,
                              location=(cx, cy, holo_z - 1), vertices=32)
    assign(holo_frame, make_material("HoloFrameMat",
        (0.10, 0.30, 0.60, 0.25), 0.10, 0.0,
        COL_NEON_CYAN, 3.0))

    # Piernas A
    hol_l = add_box("Hol_A_L", 0.30, 0.15, 6,
                    location=(cx - 1.0, cy, holo_z))
    hol_l.rotation_euler = (0, 0, math.radians(-10))
    assign(hol_l, make_emissive("HolMat", COL_NEON_CYAN, 18.0))

    hol_r = add_box("Hol_A_R", 0.30, 0.15, 6,
                    location=(cx + 1.0, cy, holo_z))
    hol_r.rotation_euler = (0, 0, math.radians(10))
    assign(hol_r, make_emissive("HolMat2", COL_NEON_CYAN, 18.0))

    hol_c = add_box("Hol_A_C", 2.5, 0.15, 0.6,
                    location=(cx, cy, holo_z - 2.5))
    assign(hol_c, make_emissive("HolMat3", COL_NEON_CYAN, 18.0))

    # Anillos LED emisivos a varias alturas (efecto holográfico)
    for z in (10, 12, 14, 16, 18):
        ring = add_torus(f"HoloRing_{z}", 2.2, 0.08,
                          location=(cx, cy, z))
        ring.rotation_euler = (math.radians(90), 0, 0)
        col_ring = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                   COL_NEON_BLUE, COL_NEON_PURPLE])
        assign(ring, make_emissive(f"HoloRingMat_{z}",
                                    col_ring, 12.0))

    # ── Puntos de luz puntuales en los bordes de la fuente ──
    for i in range(24):
        ang = math.radians(i * 15)
        bx = cx + math.cos(ang) * 7.8
        by = cy + math.sin(ang) * 7.8
        led = add_uv_sphere(f"FountainLed_{i}", 0.15,
                             location=(bx, by, 0.5))
        col_led = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                  COL_NEON_BLUE, COL_WARM_LED])
        assign(led, make_emissive(f"FountainLedMat_{i}",
                                    col_led, 10.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ROBOTS AUTÓNOMOS DE DELIVERY (3)                                   ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_delivery_robot(x, y, suffix=""):
    """Pequeño robot tipo delivery."""
    z = 0.5
    s = suffix  # alias local

    # Cuerpo principal
    body = add_box(f"RobotBody{suffix}", 1.5, 1.1, 1.4, location=(x, y, z+1.1))
    assign(body, make_material(f"RobotBodyMat{suffix}",
        COL_LOGO_WHITE, 0.2, 0.5,
        random.choice([COL_NEON_CYAN, COL_NEON_BLUE, COL_NEON_MAGENTA]),
        1.5))
    add_bevel(body, 0.15, 4)

    # Cabeza con cámara
    head = add_box(f"RobotHead{suffix}", 1.0, 0.9, 0.6,
                   location=(x, y - 0.45, z+2.0))
    assign(head, make_material(f"RobotHeadMat{suffix}",
        (0.10, 0.10, 0.12, 1), 0.3, 0.6,
        COL_NEON_BLUE, 2.0))

    # Ojos LED
    for ox in (-0.30, 0.30):
        eye = add_box(f"RobotEye{suffix}_{ox}", 0.18, 0.05, 0.18,
                      location=(x + ox, y - 0.95, z + 2.0))
        assign(eye, make_emissive(f"RobotEyeMat{suffix}_{ox}",
                                   COL_NEON_CYAN, 18.0))

    # Logo Aguitech en el cuerpo
    logo = add_box(f"RobotLogo{suffix}", 0.6, 0.05, 0.4,
                   location=(x, y + 0.6, z + 1.1))
    assign(logo, make_emissive(f"RobotLogoMat{suffix}",
                                 COL_NEON_BLUE, 10.0))

    # Caja de delivery encima
    pkg = add_box(f"RobotPkg{suffix}", 1.0, 0.8, 0.6,
                  location=(x, y + 0.3, z + 2.2))
    assign(pkg, make_material(f"RobotPkgMat{suffix}",
        COL_NEON_BLUE, 0.3, 0.3,
        COL_NEON_CYAN, 1.0))
    add_bevel(pkg, 0.05, 2)

    # Ruedas (4 toroides)
    for wx, wy in ((-0.65, -0.45), (0.65, -0.45), (-0.65, 0.45), (0.65, 0.45)):
        wheel = add_torus(f"RobotWheel{suffix}_{wx}_{wy}", 0.28, 0.13,
                          location=(x + wx, y + wy, z + 0.1))
        wheel.rotation_euler = (math.radians(90), 0, 0)
        assign(wheel, make_material(f"RobotWheelMat{suffix}_{wx}",
            COL_METAL_DARK, 0.5, 0.8))


def build_all_robots():
    """3 robots en distintas posiciones."""
    suffix = "_A"
    build_delivery_robot(-22, 41, suffix)
    suffix = "_B"
    build_delivery_robot(38, 41, suffix)
    suffix = "_C"
    build_delivery_robot(-30, -18, suffix)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ DRONES VOLANDO (12)                                                ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_drones():
    """12 drones en distintas alturas."""
    drones_pos = [
        # Posición (x, y, z)
        (-15, -15, 22), (15, 5, 26), (-12, 15, 30),
        (25, 25, 24),  (-25, -25, 32), (20, -30, 28),
        (35, -15, 35), (-35, 25, 30), (10, 35, 22),
        (-10, 40, 28), (40, -35, 26), (-40, -40, 33),
    ]
    for i, (x, y, z) in enumerate(drones_pos):
        # Cuerpo
        body = add_uv_sphere(f"Drone{i}_Body", 0.35,
                             location=(x, y, z))
        assign(body, make_material(f"Drone{i}_Mat",
            COL_METAL_DARK, 0.4, 0.6,
            random.choice([COL_NEON_BLUE, COL_NEON_CYAN, COL_NEON_MAGENTA]),
            1.5))

        # Brazos en X con rotores
        for ang in (45, 135, 225, 315):
            rad = math.radians(ang)
            bx = x + math.cos(rad) * 1.0
            by = y + math.sin(rad) * 1.0
            arm = add_box(f"Drone{i}_Arm_{ang}", 1.2, 0.06, 0.06,
                          location=(bx, by, z))
            arm.rotation_euler = (0, 0, rad)
            assign(arm, make_material(f"Drone{i}_ArmMat",
                COL_METAL_DARK, 0.3, 0.8))

            rotor = add_torus(f"Drone{i}_Rotor_{ang}", 0.42, 0.04,
                              location=(bx, by, z))
            rotor.rotation_euler = (math.radians(90), 0, 0)
            assign(rotor, make_material(f"Drone{i}_RotorMat",
                (0.3, 0.3, 0.35, 1), 0.4, 0.5))

        # LED inferior potente
        led = add_uv_sphere(f"Drone{i}_LED", 0.12,
                            location=(x, y, z - 0.4))
        assign(led, make_emissive(f"Drone{i}_LEDMat",
                                   random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                  COL_NEON_BLUE]),
                                   30.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ VIADUCTO DOBLE                                                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_viaduct():
    """Autopista elevada cruzando por detrás de la plaza."""
    # Vía principal (alta)
    road_hi = add_box("ViaductRoadHi", 130, 5, 0.5, location=(0, -45, 8))
    assign(road_hi, make_material("ViaductRoadMat",
        (0.08, 0.08, 0.10, 1), 0.7))

    # Barandas LED
    for side in (-2.55, 2.55):
        rail = add_box(f"ViaductRailHi_{side}", 130, 0.12, 0.7,
                       location=(0, -45 + side, 8.85))
        assign(rail, make_emissive(f"ViaductRailHiMat_{side}",
                                    COL_NEON_MAGENTA, 6.0))

    # Pilares cada 8m
    for px in range(-60, 61, 8):
        pil = add_cylinder(f"ViaductPilHi_{px}", 0.55, 8,
                           location=(px, -45, 4))
        assign(pil, make_material("ViaductPilMat",
            COL_CONCRETE, 0.7, 0.0,
            COL_NEON_BLUE, 0.4))

    # Coches en viaducto alto (6 coches)
    cars = [
        (-50, -45, COL_NEON_BLUE),
        (-30, -45, COL_NEON_MAGENTA),
        (-10, -45, COL_NEON_CYAN),
        ( 15, -45, COL_NEON_PURPLE),
        ( 35, -45, COL_NEON_BLUE),
        ( 55, -45, COL_NEON_CYAN),
    ]
    for i, (cx, cy, body_col) in enumerate(cars):
        car = add_box(f"CarHi{i}", 1.0, 1.7, 0.9, location=(cx, cy, 8 + 0.45))
        assign(car, make_material(f"CarHi{i}Mat",
            body_col, 0.2, 0.7,
            body_col, 0.5))
        # Faros delanteros
        for hy in (-0.5, 0.5):
            hl = add_uv_sphere(f"CarHi{i}_HL_{hy}", 0.10,
                                location=(cx + 0.55, cy + hy, 8 + 0.5))
            assign(hl, make_emissive(f"CarHi{i}_HLMat_{hy}",
                                      COL_WARM_LED, 35.0))
        # Luces traseras rojas
        for hy in (-0.5, 0.5):
            tl = add_uv_sphere(f"CarHi{i}_TL_{hy}", 0.08,
                                location=(cx - 0.55, cy + hy, 8 + 0.5))
            assign(tl, make_emissive(f"CarHi{i}_TLMat_{hy}",
                                      (1.0, 0.1, 0.1, 1), 18.0))

    # Vía baja (peatonal / servicio) — más baja y con tráfico lento
    road_lo = add_box("ViaductRoadLo", 130, 4, 0.3, location=(0, -30, 4))
    assign(road_lo, make_material("ViaductRoadLoMat",
        (0.10, 0.10, 0.12, 1), 0.8))

    # Coches en viaducto bajo (4)
    for i, (cx, cy, body_col) in enumerate([
        (-40, -30, COL_NEON_CYAN),
        (-5, -30, COL_NEON_MAGENTA),
        (25, -30, COL_NEON_PURPLE),
        (50, -30, COL_NEON_BLUE),
    ]):
        car = add_box(f"CarLo{i}", 0.9, 1.5, 0.8, location=(cx, cy, 4 + 0.4))
        assign(car, make_material(f"CarLo{i}Mat",
            body_col, 0.2, 0.7,
            body_col, 0.5))
        # Faros
        for hy in (-0.45, 0.45):
            hl = add_uv_sphere(f"CarLo{i}_HL_{hy}", 0.10,
                                location=(cx + 0.5, cy + hy, 4 + 0.45))
            assign(hl, make_emissive(f"CarLo{i}_HLMat_{hy}",
                                      COL_WARM_LED, 30.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ÁRBOLES NEÓN (16)                                                  ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_neon_trees():
    """16 árboles tech con copas emisivas."""
    positions = [
        (-22, -22), (-22, -16), (-16, -22),
        ( 50, -22), ( 50, -16),
        (-22,  52), (-16,  52),
        ( 50,  52), ( 45,  52),
        (-50,  -8), (-50,   0),
        ( 60,   0), ( 60,   8),
        (-10, -45), ( 10, -45),
        (  0,  52),
    ]
    for i, (x, y) in enumerate(positions):
        # Tronco más alto
        trunk = add_cylinder(f"Tree{i}_Trunk", 0.18, 3.5,
                            location=(x, y, 1.75), vertices=8)
        assign(trunk, make_material(f"Tree{i}_TrunkMat",
            (0.06, 0.05, 0.04, 1), 0.8, 0.0,
            COL_NEON_CYAN, 0.4))

        # Copa emisiva más grande
        col = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                              COL_NEON_PURPLE, COL_NEON_BLUE, COL_TEAL])
        crown = add_uv_sphere(f"Tree{i}_Crown", 1.6,
                               location=(x, y, 4.5))
        crown.scale = (1, 1, 0.7)
        assign(crown, make_emissive(f"Tree{i}_CrownMat",
                                     col, 3.5))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ILUMINACIÓN (más rica)                                             ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_lighting():
    """Iluminación cinematográfica de atardecer cyberpunk v3."""
    # Limpiar luces previas
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.select_set(True)
            bpy.ops.object.delete()

    # Sol bajo (tono cálido del atardecer)
    bpy.ops.object.light_add(type='SUN',
                              location=(25, 35, 30),
                              rotation=(math.radians(60),
                                        math.radians(15), 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 2.5
    sun.data.color = _rgb(COL_WARM_LED)
    sun.data.specular_factor = 0.5

    # Ambient point elevado (simula hemi)
    bpy.ops.object.light_add(type='POINT',
                              location=(0, 0, 80))
    hemi = bpy.context.active_object
    hemi.name = "HemiAmbient"
    hemi.data.energy = 1200
    hemi.data.color = _rgb((0.4, 0.4, 0.7))

    # Foco dramático sobre el HQ
    bpy.ops.object.light_add(type='SPOT',
                              location=(-30, -35, 50),
                              rotation=(math.radians(55),
                                        math.radians(40), 0))
    key = bpy.context.active_object
    key.name = "KeySpot"
    key.data.energy = 1500
    key.data.color = _rgb((0.6, 0.8, 1.0))
    key.data.spot_size = math.radians(50)
    key.data.spot_blend = 0.4

    # Foco sobre la fuente
    bpy.ops.object.light_add(type='SPOT',
                              location=(0, -25, 30),
                              rotation=(math.radians(70),
                                        math.radians(0), 0))
    ftn = bpy.context.active_object
    ftn.name = "FountainSpot"
    ftn.data.energy = 800
    ftn.data.color = _rgb((0.4, 0.7, 1.0))
    ftn.data.spot_size = math.radians(35)

    # Rim lights neón
    for i, (loc, col) in enumerate([
        ((45, 35, 35), (1.0, 0.3, 0.7)),
        ((-45, 40, 30), (0.3, 0.6, 1.0)),
        ((0, -55, 30), (0.8, 0.4, 1.0)),
        ((60, -25, 35), (0.4, 0.9, 0.9)),
        ((-60, -10, 35), (1.0, 0.4, 0.8)),
    ]):
        bpy.ops.object.light_add(type='AREA',
                                  location=loc,
                                  rotation=(math.radians(70), 0, 0))
        rim = bpy.context.active_object
        rim.name = f"RimLight{i}"
        rim.data.energy = 300
        rim.data.color = _rgb(col)
        rim.data.size = 12.0

    # Farolas LED en avenida (más cantidad)
    for fx in range(-50, 51, 8):
        bpy.ops.object.light_add(type='POINT',
                                  location=(fx, 42, 6))
        lamp = bpy.context.active_object
        lamp.name = f"Lamp_{fx}"
        lamp.data.energy = 100
        lamp.data.color = _rgb((1.0, 0.85, 0.55))

    # Focos adicionales en la fuente (luz subacuática)
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        lx = math.cos(ang) * 5
        ly = math.sin(ang) * 5
        bpy.ops.object.light_add(type='POINT',
                                  location=(lx, ly, 0.5))
        ul = bpy.context.active_object
        ul.name = f"UnderwaterLight_{i}"
        ul.data.energy = 200
        ul.data.color = _rgb(random.choice([COL_NEON_CYAN, COL_NEON_BLUE,
                                              COL_NEON_MAGENTA]))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ CÁMARA                                                             ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_camera():
    """Cámara cinematográfica — vista panorámica más amplia."""
    bpy.ops.object.camera_add(
        location=(55, -55, 35),
        rotation=(math.radians(50), 0, math.radians(45)))
    cam = bpy.context.active_object
    cam.name = "CinematicCamera"
    cam.data.lens = 32  # Gran angular
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.1
    cam.data.clip_end = 500
    bpy.context.scene.camera = cam
    return cam


# ╔════════════════════════════════════════════════════════════════════╗
# ║ FONDO / SKY                                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_sky_gradient():
    """Gradiente de cielo procedural: atardecer cyberpunk."""
    world = bpy.data.worlds.new("WorldAguitech_v3")
    bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    for n in nodes:
        nodes.remove(n)

    output = nodes.new("ShaderNodeOutputWorld")
    output.location = (300, 0)

    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.04, 0.05, 0.10, 1)
    bg.inputs["Strength"].default_value = 0.35

    gradient = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    tex_gradient = nodes.new("ShaderNodeTexGradient")
    tex_gradient.gradient_type = 'SPHERICAL'

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].color = (0.95, 0.45, 0.20, 1)   # naranja
    color_ramp.color_ramp.elements[1].color = (0.06, 0.08, 0.20, 1)   # azul oscuro
    mid = color_ramp.color_ramp.elements.new(0.5)
    mid.color = (0.55, 0.20, 0.50, 1)                                 # magenta

    links.new(gradient.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex_gradient.inputs["Vector"])
    links.new(tex_gradient.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], output.inputs["Surface"])


# ╔════════════════════════════════════════════════════════════════════╗
# ║ VOLUMÉTRICOS                                                       ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_volumetrics():
    scene = bpy.context.scene
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links

    volume = nodes.new("ShaderNodeVolumeScatter")
    volume.inputs["Color"].default_value = (0.10, 0.15, 0.30, 1)
    volume.inputs["Density"].default_value = 0.020
    volume.inputs["Anisotropy"].default_value = 0.5

    output = nodes.get("World Output")
    if output:
        try:
            links.new(volume.outputs["Volume"], output.inputs["Volume"])
        except Exception:
            pass


# ╔════════════════════════════════════════════════════════════════════╗
# ║ CONFIGURACIÓN DE RENDER                                            ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    try:
        scene.eevee.use_volumetric_lights = True
        scene.eevee.volumetric_light_clamp = 12
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = 1.0
        scene.eevee.bloom_threshold = 0.85
        scene.eevee.bloom_radius = 7.0
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 1.2
        scene.eevee.gtao_factor = 0.6
        scene.eevee.use_ssr = True
    except Exception:
        pass

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = RENDER_PATH
    scene.render.film_transparent = False

    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


# ╔════════════════════════════════════════════════════════════════════╗
# ║ EJECUCIÓN                                                          ║
# ╚════════════════════════════════════════════════════════════════════╝
try:
    safe_run("01 clear_scene", clear_scene)
    safe_run("02 build_sky_gradient", build_sky_gradient)
    safe_run("03 build_ground", build_ground)
    safe_run("04 build_hq_tower", build_hq_tower)
    safe_run("05 build_satellite_district", build_satellite_district)
    safe_run("06 build_skybridge", build_skybridge)
    safe_run("07 build_central_fountain", build_central_fountain)
    safe_run("08 build_all_robots", build_all_robots)
    safe_run("09 build_drones", build_drones)
    safe_run("10 build_viaduct", build_viaduct)
    safe_run("11 build_neon_trees", build_neon_trees)
    safe_run("12 build_lighting", build_lighting)
    safe_run("13 setup_camera", setup_camera)
    safe_run("14 setup_volumetrics", setup_volumetrics)
    safe_run("15 setup_render", setup_render)

    log("\n>>> Guardando .blend...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log(f">>> .blend guardado en {BLEND_PATH}")

    log("\n>>> Renderizando...")
    bpy.ops.render.render(write_still=True)
    log(f">>> Render guardado en {RENDER_PATH}")

    log("\n" + "=" * 70)
    log("AGUITECH CITY v3 — COMPLETADO")
    log("=" * 70)

except Exception:
    log(f"\nFATAL:\n{traceback.format_exc()}")
    raise
