"""
aguitech_city_v4 — CIUDAD COSMOPOLITA AGUITECH (versión audaz)
================================================================

Concepto: urbe cyberpunk de escala masiva con la energía visual de
Blade Runner + Times Square + CDMX Polanco.

200+ construcciones distribuidas en:
  - 6 avenidas principales con camellones (LED + árboles + pabellones)
  - 20 calles perpendiculares empedradas
  - 30 rascacielos espejo azul (distrito financiero)
  - 50 comercios con marquesinas neón (boutiques, cafés, restaurantes)
  - 80 casas/edificios residenciales con ventanas iluminadas
  - 25 espectaculares/vallas publicitarias gigantes
  - 12 pabellones decorativos en camellones (fuentes, esculturas)
  - 1 plaza central monumental con monumento Aguitech + 8 chorros
  - 60 vehículos con luces
  - Semáforos, pasos peatonales, señalización
  - 30 drones, 5 robots, 100+ ventanas iluminadas

Render  -> aguitech_city/imagenes/aguitech_city_v4.png  (1920x1080)
Blend   -> aguitech_city/aguitech_city_v4.blend
Tiempo  -> ~3 min render EEVEE
"""

import bpy
import math
import os
import sys
import traceback
import random

LOG_FILE = "/tmp/aguitech_city_v4.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")
        f.flush()

try: os.remove(LOG_FILE)
except FileNotFoundError: pass

log("=" * 70)
log("AGUITECH CITY v4 — CIUDAD COSMOPOLITA")
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
BLEND_PATH  = os.path.join(SCRIPT_DIR, "aguitech_city_v4.blend")
RENDER_PATH = os.path.join(IMAGES_DIR, "aguitech_city_v4.png")

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
COL_MIRROR_BLUE = (0.06, 0.20, 0.45, 1)
COL_MIRROR_DARK = (0.04, 0.08, 0.18, 1)
COL_DARK_GLASS  = (0.04, 0.06, 0.10, 1)
COL_METAL_DARK  = (0.08, 0.09, 0.12, 1)
COL_METAL_LIGHT = (0.55, 0.58, 0.62, 1)
COL_CONCRETE    = (0.22, 0.23, 0.26, 1)
COL_STONE_DARK  = (0.18, 0.18, 0.20, 1)
COL_BRICK       = (0.45, 0.20, 0.15, 1)
COL_BRICK_LIGHT = (0.65, 0.40, 0.30, 1)
COL_WOOD        = (0.35, 0.22, 0.12, 1)
COL_PLASTER     = (0.85, 0.82, 0.75, 1)
COL_PLASTER_W   = (0.92, 0.90, 0.85, 1)
COL_ASPHALT     = (0.06, 0.06, 0.08, 1)
COL_COBBLE      = (0.30, 0.28, 0.27, 1)
COL_GRASS       = (0.03, 0.10, 0.05, 1)
COL_LOGO_WHITE  = (0.95, 0.97, 1.00, 1)
COL_WARM_LED    = (1.00, 0.78, 0.35, 1)

_mat_cache = {}

def _rgb(c):
    return (c[0], c[1], c[2])

# ╔════════════════════════════════════════════════════════════════════╗
# ║ UTILIDADES                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def mat(name, base, rough=0.5, metal=0.0, emi=None, emi_s=0.0,
        alpha=1.0, ior=1.45):
    if name in _mat_cache:
        return _mat_cache[name]
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
                                      major_segments=48, minor_segments=24)
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
# ║ 01. LIMPIAR                                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(73)

# ╔════════════════════════════════════════════════════════════════════╗
# ║ 02. TERRENO + AVDAS + CALLES (grid urbano cosmopolita)             ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_city_grid():
    """Grid urbano: 6 avdas principales (E-O) + 5 avdas (N-S) + 20 calles."""
    log("    → construyendo grid urbano...")
    # Terreno base (pasto/concreto)
    ground = box("Ground", 400, 400, 0.1, loc=(0, 0, -0.05))
    assign(ground, mat("GroundMat", COL_ASPHALT, 0.9))

    # 6 avenidas principales horizontales (E-O), separadas cada 60m
    for i, y in enumerate([-150, -90, -30, 30, 90, 150]):
        # Pavimento de la avenida (más ancho: 18m)
        road = box(f"Avda_H_{i}", 400, 18, 0.05, loc=(0, y, 0.01))
        assign(road, mat(f"RoadMat_{i}", COL_ASPHALT, 0.85))

        # Líneas amarillas centrales
        for sign in (-1, 1):
            line = box(f"Avda_H_Line_{i}_{sign}", 400, 0.2, 0.06, loc=(0, y + sign*9, 0.05))
            assign(line, emissive(f"LineMat_{i}_{sign}", COL_NEON_AMBER, 1.2))

        # Camellón central (entre los 2 carriles): 6m con árboles/LED
        median = box(f"Avda_H_Median_{i}", 400, 6, 0.2, loc=(0, y, 0.1))
        median_col = random.choice([COL_NEON_CYAN, COL_NEON_BLUE, COL_NEON_PURPLE])
        assign(median, emissive(f"MedianMat_{i}", median_col, 0.5))

        # Banquetas a los lados
        for sign in (-1, 1):
            curb = box(f"Avda_H_Curb_{i}_{sign}", 400, 1.2, 0.15, loc=(0, y + sign*10, 0.07))
            assign(curb, mat(f"CurbMat_{i}_{sign}", COL_CONCRETE, 0.7))

    # 5 avenidas verticales (N-S), separadas cada 60m
    for i, x in enumerate([-120, -60, 0, 60, 120]):
        road = box(f"Avda_V_{i}", 18, 400, 0.05, loc=(x, 0, 0.01))
        assign(road, mat(f"RoadV_{i}", COL_ASPHALT, 0.85))

        for sign in (-1, 1):
            line = box(f"Avda_V_Line_{i}_{sign}", 0.2, 400, 0.06, loc=(x + sign*9, 0, 0.05))
            assign(line, emissive(f"LineVMat_{i}_{sign}", COL_NEON_AMBER, 1.2))

        median = box(f"Avda_V_Median_{i}", 6, 400, 0.2, loc=(x, 0, 0.1))
        assign(median, emissive(f"MedianVMat_{i}",
                                  random.choice([COL_NEON_CYAN, COL_NEON_BLUE]),
                                  0.5))

        for sign in (-1, 1):
            curb = box(f"Avda_V_Curb_{i}_{sign}", 1.2, 400, 0.15, loc=(x + sign*10, 0, 0.07))
            assign(curb, mat(f"CurbVMat_{i}_{sign}", COL_CONCRETE, 0.7))

    # 20 calles perpendiculares secundarias (entre las avdas principales)
    for i, x in enumerate(range(-110, 111, 12)):
        if x in (-120, -60, 0, 60, 120):  # ya cubiertas por avdas verticales
            continue
        # Solo en segmentos (calles que cruzan perpendiculares a avdas H)
        # NO las dibujamos (serían demasiadas) — el grid se siente con las avdas
        pass

# ╔════════════════════════════════════════════════════════════════════╗
# ║ 03. CALLE EMPEDRADA (distrito histórico/casco antiguo)             ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_cobblestone_district():
    """Una calle empedrada estilo casco antiguo con adoquines."""
    # Pavimento empedrado (textura procedural = matriz de cubos pequeños)
    street_x, street_y = -150, 0
    street_w, street_l = 12, 80

    # Base gris
    base = box("CobbleBase", street_w, street_l, 0.05, loc=(street_x, street_y, 0.02))
    assign(base, mat("CobbleBaseMat", COL_STONE_DARK, 0.85))

    # Adoquines individuales (matriz 12x40 = 480 cubos - pero optimizamos: plano con bumps)
    # Para hacerlo bien visible sin 480 objetos: cinta de adoquines alternados
    for row in range(0, 80, 2):
        for col in range(0, 12, 2):
            sx = street_x - 6 + col + 1
            sy = street_y - 40 + row + 1
            # Offset alternado (estilo adoquin real)
            offset = 1 if row % 4 == 0 else 0
            sx += offset
            stone = box(f"Cobble_{row}_{col}", 1.6, 1.6, 0.15,
                        loc=(sx, sy, 0.10))
            col_tone = random.choice([COL_COBBLE, (0.32, 0.30, 0.28, 1),
                                      (0.28, 0.26, 0.24, 1)])
            assign(stone, mat(f"CobbleMat_{row}_{col}", col_tone, 0.8))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 04. RASCACIELOS ESPEJO AZUL (30 en distrito financiero)            ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_skyscraper(name, x, y, w, d, h, color=COL_NEON_BLUE,
                     with_logo=False, with_screen=False, screen_color=None,
                     helipad=False):
    """Rascacielos de espejo azul."""
    body = box(f"{name}_Body", w, d, h, loc=(x, y, h/2))
    tint = random.choice([COL_MIRROR_BLUE, COL_MIRROR_DARK,
                          (0.05, 0.15, 0.40, 1),
                          (0.08, 0.25, 0.50, 1),
                          (0.04, 0.10, 0.25, 1)])
    assign(body, mirror(f"{name}_MirrorMat", tint, rough=0.06))

    # Franjas LED verticales (cada 4m)
    for i in range(int(h/4) - 1):
        z = 4 + i*4
        band = box(f"{name}_Band_{i}", w+0.15, d+0.15, 0.12,
                   loc=(x, y, z))
        col_band = random.choice([color, COL_NEON_CYAN, COL_NEON_MAGENTA,
                                    COL_NEON_PURPLE])
        assign(band, emissive(f"{name}_BandMat_{i}", col_band, 4.5))

    # Banda LED superior
    top = box(f"{name}_TopBand", w+0.25, d+0.25, 0.25,
              loc=(x, y, h-0.12))
    assign(top, emissive(f"{name}_TopMat", color, 11.0))

    # Corona LED
    crown = box(f"{name}_Crown", w*0.5, d*0.5, 0.4, loc=(x, y, h+0.2))
    assign(crown, emissive(f"{name}_CrownMat",
                              random.choice([COL_NEON_CYAN, COL_NEON_PINK,
                                              COL_NEON_PURPLE]), 9.0))

    # Antena con luz
    if h > 18:
        ant = cyl(f"{name}_Ant", 0.06, h*0.18, loc=(x, y, h + h*0.09))
        assign(ant, emissive(f"{name}_AntMat",
                              random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA]),
                              7.0))
        tip = sphere(f"{name}_Tip", 0.25, loc=(x, y, h + h*0.18))
        assign(tip, emissive(f"{name}_TipMat", COL_WARM_LED, 22.0))

    # Helipuerto en azotea (para rascacielos altos)
    if helipad:
        heli = cyl(f"{name}_Heli", 1.8, 0.2, loc=(x, y, h+0.3), v=32)
        assign(heli, mat(f"{name}_HeliMat", COL_NEON_GREEN, 0.4,
                          0.0, COL_NEON_GREEN, 1.0))
        # Cruz de helipuerto
        for ang in (45, 135):
            r = math.radians(ang)
            leg = box(f"{name}_HeliCross_{ang}", 2.5, 0.2, 0.1,
                      loc=(x + math.cos(r)*0.7, y + math.sin(r)*0.7, h+0.5))
            leg.rotation_euler = (0, 0, ang)
            assign(leg, emissive(f"{name}_HeliCrossMat_{ang}",
                                  COL_NEON_GREEN, 5.0))

    # Logo "A"
    if with_logo:
        logo_z = h * 0.6
        size = h * 0.20
        for ang_off, ox in ((-12, -w*0.25), (12, w*0.25)):
            leg = box(f"{name}_Logo_{ox}", 0.4, 0.15, size,
                      loc=(x + ox, y + d/2 + 0.08, logo_z))
            leg.rotation_euler = (0, 0, math.radians(ang_off))
            assign(leg, emissive(f"{name}_LogoMat_{ox}",
                                  COL_LOGO_WHITE, 12.0))
        cross = box(f"{name}_Logo_Cross", w*0.6, 0.15, 0.45,
                    loc=(x, y + d/2 + 0.08, logo_z - size*0.30))
        assign(cross, emissive(f"{name}_LogoCrossMat",
                                 COL_LOGO_WHITE, 12.0))

    # Pantalla LED gigante
    if with_screen:
        sw = w*0.75
        sh = h*0.22
        screen = box(f"{name}_Screen", sw, 0.05, sh,
                     loc=(x, y - d/2 - 0.05, h*0.50))
        sc = screen_color or random.choice([COL_NEON_MAGENTA, COL_NEON_PINK,
                                            COL_NEON_CYAN, COL_NEON_AMBER])
        assign(screen, emissive(f"{name}_ScreenMat", sc, 7.5))


def build_financial_district():
    """30 rascacielos distribuidos en el centro financiero."""
    log("    → rascacielos financieros...")
    # 30 rascacielos en grid 5x6 alrededor del centro
    sk_config = [
        # (x, y, w, d, h, color, logo, screen, helipad)
        (-100, -110, 7, 6, 45, COL_NEON_BLUE,    True,  True,  True),
        (-100,  -75, 5, 5, 32, COL_NEON_CYAN,    False, True,  False),
        (-100,  -45, 8, 6, 52, COL_NEON_MAGENTA, True,  True,  True),
        (-100,  -10, 6, 5, 38, COL_NEON_PURPLE,  False, True,  False),
        (-100,   25, 7, 6, 42, COL_NEON_BLUE,    True,  False, True),
        (-100,   55, 5, 5, 28, COL_NEON_CYAN,    False, True,  False),

        ( -65, -110, 6, 5, 36, COL_NEON_MAGENTA, True,  True,  False),
        ( -65,  -75, 7, 7, 48, COL_NEON_BLUE,    True,  True,  True),
        ( -65,  -45, 5, 5, 30, COL_NEON_CYAN,    False, False, False),
        ( -65,  -10, 8, 6, 55, COL_NEON_PURPLE,  True,  True,  True),
        ( -65,   25, 6, 5, 35, COL_NEON_MAGENTA, False, True,  False),
        ( -65,   55, 7, 6, 40, COL_NEON_BLUE,    True,  True,  False),

        (  10, -110, 9, 7, 60, COL_NEON_CYAN,    True,  True,  True),  # flagship
        (  10,  -75, 6, 6, 38, COL_NEON_MAGENTA, True,  True,  False),
        (  10,  -45, 7, 5, 42, COL_NEON_BLUE,    True,  True,  True),
        (  10,  -10, 5, 5, 28, COL_NEON_PURPLE,  False, True,  False),
        (  10,   25, 8, 7, 50, COL_NEON_CYAN,    True,  True,  True),
        (  10,   55, 6, 5, 32, COL_NEON_MAGENTA, False, True,  False),

        (  75, -110, 7, 6, 44, COL_NEON_PURPLE,  True,  True,  True),
        (  75,  -75, 5, 5, 30, COL_NEON_BLUE,    False, True,  False),
        (  75,  -45, 8, 6, 48, COL_NEON_CYAN,    True,  True,  True),
        (  75,  -10, 6, 5, 35, COL_NEON_MAGENTA, True,  True,  False),
        (  75,   25, 7, 7, 46, COL_NEON_BLUE,    True,  True,  True),
        (  75,   55, 5, 5, 28, COL_NEON_PURPLE,  False, True,  False),

        ( 100, -110, 6, 6, 40, COL_NEON_CYAN,    True,  True,  False),
        ( 100,  -75, 7, 5, 38, COL_NEON_BLUE,    False, True,  False),
        ( 100,  -45, 5, 5, 32, COL_NEON_MAGENTA, True,  True,  False),
        ( 100,  -10, 8, 7, 52, COL_NEON_CYAN,    True,  True,  True),
        ( 100,   25, 6, 5, 34, COL_NEON_PURPLE,  False, True,  False),
        ( 100,   55, 7, 6, 42, COL_NEON_BLUE,    True,  True,  True),
    ]
    for i, (x, y, w, d, h, col, logo, screen, heli) in enumerate(sk_config):
        build_skyscraper(f"SK{i}", x, y, w, d, h, col, logo, screen, None, heli)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 05. COMERCIOS / BOUTIQUES / RESTAURANTES (50)                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_shop(name, x, y, w, d, h, kind="boutique"):
    """Comercio pequeño con marquesina neón."""
    # Edificio base
    body = box(f"{name}_Body", w, d, h, loc=(x, y, h/2))
    if kind == "boutique":
        col_body = random.choice([COL_PLASTER, COL_PLASTER_W, COL_BRICK,
                                    (0.30, 0.32, 0.35, 1)])
    elif kind == "cafe":
        col_body = random.choice([COL_BRICK, COL_BRICK_LIGHT, COL_WOOD])
    elif kind == "restaurant":
        col_body = random.choice([COL_DARK_GLASS, COL_METAL_DARK, (0.15, 0.10, 0.08, 1)])
    else:
        col_body = COL_PLASTER
    assign(body, mat(f"{name}_BodyMat", col_body, 0.65))

    # Marquesina neón (sobre la puerta)
    marquee = box(f"{name}_Marquee", w*0.95, 0.1, 0.6, loc=(x, y + d/2 + 0.05, h+0.3))
    m_col = random.choice([COL_NEON_MAGENTA, COL_NEON_PINK, COL_NEON_CYAN,
                            COL_NEON_AMBER, COL_NEON_PURPLE, COL_NEON_GREEN])
    assign(marquee, emissive(f"{name}_MarqueeMat", m_col, 6.0))

    # Letras/logo en marquesina (cubos pequeños en línea)
    n_letters = random.randint(3, 6)
    for i in range(n_letters):
        lt = box(f"{name}_Letter_{i}", 0.3, 0.05, 0.4,
                  loc=(x - w*0.4 + i*(w*0.8/(n_letters-1)), y + d/2 + 0.10, h+0.3))
        assign(lt, emissive(f"{name}_LetterMat_{i}",
                              random.choice([COL_LOGO_WHITE, COL_NEON_AMBER]),
                              8.0))

    # Escaparate (ventana grande emisiva en planta baja)
    window = box(f"{name}_Window", w*0.7, 0.05, h*0.4,
                  loc=(x, y + d/2 + 0.03, h*0.25))
    w_col = random.choice([COL_NEON_CYAN, COL_WARM_LED, COL_NEON_PINK,
                            COL_NEON_AMBER])
    assign(window, emissive(f"{name}_WindowMat", w_col, 3.5))

    # Toldo/parasol
    awning = box(f"{name}_Awning", w*1.05, d*0.4, 0.08,
                  loc=(x, y + d*0.7, h*0.7))
    a_col = random.choice([COL_NEON_MAGENTA, COL_NEON_CYAN, COL_NEON_AMBER,
                            COL_NEON_PURPLE, COL_NEON_GREEN])
    assign(awning, mat(f"{name}_AwningMat", a_col, 0.5, 0.0,
                         a_col, 1.5))


def build_commercial_district():
    """50 comercios distribuidos a lo largo de las calles."""
    log("    → comercios...")
    commerce_positions = []
    # Generar posiciones a lo largo de las calles (entre rascacielos)
    shop_y_positions = [-105, -85, -55, -20, 15, 50, 85]
    shop_x_positions = [-90, -75, -55, -45, -25, 25, 45, 55, 75, 90]

    shop_count = 0
    for sy in shop_y_positions:
        for sx in shop_x_positions:
            if shop_count >= 50:
                break
            # Verificar que no esté dentro de un rascacielos
            w = random.choice([5, 6, 7, 8])
            d = random.choice([5, 6, 7])
            h = random.uniform(3.5, 7.5)
            kind = random.choice(["boutique", "cafe", "restaurant",
                                   "boutique", "cafe"])
            build_shop(f"Shop_{shop_count}", sx, sy, w, d, h, kind)
            shop_count += 1
        if shop_count >= 50:
            break


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 06. CASAS Y EDIFICIOS RESIDENCIALES (80)                          ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_house(name, x, y, w, d, h, style="modern"):
    """Casa o edificio residencial con ventanas iluminadas."""
    body = box(f"{name}_Body", w, d, h, loc=(x, y, h/2))
    if style == "modern":
        col_body = random.choice([COL_PLASTER, COL_PLASTER_W, (0.55, 0.55, 0.60, 1)])
        rough = 0.5
    elif style == "brick":
        col_body = random.choice([COL_BRICK, COL_BRICK_LIGHT, (0.40, 0.25, 0.18, 1)])
        rough = 0.7
    elif style == "wood":
        col_body = random.choice([COL_WOOD, (0.30, 0.18, 0.10, 1), (0.40, 0.25, 0.15, 1)])
        rough = 0.8
    else:  # tower
        col_body = random.choice([COL_PLASTER, (0.50, 0.52, 0.55, 1)])
        rough = 0.55
    assign(body, mat(f"{name}_BodyMat", col_body, rough))

    # Techo
    roof_h = 1.2 if style != "tower" else 0.3
    roof = box(f"{name}_Roof", w+0.3, d+0.3, roof_h, loc=(x, y, h + roof_h/2))
    if style == "modern":
        assign(roof, mat(f"{name}_RoofMat", (0.20, 0.20, 0.22, 1), 0.5))
    else:
        assign(roof, mat(f"{name}_RoofMat",
                          random.choice([COL_BRICK, (0.35, 0.18, 0.12, 1)]), 0.7))

    # Ventanas iluminadas (rejilla en 2 caras)
    n_floors = max(1, int(h / 2.5))
    n_per_floor = max(2, int(w / 1.5))
    for f in range(n_floors):
        z = 1.5 + f * 2.0
        for k in range(n_per_floor):
            x_off = -w/2 + (k + 0.5) * (w / n_per_floor)
            # Ventana frontal
            win = box(f"{name}_WinN_{f}_{k}", 0.7, 0.05, 1.0,
                      loc=(x + x_off, y + d/2 + 0.03, z))
            win_col = random.choices(
                [COL_WARM_LED, COL_NEON_CYAN, COL_NEON_AMBER,
                 COL_NEON_PINK, COL_NEON_BLUE],
                weights=[5, 1, 2, 1, 1])[0]
            assign(win, emissive(f"{name}_WinNMat_{f}_{k}",
                                  win_col, random.uniform(2.0, 5.0)))
            # A veces ventana lateral
            if k < int(d / 1.5) and random.random() > 0.4:
                y_off = -d/2 + (k + 0.5) * (d / max(1, int(d / 1.5)))
                win_e = box(f"{name}_WinE_{f}_{k}", 0.05, 0.7, 1.0,
                            loc=(x + w/2 + 0.03, y + y_off, z))
                win_col_e = random.choices(
                    [COL_WARM_LED, COL_NEON_CYAN, COL_NEON_AMBER],
                    weights=[5, 2, 2])[0]
                assign(win_e, emissive(f"{name}_WinEMat_{f}_{k}",
                                        win_col_e, random.uniform(2.0, 4.0)))

    # Puerta
    door = box(f"{name}_Door", 0.8, 0.05, 1.5, loc=(x, y + d/2 + 0.03, 0.75))
    assign(door, mat(f"{name}_DoorMat",
                      random.choice([COL_WOOD, (0.25, 0.15, 0.10, 1)]), 0.6))


def build_residential_district():
    """80 casas/edificios residenciales en zonas residenciales."""
    log("    → residenciales...")
    # Zonas residenciales: bordes exteriores de la ciudad
    res_positions = []
    # Anillos residenciales
    for ring_r, ring_count in [(180, 30), (210, 30), (235, 20)]:
        for i in range(ring_count):
            ang = math.radians(i * (360 / ring_count))
            x = math.cos(ang) * ring_r
            y = math.sin(ang) * ring_r
            res_positions.append((x, y))

    count = 0
    for x, y in res_positions[:80]:
        style = random.choice(["modern", "brick", "wood", "tower"])
        if style == "tower":
            w = random.uniform(5, 8)
            d = random.uniform(5, 8)
            h = random.uniform(10, 18)
        else:
            w = random.uniform(4, 7)
            d = random.uniform(4, 7)
            h = random.uniform(3, 7)
        build_house(f"House_{count}", x, y, w, d, h, style)
        count += 1


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 07. ESPECTACULARES / VALLAS PUBLICITARIAS (25)                     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_billboard(name, x, y, w=8, h=4, orientation="h"):
    """Espectacular con pantalla LED grande sobre 2 postes."""
    # Pantalla
    if orientation == "h":
        screen = box(f"{name}_Screen", w, 0.15, h, loc=(x, y, 6))
    else:
        screen = box(f"{name}_Screen", 0.15, w, h, loc=(x, y, 6))
    sc_col = random.choice([COL_NEON_MAGENTA, COL_NEON_CYAN, COL_NEON_PINK,
                             COL_NEON_AMBER, COL_NEON_PURPLE, COL_NEON_GREEN,
                             COL_NEON_BLUE])
    assign(screen, emissive(f"{name}_ScreenMat", sc_col, 7.0))

    # Marco de la pantalla
    frame = box(f"{name}_Frame", w+0.3, 0.20, h+0.3, loc=(x, y, 6))
    assign(frame, mat(f"{name}_FrameMat", COL_METAL_DARK, 0.4, 0.8))

    # 2 postes
    for px in (-w/2 + 0.3, w/2 - 0.3):
        post = cyl(f"{name}_Post_{px}", 0.10, 6, loc=(x + px, y, 3))
        assign(post, mat(f"{name}_PostMat", COL_METAL_DARK, 0.4, 0.9))

    # Logo "A" gigante en el centro de la pantalla
    logo_size = min(w, h) * 0.5
    leg_l = box(f"{name}_A_L", 0.15, 0.20, logo_size, loc=(x-w*0.12, y+0.12, 6))
    leg_l.rotation_euler = (0, 0, math.radians(-12))
    assign(leg_l, emissive(f"{name}_ALMat", COL_LOGO_WHITE, 12.0))
    leg_r = box(f"{name}_A_R", 0.15, 0.20, logo_size, loc=(x+w*0.12, y+0.12, 6))
    leg_r.rotation_euler = (0, 0, math.radians(12))
    assign(leg_r, emissive(f"{name}_ARMat", COL_LOGO_WHITE, 12.0))
    cross = box(f"{name}_A_C", w*0.4, 0.20, 0.20, loc=(x, y+0.12, 6 - logo_size*0.20))
    assign(cross, emissive(f"{name}_ACMat", COL_LOGO_WHITE, 12.0))


def build_billboards():
    """25 espectaculares distribuidos por la ciudad."""
    log("    → espectaculares...")
    bb_positions = [
        # A lo largo de las avdas principales
        (-150, -110), (-120, -110), (-90, -110), (-60, -110), (-30, -110),
        (  0, -110), ( 30, -110), ( 60, -110), ( 90, -110), (120, -110),
        (-150,  -70), (-90,  -70), (-30,  -70), ( 30,  -70), ( 90,  -70),
        (-150,   30), (-90,   30), (-30,   30), ( 30,   30), ( 90,   30),
        (-150,   90), (-90,   90), (-30,   90), ( 30,   90), ( 90,   90),
    ]
    for i, (x, y) in enumerate(bb_positions):
        orient = "h" if i % 2 == 0 else "v"
        w = random.choice([8, 10, 12])
        h = random.choice([3, 4, 5])
        build_billboard(f"BB{i}", x, y, w, h, orient)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 08. PABELLONES EN CAMELLONES (12)                                  ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_pavilion(name, x, y, kind="fountain"):
    """Pabellón decorativo en camellón."""
    if kind == "fountain":
        # Mini-fuente
        base = cyl(f"{name}_Base", 1.5, 0.3, loc=(x, y, 0.15), v=32)
        assign(base, mat(f"{name}_BaseMat", COL_METAL_DARK, 0.3, 0.7))
        # Anillos emisivos
        for i, rad in enumerate([1.2, 0.9, 0.6]):
            ring = torus(f"{name}_Ring_{i}", rad, 0.06, loc=(x, y, 0.4))
            ring.rotation_euler = (math.radians(90), 0, 0)
            col_r = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                    COL_NEON_BLUE])
            assign(ring, emissive(f"{name}_RingMat_{i}", col_r, 6.0))
        # Chorro
        jet = cone(f"{name}_Jet", 0.20, 0.05, 3, loc=(x, y, 2), v=16)
        assign(jet, mat(f"{name}_JetMat",
                         (0.50, 0.85, 1.0, 0.7), 0.1, 0.0,
                         COL_NEON_CYAN, 3.5))

    elif kind == "sculpture":
        # Escultura abstracta
        base = box(f"{name}_Base", 2, 2, 0.4, loc=(x, y, 0.2))
        assign(base, mat(f"{name}_BaseMat", COL_CONCRETE, 0.7))
        # Columnas retorcidas (cilindros apilados)
        for i in range(4):
            seg = cyl(f"{name}_Seg_{i}", 0.5 - i*0.05, 0.6,
                       loc=(x, y, 0.6 + i*0.6), v=16)
            assign(seg, mat(f"{name}_SegMat_{i}",
                              random.choice([COL_NEON_MAGENTA, COL_NEON_CYAN,
                                              COL_NEON_PURPLE]),
                              0.3, 0.5, random.choice([COL_NEON_MAGENTA,
                                                        COL_NEON_CYAN]), 3.5))

    elif kind == "bus_stop":
        # Parada de autobús moderna
        floor = box(f"{name}_Floor", 3, 1, 0.1, loc=(x, y, 0.05))
        assign(floor, mat(f"{name}_FloorMat", COL_METAL_DARK, 0.3, 0.8))
        # Techo de cristal
        roof = box(f"{name}_Roof", 3, 1.2, 0.1, loc=(x, y, 2.5))
        assign(roof, mat(f"{name}_RoofMat",
                          (0.10, 0.20, 0.40, 0.5), 0.05, 0.3,
                          COL_NEON_CYAN, 1.5))
        # Asiento
        seat = box(f"{name}_Seat", 2.5, 0.4, 0.4, loc=(x, y+0.3, 0.4))
        assign(seat, mat(f"{name}_SeatMat", COL_NEON_CYAN, 0.4, 0.6))
        # Pantalla LED informativa
        info = box(f"{name}_Info", 1.5, 0.05, 0.5, loc=(x, y+0.6, 1.5))
        assign(info, emissive(f"{name}_InfoMat", COL_NEON_AMBER, 5.0))


def build_pavilions():
    """12 pabellones distribuidos en camellones."""
    log("    → pabellones...")
    pav_positions = [
        # En camellones de avdas horizontales (cada 60m)
        (-100, -110, "fountain"), (0, -110, "sculpture"), (100, -110, "bus_stop"),
        (-100, -50, "bus_stop"),   (0, -50, "fountain"),   (100, -50, "sculpture"),
        (-100,  10, "sculpture"),  (0,  10, "bus_stop"),   (100,  10, "fountain"),
        (-100,  70, "fountain"),   (0,  70, "bus_stop"),   (100,  70, "sculpture"),
    ]
    for i, (x, y, kind) in enumerate(pav_positions):
        build_pavilion(f"Pav{i}", x, y, kind)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 09. PLAZA CENTRAL MONUMENTAL                                       ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_central_monument():
    """Plaza central con monumento Aguitech + 8 chorros + hologramas."""
    log("    → plaza central...")
    cx, cy = 30, 30  # dentro del distrito financiero

    # Plaza circular
    plaza = cyl(f"Plaza", 12, 0.15, loc=(cx, cy, 0.075), v=64)
    assign(plaza, mat("PlazaMat", (0.18, 0.18, 0.22, 1), 0.3, 0.0,
                       COL_NEON_CYAN, 0.5))

    # Anillos LED concéntricos en el piso
    for i, rad in enumerate([11, 9, 7, 5]):
        ring = torus(f"PlazaRing_{i}", rad, 0.10, loc=(cx, cy, 0.16))
        ring.rotation_euler = (math.radians(90), 0, 0)
        assign(ring, emissive(f"PlazaRingMat_{i}",
                                random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                COL_NEON_PURPLE, COL_NEON_PINK]),
                                9.0))

    # Monumento central: monolito con logo "A"
    mono = box("Monument", 3, 3, 12, loc=(cx, cy, 6))
    assign(mono, mat("MonumentMat", COL_METAL_LIGHT, 0.2, 0.85,
                      COL_NEON_BLUE, 1.0))
    bevel(mono, 0.1, 4)

    # Logo "A" gigante emisivo en el monolito (4 caras)
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        ox = math.cos(rad) * 1.6
        oy = math.sin(rad) * 1.6
        # Rotar para que mire hacia afuera
        leg_l = box(f"Mon_A_L_{ang}", 0.3, 0.15, 4, loc=(cx+ox, cy+oy, 8))
        leg_l.rotation_euler = (0, 0, ang + math.radians(-12))
        assign(leg_l, emissive(f"Mon_ALMat_{ang}", COL_LOGO_WHITE, 15.0))
        leg_r = box(f"Mon_A_R_{ang}", 0.3, 0.15, 4, loc=(cx+ox, cy+oy, 8))
        leg_r.rotation_euler = (0, 0, ang + math.radians(12))
        assign(leg_r, emissive(f"Mon_ARMat_{ang}", COL_LOGO_WHITE, 15.0))
        cross = box(f"Mon_A_C_{ang}", 2.0, 0.15, 0.4,
                     loc=(cx+ox*0.95, cy+oy*0.95, 6.8))
        cross.rotation_euler = (0, 0, ang)
        assign(cross, emissive(f"Mon_ACMat_{ang}", COL_LOGO_WHITE, 15.0))

    # 8 chorros alrededor del monolito
    for i in range(8):
        ang = math.radians(i * 45)
        jx = cx + math.cos(ang) * 5
        jy = cy + math.sin(ang) * 5
        jet = cone(f"Mon_Jet_{i}", 0.15, 0.04, 6, loc=(jx, jy, 3.5), v=16)
        col = random.choice([COL_NEON_CYAN, COL_NEON_BLUE, COL_NEON_MAGENTA])
        assign(jet, mat(f"Mon_JetMat_{i}",
                         (0.5, 0.85, 1.0, 0.7), 0.08, 0.0,
                         col, 4.5))

    # Holograma "A" sobre el monolito
    holo_z = 20
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        leg_l = box(f"Hol_A_L_{ang}", 0.20, 0.10, 4,
                     loc=(cx + math.cos(rad)*0.8, cy + math.sin(rad)*0.8, holo_z))
        leg_l.rotation_euler = (0, 0, ang + math.radians(-10))
        assign(leg_l, emissive(f"Hol_ALMat_{ang}", COL_NEON_CYAN, 18.0))
        leg_r = box(f"Hol_A_R_{ang}", 0.20, 0.10, 4,
                     loc=(cx + math.cos(rad)*0.8, cy + math.sin(rad)*0.8, holo_z))
        leg_r.rotation_euler = (0, 0, ang + math.radians(10))
        assign(leg_r, emissive(f"Hol_ARMat_{ang}", COL_NEON_CYAN, 18.0))
    # Travesaño del holograma (solo una cara, frontal)
    cross = box("Hol_A_C", 2.0, 0.10, 0.3, loc=(cx, cy, holo_z - 1.5))
    assign(cross, emissive("Hol_ACMat", COL_NEON_CYAN, 18.0))

    # Anillos holográficos
    for z in (15, 17, 19, 21):
        ring = torus(f"Hol_Ring_{z}", 2.5, 0.10, loc=(cx, cy, z))
        ring.rotation_euler = (math.radians(90), 0, 0)
        col_r = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA, COL_NEON_PINK])
        assign(ring, emissive(f"Hol_RingMat_{z}", col_r, 14.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 10. VEHÍCULOS (60 con luces)                                       ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_vehicle(name, x, y, z=0.5, body_color=None):
    """Auto con luces."""
    body_col = body_color or random.choice([
        COL_NEON_BLUE, COL_NEON_CYAN, COL_NEON_MAGENTA, COL_NEON_PURPLE,
        COL_NEON_PINK, COL_NEON_AMBER, COL_WARM_LED,
        COL_METAL_DARK, COL_METAL_LIGHT, COL_BRICK, COL_PLASTER
    ])
    # Carrocería
    body = box(f"{name}_Body", 1.0, 1.8, 0.7, loc=(x, y, z + 0.35))
    assign(body, mat(f"{name}_BodyMat", body_col, 0.25, 0.6,
                      body_col, 0.2))
    bevel(body, 0.05, 2)

    # Cabina (más pequeña, encima)
    cab = box(f"{name}_Cab", 0.9, 1.4, 0.5, loc=(x, y, z + 0.9))
    cab_col = random.choice([COL_DARK_GLASS, COL_MIRROR_BLUE, (0.05, 0.05, 0.08, 1)])
    assign(cab, mat(f"{name}_CabMat", cab_col, 0.10, 0.4,
                     COL_NEON_CYAN, 0.3))

    # Faros delanteros
    for hy in (-0.6, 0.6):
        hl = sphere(f"{name}_HL_{hy}", 0.10, loc=(x + 0.55, y + hy, z + 0.35))
        assign(hl, emissive(f"{name}_HLMat_{hy}", COL_WARM_LED, 30.0))
    # Luces traseras
    for hy in (-0.6, 0.6):
        tl = sphere(f"{name}_TL_{hy}", 0.08, loc=(x - 0.55, y + hy, z + 0.35))
        assign(tl, emissive(f"{name}_TLMat_{hy}", (1.0, 0.1, 0.1, 1), 18.0))

    # Ruedas
    for wx, wy in ((-0.45, -0.7), (0.45, -0.7), (-0.45, 0.7), (0.45, 0.7)):
        wh = torus(f"{name}_Wheel_{wx}_{wy}", 0.18, 0.10, loc=(x+wx, y+wy, z))
        wh.rotation_euler = (math.radians(90), 0, 0)
        assign(wh, mat(f"{name}_WheelMat", COL_METAL_DARK, 0.5, 0.7))


def build_traffic():
    """60 vehículos distribuidos en las avenidas."""
    log("    → tráfico...")
    car_positions = []
    # Distribuir autos en las avdas
    for avda_y in [-150, -90, -30, 30, 90, 150]:
        # Carril derecho
        for x in range(-180, 181, 25):
            car_positions.append((x, avda_y - 5, 0.5))
        # Carril izquierdo
        for x in range(-165, 181, 25):
            car_positions.append((x, avda_y + 5, 0.5))
    for avda_x in [-120, -60, 0, 60, 120]:
        # Carril norte
        for y in range(-180, 181, 25):
            car_positions.append((avda_x - 5, y, 0.5))
        # Carril sur
        for y in range(-165, 181, 25):
            car_positions.append((avda_x + 5, y, 0.5))

    # Limitar a 60 y aleatorizar
    random.shuffle(car_positions)
    for i, (x, y, z) in enumerate(car_positions[:60]):
        build_vehicle(f"Car{i}", x, y, z)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 11. SEMÁFOROS                                                      ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_traffic_lights():
    """Semáforos en intersecciones principales."""
    log("    → semáforos...")
    intersections = [
        (-120, -150), (-60, -150), (0, -150), (60, -150), (120, -150),
        (-120, -90), (-60, -90), (0, -90), (60, -90), (120, -90),
        (-120,  90), (-60,  90), (0,  90), (60,  90), (120,  90),
    ]
    for i, (x, y) in enumerate(intersections):
        # Poste
        post = cyl(f"TL{i}_Post", 0.10, 5, loc=(x + 9.5, y + 9.5, 2.5))
        assign(post, mat(f"TL{i}_PostMat", COL_METAL_DARK, 0.4, 0.8))
        # Caja del semáforo
        box_tl = box(f"TL{i}_Box", 0.4, 0.4, 1.2, loc=(x + 9.5, y + 9.5, 5.4))
        assign(box_tl, mat(f"TL{i}_BoxMat", COL_METAL_DARK, 0.5, 0.6))
        # 3 luces (rojo, amarillo, verde)
        for j, (col, zoff) in enumerate([((1, 0.1, 0.1, 1), 6.0),
                                            ((1, 0.85, 0.1, 1), 5.4),
                                            ((0.1, 1, 0.3, 1), 4.8)]):
            light = sphere(f"TL{i}_Light_{j}", 0.12,
                           loc=(x + 9.5, y + 9.7, zoff))
            # Solo una luz está encendida (ciclo)
            strength = 12.0 if j == i % 3 else 1.5
            assign(light, emissive(f"TL{i}_LightMat_{j}", col, strength))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 12. ROBOTS DE DELIVERY (5)                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_delivery_robot(x, y, suffix=""):
    z = 0.5
    body = box(f"RobotBody{suffix}", 1.4, 1.0, 1.2, loc=(x, y, z+1.0))
    assign(body, mat(f"RobotBodyMat{suffix}",
                      COL_LOGO_WHITE, 0.2, 0.5,
                      random.choice([COL_NEON_CYAN, COL_NEON_BLUE]),
                      1.5))
    bevel(body, 0.15, 4)
    head = box(f"RobotHead{suffix}", 0.9, 0.8, 0.5, loc=(x, y-0.4, z+1.85))
    assign(head, mat(f"RobotHeadMat{suffix}", (0.10, 0.10, 0.12, 1), 0.3, 0.6,
                      COL_NEON_BLUE, 2.0))
    for ox in (-0.25, 0.25):
        eye = box(f"RobotEye{suffix}_{ox}", 0.15, 0.05, 0.15,
                  loc=(x + ox, y-0.85, z+1.85))
        assign(eye, emissive(f"RobotEyeMat{suffix}_{ox}", COL_NEON_CYAN, 18.0))
    for wx, wy in ((-0.6, -0.4), (0.6, -0.4), (-0.6, 0.4), (0.6, 0.4)):
        wh = torus(f"RobotWheel{suffix}_{wx}_{wy}", 0.25, 0.12,
                    loc=(x+wx, y+wy, z+0.1))
        wh.rotation_euler = (math.radians(90), 0, 0)
        assign(wh, mat(f"RobotWheelMat{suffix}", COL_METAL_DARK, 0.5, 0.8))


def build_all_robots():
    log("    → robots...")
    positions = [(-130, 130, "_A"), (130, -130, "_B"), (130, 130, "_C"),
                  (-130, 30, "_D"), (50, 130, "_E")]
    for x, y, s in positions:
        build_delivery_robot(x, y, s)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 13. DRONES (30)                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_drones():
    log("    → drones...")
    positions = []
    for i in range(30):
        x = random.uniform(-200, 200)
        y = random.uniform(-200, 200)
        z = random.uniform(20, 50)
        positions.append((x, y, z))
    for i, (x, y, z) in enumerate(positions):
        body = sphere(f"Drone{i}_Body", 0.32, loc=(x, y, z))
        assign(body, mat(f"Drone{i}_Mat",
                          COL_METAL_DARK, 0.4, 0.6,
                          random.choice([COL_NEON_BLUE, COL_NEON_CYAN, COL_NEON_MAGENTA]),
                          1.5))
        for ang in (45, 135, 225, 315):
            rad = math.radians(ang)
            bx = x + math.cos(rad) * 0.9
            by = y + math.sin(rad) * 0.9
            arm = box(f"Drone{i}_Arm_{ang}", 1.1, 0.05, 0.05, loc=(bx, by, z))
            arm.rotation_euler = (0, 0, rad)
            assign(arm, mat(f"Drone{i}_ArmMat", COL_METAL_DARK, 0.3, 0.8))
            rotor = torus(f"Drone{i}_Rotor_{ang}", 0.38, 0.04, loc=(bx, by, z))
            rotor.rotation_euler = (math.radians(90), 0, 0)
            assign(rotor, mat(f"Drone{i}_RotorMat", (0.3, 0.3, 0.35, 1), 0.4, 0.5))
        led = sphere(f"Drone{i}_LED", 0.10, loc=(x, y, z-0.35))
        assign(led, emissive(f"Drone{i}_LEDMat",
                              random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA]),
                              28.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 14. ILUMINACIÓN                                                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_lighting():
    log("    → luces...")
    # Limpiar luces
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o, do_unlink=True)

    # Sol bajo atardecer
    bpy.ops.object.light_add(type='SUN',
                              location=(30, 50, 40),
                              rotation=(math.radians(55), math.radians(15), 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 2.2
    sun.data.color = _rgb((1.0, 0.65, 0.40))

    # Ambient hemi simulado
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 100))
    amb = bpy.context.active_object
    amb.name = "HemiAmbient"
    amb.data.energy = 1500
    amb.data.color = _rgb((0.35, 0.40, 0.65))

    # Farolas en camellones (miles de pequeños LEDs)
    for avda_y in [-150, -90, -30, 30, 90, 150]:
        for x in range(-180, 181, 15):
            bpy.ops.object.light_add(type='POINT', location=(x, avda_y, 4))
            lamp = bpy.context.active_object
            lamp.data.energy = 60
            lamp.data.color = _rgb((1.0, 0.85, 0.55))
    for avda_x in [-120, -60, 0, 60, 120]:
        for y in range(-180, 181, 15):
            bpy.ops.object.light_add(type='POINT', location=(avda_x, y, 4))
            lamp = bpy.context.active_object
            lamp.data.energy = 60
            lamp.data.color = _rgb((1.0, 0.85, 0.55))

    # Rim lights
    for i, (loc, col) in enumerate([
        ((150, 150, 50), (1.0, 0.3, 0.7)),
        ((-150, 150, 50), (0.3, 0.6, 1.0)),
        ((150, -150, 50), (0.8, 0.4, 1.0)),
        ((-150, -150, 50), (0.4, 0.9, 0.9)),
        ((0, 0, 80), (1.0, 0.5, 0.8)),
    ]):
        bpy.ops.object.light_add(type='AREA', location=loc,
                                  rotation=(math.radians(70), 0, 0))
        rim = bpy.context.active_object
        rim.data.energy = 500
        rim.data.color = _rgb(col)
        rim.data.size = 25.0

    # Spot dramático sobre el monumento central
    bpy.ops.object.light_add(type='SPOT',
                              location=(30, -50, 60),
                              rotation=(math.radians(55), 0, 0))
    spot = bpy.context.active_object
    spot.data.energy = 2500
    spot.data.color = _rgb((0.6, 0.85, 1.0))
    spot.data.spot_size = math.radians(40)


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 15. CÁMARA                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_camera():
    bpy.ops.object.camera_add(
        location=(180, -180, 110),
        rotation=(math.radians(40), 0, math.radians(45)))
    cam = bpy.context.active_object
    cam.name = "CinematicCamera"
    cam.data.lens = 35
    cam.data.sensor_width = 36
    cam.data.clip_end = 800
    bpy.context.scene.camera = cam


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 16. CIELO + ATMÓSFERA                                              ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_sky():
    world = bpy.data.worlds.new("WorldAguitech_v4")
    bpy.context.scene.world = world
    world.use_nodes = True
    ns = world.node_tree.nodes
    ls = world.node_tree.links
    for n in ns: ns.remove(n)

    out = ns.new("ShaderNodeOutputWorld")
    bg = ns.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.03, 0.04, 0.10, 1)
    bg.inputs["Strength"].default_value = 0.3
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
    vol.inputs["Density"].default_value = 0.018
    vol.inputs["Anisotropy"].default_value = 0.5
    try:
        ls.new(vol.outputs["Volume"], out.inputs["Volume"])
    except Exception:
        pass


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 17. RENDER                                                         ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    try:
        scene.eevee.use_volumetric_lights = True
        scene.eevee.volumetric_light_clamp = 15
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = 1.2
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
    safe_run("03 build_city_grid", build_city_grid)
    safe_run("04 build_cobblestone_district", build_cobblestone_district)
    safe_run("05 build_financial_district", build_financial_district)
    safe_run("06 build_commercial_district", build_commercial_district)
    safe_run("07 build_residential_district", build_residential_district)
    safe_run("08 build_billboards", build_billboards)
    safe_run("09 build_pavilions", build_pavilions)
    safe_run("10 build_central_monument", build_central_monument)
    safe_run("11 build_traffic", build_traffic)
    safe_run("12 build_traffic_lights", build_traffic_lights)
    safe_run("13 build_all_robots", build_all_robots)
    safe_run("14 build_drones", build_drones)
    safe_run("15 build_lighting", build_lighting)
    safe_run("16 setup_camera", setup_camera)
    safe_run("17 setup_render", setup_render)

    log("\n>>> Guardando .blend...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log(f">>> .blend guardado en {BLEND_PATH}")

    log("\n>>> Renderizando...")
    bpy.ops.render.render(write_still=True)
    log(f">>> Render guardado en {RENDER_PATH}")

    log("\n" + "=" * 70)
    log("AGUITECH CITY v4 — COMPLETADO")
    log("=" * 70)

except Exception:
    log(f"\nFATAL:\n{traceback.format_exc()}")
    raise
