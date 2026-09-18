"""
aguitech_city — Ciudad futurista corporativa Aguitech
=====================================================

Inspirado en la referencia: skyline nocturno cyberpunk, rascacielos con
pantallas LED azules/magentas, branding Aguitech omnipresente, drones,
robots autónomos, viaductos, fuente holográfica, skybridge conector.

Render  -> aguitech_city/imagenes/aguitech_city.png (4K cinematic)
Blend   -> aguitech_city/aguitech_city.blend

Composición:
  1. Torre HQ Aguitech (rascacielos flagship con logo "A" gigante)
  2. Edificios satélite (10 rascacielos con variación)
  3. Skybridge conector entre HQ y torre secundaria
  4. Plaza central con fuente holográfica
  5. Avenida con viaducto elevado y tráfico
  6. Robot de delivery autónomo
  7. Drones volando
  8. Iluminación neón azul/magenta volumétrica
  9. Skyline nocturno al atardecer (HDRI procedural)
"""

import bpy
import math
import os
import sys
import traceback
import random

LOG_FILE = "/tmp/aguitech_city.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")
        f.flush()

try:
    os.remove(LOG_FILE)
except FileNotFoundError:
    pass

log("=" * 70)
log("AGUITECH CITY — INICIANDO")
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
BLEND_PATH  = os.path.join(SCRIPT_DIR, "aguitech_city.blend")
RENDER_PATH = os.path.join(IMAGES_DIR, "aguitech_city.png")

# ╔════════════════════════════════════════════════════════════════════╗
# ║ PALETA AGUITECH                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
COL_NEON_BLUE   = (0.10, 0.55, 1.00, 1)   # azul corporativo Aguitech
COL_NEON_CYAN   = (0.30, 0.85, 1.00, 1)
COL_NEON_MAGENTA= (1.00, 0.18, 0.55, 1)
COL_NEON_PURPLE = (0.55, 0.25, 1.00, 1)
COL_DARK_GLASS  = (0.04, 0.06, 0.10, 1)
COL_METAL_DARK  = (0.08, 0.09, 0.12, 1)
COL_METAL_LIGHT = (0.55, 0.58, 0.62, 1)
COL_CONCRETE    = (0.22, 0.23, 0.26, 1)
COL_LOGO_WHITE  = (0.95, 0.97, 1.00, 1)
COL_WARM_LED    = (1.00, 0.78, 0.35, 1)

# Material cache to avoid duplicates
_mat_cache = {}

# ╔════════════════════════════════════════════════════════════════════╗
# ║ UTILIDADES                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def make_material(name, base_color, roughness=0.5, metallic=0.0,
                  emissive=None, emissive_strength=0.0, alpha=1.0):
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


def make_emissive(name, color, strength=5.0):
    """Material puramente emisivo (LED, neón, pantallas)."""
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


def add_cylinder(name, r, h, location=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=h, vertices=vertices, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_bevel(obj, width=0.02, segments=2):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'


def set_smooth(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()


# ╔════════════════════════════════════════════════════════════════════╗
# ║ LIMPIAR ESCENA                                                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(42)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ TERRENO Y CALLE                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_ground():
    """Plaza + calles con líneas + pasto perimetral."""
    # Plaza central (concreto oscuro pulido)
    plaza = add_box("Plaza", 80, 80, 0.2, location=(0, 0, -0.1))
    assign(plaza, make_material("PlazaMat",
        (0.10, 0.10, 0.13, 1), roughness=0.35, metallic=0.0))

    # Avenida horizontal (frente al observador)
    ave_h = add_box("AvenidaH", 80, 10, 0.05, location=(0, 25, 0.01))
    assign(ave_h, make_material("AsfaltoMat",
        (0.08, 0.08, 0.10, 1), roughness=0.85))

    # Avenida vertical (izquierda)
    ave_v = add_box("AvenidaV", 10, 80, 0.05, location=(-30, 0, 0.01))
    assign(ave_v, make_material("AsfaltoMat",
        (0.08, 0.08, 0.10, 1), roughness=0.85))

    # Líneas centrales de las avenidas (pintura amarilla)
    line_h1 = add_box("LineaH1", 80, 0.15, 0.06, location=(0, 23, 0.05))
    line_h2 = add_box("LineaH2", 80, 0.15, 0.06, location=(0, 27, 0.05))
    for ln in (line_h1, line_h2):
        assign(ln, make_material("LineaMat",
            (1.0, 0.85, 0.10, 1), 0.6, 0.0,
            (1.0, 0.85, 0.10, 1), 0.8))

    # Pasto perimetral (plaza grande con jardín)
    grass = add_box("Pasto", 100, 100, 0.02, location=(0, 0, -0.15))
    assign(grass, make_material("PastoMat",
        (0.04, 0.12, 0.06, 1), roughness=0.95))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ TORRE HQ AGUITECH (rascacielos flagship)                           ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_hq_tower():
    """Torre principal con logo 'A' gigante y pantallas LED."""
    base_x, base_y = -8, -8
    w, d = 8, 8

    # Base (zócalo con entramado de LED en los bordes)
    base = add_box("HQ_Base", w+0.5, d+0.5, 2, location=(base_x, base_y, 1))
    assign(base, make_material("HQ_BaseMat",
        COL_METAL_DARK, 0.4, 0.7,
        COL_NEON_BLUE, 1.5))
    add_bevel(base, 0.05, 3)

    # Tronco principal (segmentado en 3 secciones para variación)
    sections = [
        (w, d, 14, 8, COL_DARK_GLASS),         # sección 1: vidrio oscuro
        (w-0.4, d-0.4, 18, 22, COL_DARK_GLASS),# sección 2: más alta, vidrio
        (w-1.0, d-1.0, 16, 41, COL_METAL_DARK),# sección 3: remate metálico
    ]
    for i, (sw, sd, sh, z, color) in enumerate(sections):
        sec = add_box(f"HQ_Sec{i+1}", sw, sd, sh, location=(base_x, base_y, z))
        assign(sec, make_material(f"HQ_Sec{i+1}Mat",
            color, 0.15, 0.85,
            COL_NEON_BLUE, 0.6))
        add_bevel(sec, 0.02, 3)

    # Franjas LED horizontales entre secciones
    for z in (7.95, 21.95, 40.95):
        band = add_box(f"HQ_Band_{z}", w+0.6, d+0.6, 0.15,
                       location=(base_x, base_y, z))
        assign(band, make_emissive(f"HQ_BandMat_{z}", COL_NEON_CYAN, 8.0))

    # Logo "A" gigante (emisivo, una cara)
    # Construimos la "A" con prismas triangulares + travesaño
    a_color = COL_LOGO_WHITE

    # Pierna izquierda
    leg_l = add_box("HQ_A_Left", 0.5, 0.2, 8, location=(base_x-1.5, base_y+d/2+0.05, 50))
    leg_l.rotation_euler = (0, 0, math.radians(-10))
    assign(leg_l, make_emissive("LogoA_Mat", a_color, 12.0))

    # Pierna derecha
    leg_r = add_box("HQ_A_Right", 0.5, 0.2, 8, location=(base_x+1.5, base_y+d/2+0.05, 50))
    leg_r.rotation_euler = (0, 0, math.radians(10))
    assign(leg_r, make_emissive("LogoA_Mat2", a_color, 12.0))

    # Travesaño
    cross = add_box("HQ_A_Cross", 2.5, 0.2, 0.6,
                    location=(base_x, base_y+d/2+0.05, 46))
    assign(cross, make_emissive("LogoA_CrossMat", a_color, 12.0))

    # Punta superior (antena con luz)
    antenna = add_cylinder("HQ_Antenna", 0.08, 8, location=(base_x, base_y, 56))
    assign(antenna, make_emissive("AntennaMat", COL_NEON_CYAN, 10.0))
    ant_tip = add_uv_sphere("HQ_AntennaTip", 0.25, (base_x, base_y, 60))
    assign(ant_tip, make_emissive("AntennaTipMat", COL_WARM_LED, 15.0))

    # Pantalla LED publicitaria en una cara (lateral sur, mirando al sur)
    screen = add_box("HQ_Screen", w-1, 0.1, 8,
                     location=(base_x, base_y-d/2-0.05, 25))
    assign(screen, make_emissive("HQ_ScreenMat", COL_NEON_MAGENTA, 6.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ HELPERS GEOMETRÍA                                                  ║
# ╚════════════════════════════════════════════════════════════════════╝
def add_uv_sphere(name, r, location=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=location,
                                          segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_torus(name, major_r, minor_r, location=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_r, minor_radius=minor_r,
        location=location, major_segments=48, minor_segments=24)
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
# ║ EDIFICIOS SATÉLITE                                                 ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_satellite_tower(name, x, y, w, d, h, led_color=COL_NEON_BLUE,
                          with_logo=False, logo_height=None):
    """Rascacielos genérico con ventanas emisivas y banda LED superior."""
    # Cuerpo principal
    body = add_box(f"{name}_Body", w, d, h, location=(x, y, h/2))
    base_col = random.choice([
        COL_DARK_GLASS, COL_METAL_DARK,
        (0.06, 0.08, 0.12, 1),
        (0.10, 0.10, 0.14, 1),
    ])
    assign(body, make_material(f"{name}_Mat",
        base_col, 0.25, 0.7,
        led_color, 0.4))
    add_bevel(body, 0.015, 2)

    # Ventanas emisivas (rejilla de pequeños cubos en caras frontales)
    n_floors = max(3, int(h / 1.2))
    n_per_floor = max(2, int(w / 0.8))
    for f in range(n_floors):
        z = 0.5 + f * (h - 1) / n_floors
        for k in range(n_per_floor):
            x_off = -w/2 + (k + 0.5) * (w / n_per_floor)
            win = add_box(f"{name}_Win_{f}_{k}",
                          0.35, 0.05, 0.6,
                          location=(x + x_off, y + d/2 + 0.02, z))
            assign(win, make_emissive(
                f"{name}_WinMat_{f}_{k}",
                random.choices(
                    [led_color, COL_WARM_LED, COL_NEON_CYAN, COL_NEON_MAGENTA],
                    weights=[5, 1, 2, 1])[0],
                random.uniform(2.0, 6.0)))

    # Banda LED superior
    top_band = add_box(f"{name}_TopBand", w+0.2, d+0.2, 0.15,
                       location=(x, y, h - 0.1))
    assign(top_band, make_emissive(f"{name}_TopBandMat",
                                   led_color, 9.0))

    # Antena con luz
    if h > 15:
        ant = add_cylinder(f"{name}_Antenna", 0.04, h*0.12,
                           location=(x, y, h + h*0.06))
        assign(ant, make_emissive(f"{name}_AntMat", COL_NEON_CYAN, 6.0))

    # Logo opcional "A"
    if with_logo:
        logo_z = logo_height or h * 0.6
        leg_l = add_box(f"{name}_A_Left", 0.3, 0.12, h*0.18,
                        location=(x - w*0.2, y + d/2 + 0.05, logo_z))
        leg_l.rotation_euler = (0, 0, math.radians(-12))
        assign(leg_l, make_emissive(f"{name}_LogoMat", COL_LOGO_WHITE, 8.0))

        leg_r = add_box(f"{name}_A_Right", 0.3, 0.12, h*0.18,
                        location=(x + w*0.2, y + d/2 + 0.05, logo_z))
        leg_r.rotation_euler = (0, 0, math.radians(12))
        assign(leg_r, make_emissive(f"{name}_LogoMat2", COL_LOGO_WHITE, 8.0))

        cross = add_box(f"{name}_A_Cross", w*0.5, 0.12, 0.35,
                        location=(x, y + d/2 + 0.05, logo_z - h*0.05))
        assign(cross, make_emissive(f"{name}_LogoCross", COL_LOGO_WHITE, 8.0))


def build_satellite_district():
    """10 torres satélites alrededor de la plaza."""
    # Anillo interno (más cerca de HQ)
    inner_ring = [
        ( 12,  -8, 5,  5, 22, COL_NEON_BLUE,   False),
        ( 22, -10, 4,  4, 18, COL_NEON_CYAN,   False),
        (-22, -12, 6,  5, 26, COL_NEON_MAGENTA, True),
        (-25,  10, 4,  4, 16, COL_NEON_BLUE,   False),
    ]
    for (x, y, w, d, h, col, logo) in inner_ring:
        build_satellite_tower(f"Inner_{x}_{y}", x, y, w, d, h, col, logo)

    # Anillo externo
    outer_ring = [
        ( 28, -22, 5,  5, 30, COL_NEON_PURPLE,  False),
        (-30, -25, 4,  4, 20, COL_NEON_BLUE,    False),
        ( 30,  18, 4,  5, 24, COL_NEON_CYAN,    False),
        (-28,  22, 6,  4, 28, COL_NEON_MAGENTA, True),
        ( 18,  28, 5,  5, 22, COL_NEON_BLUE,    False),
        (-18,  30, 4,  4, 18, COL_NEON_PURPLE,  False),
    ]
    for (x, y, w, d, h, col, logo) in outer_ring:
        build_satellite_tower(f"Outer_{x}_{y}", x, y, w, d, h, col, logo)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ SKYBRIDGE CONECTOR                                                 ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_skybridge():
    """Puente elevado entre HQ y torre Inner_12_-8."""
    # Viga estructural
    beam = add_box("Skybridge", 22, 2, 1.2, location=(2, -8, 12))
    assign(beam, make_material("SkybridgeMat",
        COL_METAL_LIGHT, 0.3, 0.9,
        COL_NEON_CYAN, 1.0))
    add_bevel(beam, 0.05, 3)

    # Pasarela de vidrio inferior (emisiva)
    floor = add_box("SkybridgeFloor", 21.5, 1.8, 0.1, location=(2, -8, 11.45))
    assign(floor, make_material("SkyFloorMat",
        (0.05, 0.10, 0.20, 1), 0.2, 0.0,
        COL_NEON_CYAN, 2.0))

    # Barandillas LED a los lados
    for sign in (-1.05, 1.05):
        rail = add_box(f"SkybridgeRail_{sign}", 21.5, 0.08, 0.5,
                       location=(2, -8 + sign, 12.4))
        assign(rail, make_emissive(f"SkyRailMat_{sign}",
                                    COL_NEON_BLUE, 7.0))

    # Pilares de soporte
    for px in (-8, 2, 12):
        pil = add_cylinder(f"SkybridgePillar_{px}", 0.4, 12,
                           location=(px, -8, 6))
        assign(pil, make_material("PillarMat",
            COL_CONCRETE, 0.7, 0.0,
            COL_NEON_BLUE, 0.5))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ PLAZA CENTRAL — FUENTE HOLOGRÁFICA                                 ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_central_fountain():
    """Fuente circular con chorro y holograma del logo A arriba."""
    cx, cy = 10, 10

    # Base circular escalonada (3 niveles)
    for i, (r, h, z) in enumerate([(4.0, 0.4, 0.2),
                                    (3.2, 0.4, 0.5),
                                    (2.4, 0.4, 0.8)]):
        ring = add_cylinder(f"FountainRing{i}", r, h,
                            location=(cx, cy, z), vertices=64)
        assign(ring, make_material(f"FountainRingMat{i}",
            COL_METAL_DARK, 0.25, 0.8,
            COL_NEON_BLUE, 2.5))

    # Piscina de agua (disco azul oscuro emisivo)
    pool = add_cylinder("FountainPool", 2.3, 0.05,
                        location=(cx, cy, 0.95), vertices=64)
    assign(pool, make_material("WaterMat",
        (0.02, 0.10, 0.25, 1), 0.05, 0.0,
        COL_NEON_CYAN, 3.0))

    # Chorro central (cono emisivo)
    jet = add_cone("FountainJet", 0.15, 0.05, 6,
                   location=(cx, cy, 3.5), vertices=16)
    assign(jet, make_material("WaterJetMat",
        (0.4, 0.8, 1.0, 0.7), 0.1, 0.0,
        COL_NEON_CYAN, 4.0))

    # Holograma del logo "A" flotante arriba
    # Piernas
    hol_l = add_box("Hol_A_L", 0.15, 0.08, 3,
                    location=(cx - 0.5, cy, 7))
    hol_l.rotation_euler = (0, 0, math.radians(-10))
    assign(hol_l, make_emissive("HolMat", COL_NEON_CYAN, 12.0))

    hol_r = add_box("Hol_A_R", 0.15, 0.08, 3,
                    location=(cx + 0.5, cy, 7))
    hol_r.rotation_euler = (0, 0, math.radians(10))
    assign(hol_r, make_emissive("HolMat2", COL_NEON_CYAN, 12.0))

    hol_c = add_box("Hol_A_C", 1.2, 0.08, 0.3,
                    location=(cx, cy, 6.0))
    assign(hol_c, make_emissive("HolMat3", COL_NEON_CYAN, 12.0))

    # Anillos LED emisivos a varias alturas (efecto holográfico)
    for z in (4.5, 5.5, 6.5):
        ring = add_torus(f"HoloRing_{z}", 1.5, 0.05,
                          location=(cx, cy, z))
        # Rotar para verse horizontal
        ring.rotation_euler = (math.radians(90), 0, 0)
        assign(ring, make_emissive(f"HoloRingMat_{z}",
                                    COL_NEON_MAGENTA, 8.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ROBOT AUTÓNOMO DE DELIVERY                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_delivery_robot():
    """Pequeño robot tipo 'Optimus/Aguitech delivery' en la avenida."""
    x, y, z = -15, 27, 0.5

    # Cuerpo principal (cubo con bordes redondeados)
    body = add_box("RobotBody", 1.4, 1.0, 1.2, location=(x, y, z+1))
    assign(body, make_material("RobotBodyMat",
        COL_LOGO_WHITE, 0.2, 0.5,
        COL_NEON_CYAN, 1.5))
    add_bevel(body, 0.15, 4)

    # Cabeza con cámara
    head = add_box("RobotHead", 0.9, 0.8, 0.5, location=(x, y - 0.4, z+1.85))
    assign(head, make_material("RobotHeadMat",
        (0.10, 0.10, 0.12, 1), 0.3, 0.6,
        COL_NEON_BLUE, 2.0))

    # Ojos LED (2 pequeños cubos emisivos)
    for ox in (-0.25, 0.25):
        eye = add_box(f"RobotEye_{ox}", 0.15, 0.05, 0.15,
                      location=(x + ox, y - 0.85, z + 1.85))
        assign(eye, make_emissive(f"RobotEyeMat_{ox}",
                                   COL_NEON_CYAN, 15.0))

    # Logo Aguitech en el cuerpo
    logo = add_box("RobotLogo", 0.5, 0.05, 0.3,
                   location=(x, y + 0.55, z + 1))
    assign(logo, make_emissive("RobotLogoMat", COL_NEON_BLUE, 8.0))

    # Ruedas (4 toroides aplastados)
    for wx, wy in ((-0.6, -0.4), (0.6, -0.4), (-0.6, 0.4), (0.6, 0.4)):
        wheel = add_torus(f"RobotWheel_{wx}_{wy}", 0.25, 0.12,
                          location=(x + wx, y + wy, z + 0.1))
        wheel.rotation_euler = (math.radians(90), 0, 0)
        assign(wheel, make_material(f"RobotWheelMat_{wx}",
            COL_METAL_DARK, 0.5, 0.8))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ DRONES VOLANDO                                                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_drones():
    """Drones tipo cuadricóptero con LED inferior."""
    drones_pos = [
        (-5, -5, 18),
        (15, 5, 22),
        (-12, 15, 25),
        (25, 25, 20),
        (-25, -20, 28),
        (20, -25, 24),
    ]
    for i, (x, y, z) in enumerate(drones_pos):
        # Cuerpo
        body = add_uv_sphere(f"Drone{i}_Body", 0.3,
                             location=(x, y, z))
        assign(body, make_material(f"Drone{i}_Mat",
            COL_METAL_DARK, 0.4, 0.6,
            COL_NEON_BLUE, 1.0))

        # Brazos en X con rotores
        for ang in (45, 135, 225, 315):
            rad = math.radians(ang)
            bx = x + math.cos(rad) * 0.8
            by = y + math.sin(rad) * 0.8
            arm = add_box(f"Drone{i}_Arm_{ang}", 1.0, 0.05, 0.05,
                          location=(bx, by, z))
            arm.rotation_euler = (0, 0, rad)
            assign(arm, make_material(f"Drone{i}_ArmMat",
                COL_METAL_DARK, 0.3, 0.8))

            rotor = add_torus(f"Drone{i}_Rotor_{ang}", 0.35, 0.03,
                              location=(bx, by, z))
            rotor.rotation_euler = (math.radians(90), 0, 0)
            assign(rotor, make_material(f"Drone{i}_RotorMat",
                (0.3, 0.3, 0.35, 1), 0.4, 0.5))

        # LED inferior
        led = add_uv_sphere(f"Drone{i}_LED", 0.1,
                            location=(x, y, z - 0.35))
        assign(led, make_emissive(f"Drone{i}_LEDMat",
                                   COL_NEON_CYAN, 25.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ VIADUCTO ELEVADO                                                   ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_viaduct():
    """Autopista elevada cruzando por detrás de la plaza."""
    # Vía principal
    road = add_box("ViaductRoad", 80, 4, 0.4, location=(0, -22, 6))
    assign(road, make_material("ViaductRoadMat",
        (0.10, 0.10, 0.12, 1), 0.7))

    # Barandas LED
    for side in (-2.05, 2.05):
        rail = add_box(f"ViaductRail_{side}", 80, 0.1, 0.6,
                       location=(0, -22 + side, 6.6))
        assign(rail, make_emissive(f"ViaductRailMat_{side}",
                                    COL_NEON_MAGENTA, 5.0))

    # Pilares cada 10m
    for px in range(-35, 36, 10):
        pil = add_cylinder(f"ViaductPil_{px}", 0.5, 6,
                           location=(px, -22, 3))
        assign(pil, make_material("ViaductPilMat",
            COL_CONCRETE, 0.7, 0.0,
            COL_NEON_BLUE, 0.3))

    # Coches pasando (cubos con luces)
    cars = [
        (-30, -22, 1.0, 1.5, 0.8, COL_NEON_BLUE,  COL_WARM_LED),
        (-10, -22, 1.0, 1.5, 0.8, COL_NEON_MAGENTA, COL_WARM_LED),
        ( 15, -22, 1.0, 1.5, 0.8, COL_NEON_CYAN,   COL_WARM_LED),
        ( 30, -22, 1.0, 1.5, 0.8, COL_NEON_PURPLE, COL_WARM_LED),
    ]
    for i, (cx, cy, cw, cd, ch, body_col, headlight) in enumerate(cars):
        car = add_box(f"Car{i}", cw, cd, ch, location=(cx, cy, 6 + ch/2))
        assign(car, make_material(f"Car{i}Mat",
            body_col, 0.2, 0.7,
            body_col, 0.5))
        # Faros delanteros (luces cálidas brillantes)
        for hy in (-0.4, 0.4):
            hl = add_uv_sphere(f"Car{i}_HL_{hy}", 0.1,
                                location=(cx + cw/2 + 0.05, cy + hy, 6 + ch/2))
            assign(hl, make_emissive(f"Car{i}_HLMat_{hy}",
                                      headlight, 30.0))
        # Luces traseras rojas
        for hy in (-0.4, 0.4):
            tl = add_uv_sphere(f"Car{i}_TL_{hy}", 0.08,
                                location=(cx - cw/2 - 0.05, cy + hy, 6 + ch/2))
            assign(tl, make_emissive(f"Car{i}_TLMat_{hy}",
                                      (1.0, 0.1, 0.1, 1), 15.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ÁRBOLES NEÓN (jardines tech)                                       ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_neon_trees():
    """Árboles estilizados con tronco oscuro y copa de luz neón."""
    positions = [
        (-15, -15), (-15, -10), (-10, -15),
        ( 35, -15), ( 35, -10),
        (-15,  35), (-10,  35),
        ( 35,  35), ( 30,  35),
    ]
    for i, (x, y) in enumerate(positions):
        # Tronco
        trunk = add_cylinder(f"Tree{i}_Trunk", 0.15, 2.5,
                            location=(x, y, 1.25), vertices=8)
        assign(trunk, make_material(f"Tree{i}_TrunkMat",
            (0.06, 0.05, 0.04, 1), 0.8, 0.0,
            COL_NEON_CYAN, 0.3))

        # Copa: esfera emisiva colorida
        col = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                              COL_NEON_PURPLE, COL_NEON_BLUE])
        crown = add_uv_sphere(f"Tree{i}_Crown", 1.2,
                               location=(x, y, 3.5))
        crown.scale = (1, 1, 0.7)
        assign(crown, make_emissive(f"Tree{i}_CrownMat",
                                     col, 2.5))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ILUMINACIÓN                                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_lighting():
    """Iluminación cinematográfica de atardecer cyberpunk."""
    # Limpiar luces previas
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.select_set(True)
            bpy.ops.object.delete()

    # Sol bajo (tono cálido del atardecer)
    bpy.ops.object.light_add(type='SUN',
                              location=(20, 30, 25),
                              rotation=(math.radians(60),
                                        math.radians(15), 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.65, 0.40)
    sun.data.specular_factor = 0.5

    # Ambient point elevado (atardecer azul-violeta, simula hemi)
    bpy.ops.object.light_add(type='POINT',
                              location=(0, 0, 60))
    hemi = bpy.context.active_object
    hemi.name = "HemiAmbient"
    hemi.data.energy = 800
    hemi.data.color = (0.4, 0.4, 0.7)

    # Foco dramatico sobre la HQ (key light)
    bpy.ops.object.light_add(type='SPOT',
                              location=(-20, -25, 40),
                              rotation=(math.radians(55),
                                        math.radians(40), 0))
    key = bpy.context.active_object
    key.name = "KeySpot"
    key.data.energy = 800
    key.data.color = (0.6, 0.8, 1.0)
    key.data.spot_size = math.radians(45)
    key.data.spot_blend = 0.4

    # Luces de relleno (rim lights) magenta-azul para look neón
    for i, (loc, col) in enumerate([
        ((30, 25, 30), (1.0, 0.3, 0.7)),
        ((-30, 30, 25), (0.3, 0.6, 1.0)),
        ((0, -35, 25), (0.8, 0.4, 1.0)),
    ]):
        bpy.ops.object.light_add(type='AREA',
                                  location=loc,
                                  rotation=(math.radians(70), 0, 0))
        rim = bpy.context.active_object
        rim.name = f"RimLight{i}"
        rim.data.energy = 200
        rim.data.color = col
        rim.data.size = 8.0

    # Farolas LED puntuales en la avenida
    for fx in range(-30, 31, 10):
        bpy.ops.object.light_add(type='POINT',
                                  location=(fx, 32, 5))
        lamp = bpy.context.active_object
        lamp.name = f"Lamp_{fx}"
        lamp.data.energy = 80
        lamp.data.color = (1.0, 0.85, 0.55)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ CÁMARA                                                             ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_camera():
    """Cámara cinematográfica tipo Establishing Shot."""
    bpy.ops.object.camera_add(
        location=(42, -42, 28),
        rotation=(math.radians(50), 0, math.radians(45)))
    cam = bpy.context.active_object
    cam.name = "CinematicCamera"
    cam.data.lens = 28  # Gran angular cinematográfico
    cam.data.sensor_width = 36
    cam.data.clip_start = 0.1
    cam.data.clip_end = 500
    bpy.context.scene.camera = cam
    return cam


# ╔════════════════════════════════════════════════════════════════════╗
# ║ FONDO / SKY                                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_sky_gradient():
    """Gradiente de cielo procedural: atardecer cyberpunk (sin HDRI)."""
    world = bpy.data.worlds.new("WorldAguitech")
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
    bg.inputs["Strength"].default_value = 0.3

    # Gradient texture
    gradient = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    tex_gradient = nodes.new("ShaderNodeTexGradient")
    tex_gradient.gradient_type = 'SPHERICAL'

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].color = (0.95, 0.45, 0.20, 1)   # naranja atardecer
    color_ramp.color_ramp.elements[1].color = (0.06, 0.08, 0.20, 1)   # azul oscuro arriba
    # Add mid stop for magenta
    mid = color_ramp.color_ramp.elements.new(0.5)
    mid.color = (0.50, 0.20, 0.45, 1)

    links.new(gradient.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex_gradient.inputs["Vector"])
    links.new(tex_gradient.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], output.inputs["Surface"])


# ╔════════════════════════════════════════════════════════════════════╗
# ║ NIEBLA VOLUMÉTRICA                                                 ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_volumetrics():
    """Niebla volumétrica para atmósfera cyberpunk."""
    scene = bpy.context.scene
    scene.world.use_nodes = True

    # Volume scatter en world
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links

    volume = nodes.new("ShaderNodeVolumeScatter")
    volume.inputs["Color"].default_value = (0.10, 0.15, 0.30, 1)
    volume.inputs["Density"].default_value = 0.025
    volume.inputs["Anisotropy"].default_value = 0.5

    output = nodes.get("World Output")
    if output:
        # Insertar volume antes del output
        # Conectar volume a Volume input del output
        try:
            links.new(volume.outputs["Volume"], output.inputs["Volume"])
        except Exception:
            pass


# ╔════════════════════════════════════════════════════════════════════╗
# ║ CONFIGURACIÓN DE RENDER                                            ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'  # EEVEE para velocidad + buena calidad
    try:
        scene.eevee.use_volumetric_lights = True
        scene.eevee.volumetric_light_clamp = 10
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = 0.8
        scene.eevee.bloom_threshold = 0.9
        scene.eevee.bloom_radius = 6.0
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 1.0
        scene.eevee.gtao_factor = 0.5
        scene.eevee.use_ssr = True
    except Exception:
        pass

    # Resolucion 4K cinematic
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = RENDER_PATH
    scene.render.film_transparent = False

    # Color management
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
    safe_run("08 build_delivery_robot", build_delivery_robot)
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
    log("AGUITECH CITY — COMPLETADO")
    log("=" * 70)

except Exception:
    log(f"\nFATAL:\n{traceback.format_exc()}")
    raise
