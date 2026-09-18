"""
nestle_city.blend — NESTLÉ CONECTA × DIAFI MALL DISTRICT
==========================================================

Concepto basado en la infografía "Nestlé Conecta · DIAFI Mall District":
4 puntos cardinales × 4 tipos de ciudades / plazas:

  NORTE  → USO MIXTO       (oficinas + hoteles + residencias + servicios)
  ESTE   → FASHION MALL    (moda + estilo de vida, escaparates premium)
  SUR    → POWER CENTER    (compras masivas, grandes tiendas ancla)
  OESTE  → LIFESTYLE CENTER (experiencias, fuentes, palmeras, esculturas)

Centro: Rotonda DIAFI con portal holográfico + RedCup (mascota).

Render  -> ~/Projects/edificio/edificios/nestle_city/nestle_city.png
Blend   -> ~/Projects/edificio/edificios/nestle_city/nestle_city.blend
"""

import bpy
import math
import os
import sys
import traceback
import random

LOG_FILE = "/tmp/nestle_city.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n"); f.flush()
try: os.remove(LOG_FILE)
except FileNotFoundError: pass

log("=" * 70)
log("NESTLÉ CITY — DIAFI MALL DISTRICT")
log("=" * 70)

def safe_run(label, fn):
    log(f"  {label}...")
    try: fn(); log(f"  {label} OK")
    except Exception: log(f"  {label} ERROR:\n{traceback.format_exc()}"); raise

# RUTAS
SCRIPT_DIR  = "/Users/hectoraguilar/Projects/edificio/edificios/nestle_city"
IMAGES_DIR  = os.path.join(SCRIPT_DIR, "imagenes")
BLEND_PATH  = os.path.join(SCRIPT_DIR, "nestle_city.blend")
RENDER_PATH = os.path.join(IMAGES_DIR, "nestle_city.png")
os.makedirs(IMAGES_DIR, exist_ok=True)

# ╔════════════════════════════════════════════════════════════════════╗
# ║ PALETA                                                             ║
# ╚════════════════════════════════════════════════════════════════════╝
# Nestlé rojo + DIAFI azul + acentos
COL_NESTLE_RED    = (0.85, 0.10, 0.10, 1)
COL_NESTLE_RED_B  = (0.65, 0.05, 0.05, 1)
COL_NESTLE_WHITE  = (0.98, 0.96, 0.92, 1)
COL_NESTLE_CREAM  = (0.95, 0.88, 0.75, 1)
COL_DIAFI_BLUE    = (0.10, 0.45, 0.85, 1)
COL_DIAFI_BLUE_B  = (0.04, 0.20, 0.50, 1)
COL_DIAFI_CYAN    = (0.30, 0.85, 1.00, 1)
COL_NEON_CYAN     = (0.30, 0.85, 1.00, 1)
COL_NEON_MAGENTA  = (1.00, 0.30, 0.65, 1)
COL_NEON_PINK     = (1.00, 0.50, 0.80, 1)
COL_NEON_GOLD     = (1.00, 0.80, 0.30, 1)
COL_NEON_AMBER    = (1.00, 0.65, 0.10, 1)
COL_NEON_GREEN    = (0.20, 1.00, 0.50, 1)
COL_MIRROR_BLUE   = (0.10, 0.30, 0.55, 1)
COL_MIRROR_DARK   = (0.05, 0.10, 0.20, 1)
COL_DARK_GLASS    = (0.04, 0.06, 0.10, 1)
COL_METAL_DARK    = (0.10, 0.12, 0.15, 1)
COL_METAL_GOLD    = (0.85, 0.70, 0.30, 1)
COL_METAL_SILVER  = (0.75, 0.78, 0.82, 1)
COL_CONCRETE      = (0.30, 0.30, 0.32, 1)
COL_CONCRETE_W    = (0.75, 0.73, 0.70, 1)
COL_ASPHALT       = (0.08, 0.08, 0.10, 1)
COL_GRASS         = (0.05, 0.20, 0.08, 1)
COL_PALM_TRUNK    = (0.30, 0.20, 0.10, 1)
COL_PALM_LEAF     = (0.10, 0.40, 0.15, 1)
COL_LOGO_WHITE    = (0.98, 0.98, 1.00, 1)
COL_WARM_LED      = (1.00, 0.78, 0.35, 1)
COL_HOLOGRAM      = (0.40, 0.90, 1.00, 1)
COL_HOTEL_GLASS   = (0.08, 0.15, 0.30, 1)

_mat_cache = {}
def _rgb(c): return (c[0], c[1], c[2])

# UTILIDADES
def mat(name, base, rough=0.5, metal=0.0, emi=None, emi_s=0.0, alpha=1.0, ior=1.45):
    if name in _mat_cache: return _mat_cache[name]
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    ns = m.node_tree.nodes; ls = m.node_tree.links
    for n in ns: ns.remove(n)
    bsdf = ns.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        m.blend_method = 'BLEND'; bsdf.inputs["Alpha"].default_value = alpha
    if emi is not None:
        bsdf.inputs["Emission Color"].default_value = emi
        bsdf.inputs["Emission Strength"].default_value = emi_s
    out = ns.new("ShaderNodeOutputMaterial")
    ls.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _mat_cache[name] = m; return m

def emissive(name, color, strength=5.0):
    return mat(name, color, 0.3, 0.0, color, strength)
def mirror(name, tint=COL_MIRROR_BLUE, rough=0.05):
    return mat(name, tint, rough, 0.95)
def assign(obj, m):
    if obj.data.materials: obj.data.materials[0] = m
    else: obj.data.materials.append(m)
def box(name, w, h, d, loc=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = (w, h, d); return o
def cyl(name, r, h, loc=(0,0,0), v=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=v, location=loc)
    o = bpy.context.active_object; o.name = name; return o
def sphere(name, r, loc=(0,0,0), seg=32, rng=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=rng)
    o = bpy.context.active_object; o.name = name; return o
def torus(name, R, r, loc=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=64, minor_segments=24)
    o = bpy.context.active_object; o.name = name; return o
def cone(name, r1, r2, h, loc=(0,0,0), v=16):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, vertices=v, location=loc)
    o = bpy.context.active_object; o.name = name; return o
def bevel(o, w=0.02, s=2):
    m = o.modifiers.new(name="Bevel", type='BEVEL')
    m.width = w; m.segments = s; m.limit_method = 'ANGLE'

# ╔════════════════════════════════════════════════════════════════════╗
# ║ 01. LIMPIAR + TERRENO                                              ║
# ╚════════════════════════════════════════════════════════════════════╝
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(73)

def build_ground():
    """Terreno + 4 plazas circulares para los 4 distritos + calles conectoras."""
    ground = box("Ground", 500, 500, 0.1, loc=(0, 0, -0.05))
    assign(ground, mat("GroundMat", COL_ASPHALT, 0.9))

    # Plataforma central elevada (plaza DIAFI)
    center = cyl("CenterPlaza", 20, 0.3, loc=(0, 0, 0.15), v=64)
    assign(center, mat("CenterPlazaMat", COL_CONCRETE_W, 0.4))

    # Anillo LED perimetral del centro
    ring = torus("CenterRing", 22, 0.4, loc=(0, 0, 0.3))
    assign(ring, emissive("CenterRingMat", COL_DIAFI_CYAN, 12.0))

    # Pasto perimetral
    grass = box("Grass", 450, 450, 0.02, loc=(0, 0, -0.10))
    assign(grass, mat("GrassMat", COL_GRASS, 0.95))

    # 4 calles que conectan el centro con cada distrito cardinal
    for ang_deg in (0, 90, 180, 270):
        rad = math.radians(ang_deg)
        # Calle principal (40m ancho)
        for i, offset in enumerate([-3, 3]):
            sx = math.cos(rad) * 100
            sy = math.sin(rad) * 100
            road = box(f"Street_{ang_deg}_{i}", 6, 110, 0.05,
                       loc=(sx/2, sy/2, 0.025))
            # Rotar la calle para alinearla con su ángulo
            road.rotation_euler = (0, 0, math.radians(ang_deg))
            # Recalcular posición ya rotada
            cx = math.cos(rad) * 60 + math.cos(rad + math.radians(90)) * offset
            cy = math.sin(rad) * 60 + math.sin(rad + math.radians(90)) * offset
            road.location = (cx, cy, 0.025)
            assign(road, mat(f"StreetMat_{ang_deg}_{i}", COL_ASPHALT, 0.85))

        # Línea amarilla central de la calle
        cx = math.cos(rad) * 60
        cy = math.sin(rad) * 60
        line = box(f"StreetLine_{ang_deg}", 0.2, 110, 0.06,
                    loc=(cx, cy, 0.05))
        line.rotation_euler = (0, 0, math.radians(ang_deg))
        assign(line, emissive(f"StreetLineMat_{ang_deg}", COL_NEON_AMBER, 1.5))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 02. DISTRITO NORTE — USO MIXTO (rascacielos corporativos)          ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_distrito_norte():
    """USO MIXTO: 4 rascacielos corporativos + hotel + residencial."""
    log("  → distrito NORTE (Uso Mixto)...")
    cx, cy = 0, 100

    # Plataforma de plaza
    plaza = cyl("N_Plaza", 30, 0.2, loc=(cx, cy, 0.1), v=64)
    assign(plaza, mat("N_PlazaMat", COL_CONCRETE, 0.5))

    # 4 torres de oficinas espejo azul
    office_positions = [
        (-15, -10, 8, 7, 50, COL_DIAFI_BLUE),
        ( 15, -10, 7, 7, 45, COL_DIAFI_CYAN),
        (-15,  10, 7, 7, 42, COL_DIAFI_BLUE_B),
        ( 15,  10, 8, 7, 55, COL_DIAFI_BLUE),
    ]
    for i, (ox, oy, w, d, h, col) in enumerate(office_positions):
        bldg = box(f"N_Tower_{i}", w, d, h, loc=(cx+ox, cy+oy, h/2))
        assign(bldg, mirror(f"N_TowerMat_{i}", col, 0.05))
        bevel(bldg, 0.05, 3)

        # Franjas LED horizontales
        for z in range(8, int(h), 8):
            band = box(f"N_Tower_{i}_Band_{z}", w+0.2, d+0.2, 0.15,
                        loc=(cx+ox, cy+oy, z))
            assign(band, emissive(f"N_Tower_{i}_BandMat_{z}",
                                    random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                                    COL_NEON_PINK]), 8.0))

        # Banda superior
        top = box(f"N_Tower_{i}_Top", w+0.3, d+0.3, 0.4,
                   loc=(cx+ox, cy+oy, h+0.2))
        assign(top, emissive(f"N_Tower_{i}_TopMat", col, 12.0))

        # Antena
        ant = cyl(f"N_Tower_{i}_Ant", 0.10, h*0.15,
                   loc=(cx+ox, cy+oy, h + h*0.08))
        assign(ant, emissive(f"N_Tower_{i}_AntMat", COL_NEON_CYAN, 8.0))
        tip = sphere(f"N_Tower_{i}_Tip", 0.3, loc=(cx+ox, cy+oy, h + h*0.15))
        assign(tip, emissive(f"N_Tower_{i}_TipMat", COL_WARM_LED, 22.0))

    # Hotel (edificio más ancho, menos alto, con ventanas hoteleras)
    hotel = box("N_Hotel", 18, 8, 20, loc=(cx, cy, 10))
    assign(hotel, mat("N_HotelMat", COL_HOTEL_GLASS, 0.10, 0.5))
    # Ventanas iluminadas en grid
    for f in range(6):
        for k in range(11):
            for side in ('N', 'S'):
                if side == 'N':
                    win = box(f"N_Hotel_Win_{f}_{k}_{side}", 0.8, 0.05, 1.2,
                              loc=(cx - 8 + k*1.6, cy + 4.05, 2 + f*3))
                else:
                    win = box(f"N_Hotel_Win_{f}_{k}_{side}", 0.8, 0.05, 1.2,
                              loc=(cx - 8 + k*1.6, cy - 4.05, 2 + f*3))
                win_col = random.choices(
                    [COL_WARM_LED, COL_NEON_CYAN, COL_NEON_AMBER],
                    weights=[5, 1, 2])[0]
                assign(win, emissive(f"N_Hotel_WinMat_{f}_{k}_{side}",
                                      win_col, random.uniform(2, 5)))

    # Residencial (torres habitacionales)
    for i in range(3):
        tower = box(f"N_Res_{i}", 6, 6, random.uniform(14, 22),
                     loc=(cx + (-20 + i*20), cy + 22, 11))
        assign(tower, mat(f"N_ResMat_{i}",
                            random.choice([COL_CONCRETE_W, COL_PALM_TRUNK,
                                            (0.60, 0.62, 0.65, 1)]), 0.5))
        # Ventanas iluminadas
        n_floors = max(4, int(22/2.5))
        for f in range(n_floors):
            for k in range(3):
                for side in ('N', 'S', 'E', 'W'):
                    z = 2 + f * 2.2
                    if side in ('N', 'S'):
                        w_win = box(f"N_Res_{i}_W_{f}_{k}_{side}", 1.0, 0.05, 1.2,
                                     loc=(cx + (-20 + i*20) - 2 + k*2,
                                          cy + 22 + (3.05 if side == 'N' else -3.05),
                                          z))
                    else:
                        w_win = box(f"N_Res_{i}_W_{f}_{k}_{side}", 0.05, 1.0, 1.2,
                                     loc=(cx + (-20 + i*20) + (3.05 if side == 'E' else -3.05),
                                          cy + 22 - 2 + k*2,
                                          z))
                    wcol = random.choices([COL_WARM_LED, COL_NEON_AMBER, COL_NEON_PINK],
                                            weights=[5, 2, 1])[0]
                    assign(w_win, emissive(f"N_Res_{i}_WMat_{f}_{k}_{side}",
                                            wcol, random.uniform(2, 4)))

    # Letrero grande "USO MIXTO" en la base de la plaza
    sign = box("N_Sign_UM", 14, 0.3, 2.5, loc=(cx, cy - 18, 4))
    assign(sign, emissive("N_Sign_Mat", COL_DIAFI_CYAN, 10.0))
    # Letras
    for j, ch in enumerate("USO MIXTO"):
        lt = box(f"N_Sign_Let_{j}", 1.0, 0.4, 1.6, loc=(cx - 5.5 + j*1.4, cy - 18, 4))
        assign(lt, emissive(f"N_Sign_LetMat_{j}", COL_LOGO_WHITE, 14.0))

    # Fuente decorativa en la plaza
    ftn_base = cyl("N_Fountain", 3, 0.5, loc=(cx, cy, 0.35), v=32)
    assign(ftn_base, mat("N_FountainMat", COL_METAL_DARK, 0.3, 0.85))
    pool = cyl("N_FountainPool", 2.5, 0.1, loc=(cx, cy, 0.65), v=32)
    assign(pool, mat("N_FountainPoolMat",
                      (0.05, 0.20, 0.40, 1), 0.05, 0.0, COL_NEON_CYAN, 3.0))
    jet = cone("N_FountainJet", 0.2, 0.05, 5, loc=(cx, cy, 3), v=16)
    assign(jet, mat("N_FountainJetMat",
                     (0.5, 0.85, 1.0, 0.7), 0.08, 0.0, COL_NEON_CYAN, 4.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 03. DISTRITO ESTE — FASHION MALL (escaparates premium dorados)     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_distrito_este():
    """FASHION MALL: galerías comerciales con escaparates premium."""
    log("  → distrito ESTE (Fashion Mall)...")
    cx, cy = 100, 0

    # Plaza circular con piso de mármol
    plaza = cyl("E_Plaza", 30, 0.2, loc=(cx, cy, 0.1), v=64)
    assign(plaza, mat("E_PlazaMat",
                       random.choice([COL_CONCRETE_W, COL_NESTLE_CREAM]), 0.25, 0.0,
                       COL_NEON_GOLD, 0.5))

    # Edificio principal del Fashion Mall: forma de "U" o rectangular largo
    # Galerías comerciales con escaparates iluminados (luz cálida)
    mall = box("E_Mall", 35, 15, 12, loc=(cx, cy, 6))
    assign(mall, mat("E_MallMat", COL_NESTLE_WHITE, 0.35, 0.3,
                      COL_NEON_GOLD, 0.5))
    bevel(mall, 0.1, 4)

    # Techo curvo simulado (pirámide invertida)
    roof_top = box("E_MallRoof", 36, 16, 1, loc=(cx, cy, 12.5))
    assign(roof_top, mat("E_MallRoofMat", COL_DIAFI_BLUE_B, 0.3, 0.5))
    # Franja LED superior dorada
    cornice = box("E_MallCornice", 37, 17, 0.3, loc=(cx, cy, 13.2))
    assign(cornice, emissive("E_MallCorniceMat", COL_NEON_GOLD, 11.0))

    # Escaparates fashion (10 escaparates grandes con luz cálida)
    for i in range(10):
        for side in ('N', 'S'):
            x = cx - 15 + i*3.3
            if side == 'N':
                win = box(f"E_Win_{i}_{side}", 2.5, 0.05, 4,
                           loc=(x, cy + 7.55, 4.5))
            else:
                win = box(f"E_Win_{i}_{side}", 2.5, 0.05, 4,
                           loc=(x, cy - 7.55, 4.5))
            win_col = random.choice([COL_WARM_LED, COL_NEON_AMBER,
                                       COL_NEON_PINK, COL_NEON_GOLD])
            assign(win, emissive(f"E_WinMat_{i}_{side}",
                                  win_col, 5.0))

    # Marquesinas doradas por encima de cada escaparate
    for i in range(10):
        for side in ('N', 'S'):
            x = cx - 15 + i*3.3
            if side == 'N':
                mq = box(f"E_Marquee_{i}_{side}", 2.7, 0.8, 0.5,
                          loc=(x, cy + 7.6, 8.2))
            else:
                mq = box(f"E_Marquee_{i}_{side}", 2.7, 0.8, 0.5,
                          loc=(x, cy - 7.6, 8.2))
            assign(mq, mat(f"E_MarqueeMat_{i}_{side}",
                            COL_NEON_GOLD, 0.3, 0.5,
                            COL_NEON_GOLD, 5.0))

    # Letras "FASHION MALL" en la azotea
    for j, ch in enumerate("FASHION"):
        lt = box(f"E_Letter_FM_{j}", 1.2, 0.8, 1.6,
                  loc=(cx - 10 + j*3, cy, 14.5))
        assign(lt, emissive(f"E_Letter_FM_Mat_{j}", COL_NESTLE_RED, 14.0))

    # Tiendas exteriores (boutiques alrededor de la plaza)
    for i in range(8):
        ang = math.radians(i * 45)
        bx = cx + math.cos(ang) * 32
        by = cy + math.sin(ang) * 32
        bot = box(f"E_Boutique_{i}", 4, 4, 5, loc=(bx, by, 2.5))
        # Colores variados (lujosos)
        col_bot = random.choice([
            COL_NESTLE_RED_B, COL_METAL_GOLD, COL_DARK_GLASS,
            (0.20, 0.15, 0.10, 1), (0.45, 0.30, 0.20, 1)
        ])
        assign(bot, mat(f"E_BoutiqueMat_{i}", col_bot, 0.4, 0.3))
        # Escaparate iluminado
        esc = box(f"E_Boutique_Win_{i}", 3.5, 0.05, 3.5,
                   loc=(bx - math.cos(ang)*2.05, by - math.sin(ang)*2.05, 3))
        assign(esc, emissive(f"E_Boutique_WinMat_{i}",
                              random.choice([COL_WARM_LED, COL_NEON_GOLD,
                                              COL_NEON_PINK]), 5.5))

    # Pasarela techada circular conectando boutiques
    for i in range(8):
        ang1 = math.radians(i * 45)
        ang2 = math.radians((i+1) * 45)
        x1 = cx + math.cos(ang1) * 32
        y1 = cy + math.sin(ang1) * 32
        x2 = cx + math.cos(ang2) * 32
        y2 = cy + math.sin(ang2) * 32
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        seg_len = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        seg = box(f"E_Arcade_{i}", seg_len + 1, 1.5, 0.3,
                   loc=(mx, my, 4))
        seg.rotation_euler = (0, 0, math.atan2(y2-y1, x2-x1))
        assign(seg, mat(f"E_ArcadeMat_{i}", COL_NESTLE_WHITE, 0.4, 0.3))

    # Fuente central con querubín/escultura
    ftn_base = cyl("E_Fountain", 4, 0.5, loc=(cx, cy, 0.35), v=32)
    assign(ftn_base, mat("E_FountainMat", COL_METAL_GOLD, 0.2, 0.95))
    pool = cyl("E_FountainPool", 3.5, 0.1, loc=(cx, cy, 0.65), v=32)
    assign(pool, mat("E_FountainPoolMat",
                      (0.10, 0.30, 0.45, 1), 0.05, 0.0, COL_NEON_GOLD, 2.5))
    jet = cone("E_FountainJet", 0.25, 0.05, 6, loc=(cx, cy, 3.5), v=20)
    assign(jet, mat("E_FountainJetMat",
                     (1.0, 0.85, 0.50, 0.7), 0.08, 0.0, COL_NEON_GOLD, 4.5))

    # Letrero en el piso de la plaza
    for j, ch in enumerate("FASHION MALL"):
        lt = box(f"E_FloorSign_{j}", 0.8, 1.5, 0.05,
                  loc=(cx - 8 + j*1.4, cy, 0.22))
        assign(lt, emissive(f"E_FloorSignMat_{j}",
                              random.choice([COL_NESTLE_RED, COL_NEON_GOLD]), 10.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 04. DISTRITO SUR — POWER CENTER (grandes tiendas tipo warehouse)   ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_distrito_sur():
    """POWER CENTER: tiendas ancla grandes, estacionamientos masivos."""
    log("  → distrito SUR (Power Center)...")
    cx, cy = 0, -100

    # Plaza de concreto
    plaza = box("S_Plaza", 60, 60, 0.15, loc=(cx, cy, 0.07))
    assign(plaza, mat("S_PlazaMat", COL_CONCRETE, 0.85))

    # 4 grandes tiendas ancla (tipo Costco, Walmart, etc.)
    anchor_stores = [
        ("S_Store1", -20, -20, 18, 18, 14, COL_NESTLE_RED),
        ("S_Store2",  20, -20, 16, 18, 14, COL_DIAFI_BLUE),
        ("S_Store3", -20,  20, 16, 18, 14, COL_NEON_GOLD),
        ("S_Store4",  20,  20, 18, 18, 14, COL_NEON_GREEN),
    ]
    for name, ox, oy, w, d, h, col in anchor_stores:
        store = box(name, w, d, h, loc=(cx+ox, cy+oy, h/2))
        assign(store, mat(f"{name}Mat",
                            random.choice([COL_CONCRETE_W, (0.75, 0.70, 0.65, 1),
                                            (0.60, 0.60, 0.62, 1)]), 0.85))
        # Techo plano industrial
        roof = box(f"{name}_Roof", w+0.5, d+0.5, 0.5, loc=(cx+ox, cy+oy, h+0.25))
        assign(roof, mat(f"{name}_RoofMat", COL_METAL_DARK, 0.6, 0.7))

        # Banda superior de color de marca
        band = box(f"{name}_BrandBand", w+0.3, d+0.3, 0.8,
                    loc=(cx+ox, cy+oy, h+1.2))
        assign(band, mat(f"{name}_BrandBandMat", col, 0.4, 0.0,
                          col, 6.0))

        # Logo gigante en la fachada frontal (texto)
        for j, ch in enumerate("STORE"):
            lt = box(f"{name}_Logo_{j}", 1.5, 0.10, 2.5,
                      loc=(cx+ox - 3 + j*1.5, cy+oy - d/2 - 0.10, h - 2.5))
            assign(lt, emissive(f"{name}_LogoMat_{j}",
                                  random.choice([col, COL_LOGO_WHITE]), 11.0))

        # Entrada (puertas grandes)
        for dx in (-w/4, w/4):
            door = box(f"{name}_Door_{dx}", 3, 0.05, 4,
                        loc=(cx+ox + dx, cy+oy - d/2 - 0.10, 2))
            assign(door, mat(f"{name}_DoorMat_{dx}",
                              (0.30, 0.20, 0.15, 1), 0.6, 0.0,
                              COL_WARM_LED, 0.5))

    # Estacionamiento amplio (rampa visual + espacios)
    park = box("S_Parking", 50, 18, 0.05, loc=(cx, cy + 30, 0.03))
    assign(park, mat("S_ParkingMat", COL_ASPHALT, 0.85))

    # Líneas de estacionamiento
    for i in range(-20, 21, 4):
        line = box(f"S_ParkLine_{i}", 0.15, 2.5, 0.06, loc=(cx + i, cy + 30, 0.06))
        assign(line, emissive(f"S_ParkLineMat_{i}", COL_NESTLE_WHITE, 1.5))

    # 12 autos estacionados
    for i in range(12):
        car = box(f"S_Car_{i}", 1.0, 1.8, 0.8, loc=(cx - 20 + i*3.3, cy + 30 + random.choice([-3, 0, 3]), 0.4))
        car_col = random.choice([COL_NESTLE_RED, COL_DIAFI_BLUE, COL_NEON_GOLD,
                                   COL_NEON_GREEN, COL_NEON_CYAN, COL_NEON_MAGENTA,
                                   COL_DARK_GLASS, COL_METAL_SILVER])
        assign(car, mat(f"S_CarMat_{i}", car_col, 0.3, 0.6, car_col, 0.3))

    # Faro torre de luz
    light_tower = cyl("S_LightTower", 0.3, 18, loc=(cx + 30, cy + 30, 9))
    assign(light_tower, mat("S_LightTowerMat", COL_METAL_DARK, 0.5, 0.8))
    light_box = box("S_LightBox", 4, 4, 1, loc=(cx + 30, cy + 30, 18))
    assign(light_box, mat("S_LightBoxMat", COL_METAL_DARK, 0.5, 0.7,
                            COL_WARM_LED, 4.0))

    # Letrero "POWER CENTER"
    sign = box("S_Sign", 18, 0.3, 3, loc=(cx, cy, 6))
    assign(sign, emissive("S_SignMat", COL_NESTLE_RED, 12.0))
    for j, ch in enumerate("POWER CENTER"):
        lt = box(f"S_Sign_Let_{j}", 1.0, 0.4, 1.8, loc=(cx - 7.5 + j*1.4, cy - 0.05, 6))
        assign(lt, emissive(f"S_Sign_LetMat_{j}", COL_LOGO_WHITE, 15.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 05. DISTRITO OESTE — LIFESTYLE CENTER (experiencias + palmeras)     ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_distrito_oeste():
    """LIFESTYLE CENTER: arquitectura orgánica, palmeras, fuentes, esculturas."""
    log("  → distrito OESTE (Lifestyle Center)...")
    cx, cy = -100, 0

    # Plaza de losa de piedra clara
    plaza = cyl("W_Plaza", 32, 0.2, loc=(cx, cy, 0.1), v=64)
    assign(plaza, mat("W_PlazaMat", COL_CONCRETE_W, 0.25, 0.0,
                       COL_NEON_CYAN, 0.3))

    # Palmeras (12) alrededor de la plaza
    palm_positions = []
    for i in range(12):
        ang = math.radians(i * 30)
        px = cx + math.cos(ang) * 30
        py = cy + math.sin(ang) * 30
        palm_positions.append((px, py))

    for i, (px, py) in enumerate(palm_positions):
        # Tronco curvo (cilindro alto)
        trunk = cyl(f"W_Palm_{i}", 0.4, 10, loc=(px, py, 5), v=12)
        assign(trunk, mat(f"W_Palm_Mat_{i}", COL_PALM_TRUNK, 0.85, 0.0,
                            COL_NEON_CYAN, 0.2))

        # Copa (8 hojas emisivas en forma de palmera)
        for j in range(8):
            ang_leaf = math.radians(j * 45)
            leaf = box(f"W_Palm_{i}_Leaf_{j}", 0.2, 4, 0.1,
                        loc=(px + math.cos(ang_leaf)*1.5,
                              py + math.sin(ang_leaf)*1.5,
                              9.5))
            leaf.rotation_euler = (math.radians(60), 0, ang_leaf)
            assign(leaf, mat(f"W_Palm_{i}_LeafMat_{j}",
                              COL_PALM_LEAF, 0.6, 0.0,
                              random.choice([COL_PALM_LEAF, COL_NEON_GREEN]), 0.5))

    # Edificio curvo orgánico (centro del lifestyle)
    # Simulado con cubo redondeado
    org_body = box("W_Organic", 22, 18, 8, loc=(cx, cy, 4))
    assign(org_body, mat("W_OrganicMat", COL_NESTLE_WHITE, 0.20, 0.3))
    bevel(org_body, 0.3, 6)

    # Techo ondulado (simulado con prismas apilados)
    for k in range(3):
        roof = box(f"W_OrganicRoof_{k}", 22 - k*2, 18 - k*2, 0.5,
                    loc=(cx, cy, 8 + k*0.7))
        assign(roof, mat(f"W_OrganicRoofMat_{k}", COL_DIAFI_BLUE_B, 0.3, 0.5))

    # Escaparates grandes panorámicos (luz cálida lifestyle)
    for side_idx, (side, dx, dy, ddx, ddy) in enumerate([
        ("N", 0, 9.05, 1, 0.05),
        ("S", 0, -9.05, 1, 0.05),
        ("E", 11.05, 0, 0.05, 1),
        ("W", -11.05, 0, 0.05, 1),
    ]):
        win = box(f"W_Pano_{side}", ddx*20, ddy*16, 5,
                   loc=(cx + dx, cy + dy, 4))
        win_col = random.choice([COL_WARM_LED, COL_NEON_GOLD, COL_NESTLE_CREAM])
        assign(win, emissive(f"W_PanoMat_{side}", win_col, 4.5))

    # Fuente monumental con escultura central
    ftn_base = cyl("W_Fountain", 6, 0.5, loc=(cx, cy, 0.35), v=48)
    assign(ftn_base, mat("W_FountainMat", COL_CONCRETE_W, 0.4))

    # Piscina con anillos
    pool = cyl("W_FountainPool", 5.5, 0.1, loc=(cx, cy, 0.65), v=48)
    assign(pool, mat("W_FountainPoolMat",
                      (0.05, 0.30, 0.40, 1), 0.05, 0.0, COL_NEON_CYAN, 3.0))
    for i, rad in enumerate([5, 4, 3, 2, 1]):
        ring = torus(f"W_FountainRing_{i}", rad, 0.06, loc=(cx, cy, 0.7))
        ring.rotation_euler = (math.radians(90), 0, 0)
        col_r = random.choice([COL_NEON_CYAN, COL_NEON_MAGENTA,
                                COL_NEON_GOLD])
        assign(ring, emissive(f"W_FountainRingMat_{i}", col_r, 8.0))

    # Chorro central + escultura "A" gigante líquida
    jet = cone("W_FountainJet", 0.4, 0.10, 9, loc=(cx, cy, 5), v=24)
    assign(jet, mat("W_FountainJetMat",
                     (0.6, 0.9, 1.0, 0.7), 0.08, 0.0, COL_NEON_CYAN, 5.5))

    # Escultura: monolito de mármol con la "A" de Nestlé grabada
    sculpture = box("W_Sculpture", 2, 2, 6, loc=(cx + 18, cy + 18, 3))
    assign(sculpture, mat("W_SculptureMat", COL_CONCRETE_W, 0.3, 0.0,
                            COL_NEON_GOLD, 0.3))
    bevel(sculpture, 0.15, 4)
    # A grabada (emisiva dorada)
    leg_l = box("W_Sculpture_A_L", 0.4, 0.15, 2.5, loc=(cx + 17.5, cy + 19.1, 4.5))
    leg_l.rotation_euler = (0, 0, math.radians(-12))
    assign(leg_l, emissive("W_Sculpture_ALMat", COL_NEON_GOLD, 12.0))
    leg_r = box("W_Sculpture_A_R", 0.4, 0.15, 2.5, loc=(cx + 18.5, cy + 19.1, 4.5))
    leg_r.rotation_euler = (0, 0, math.radians(12))
    assign(leg_r, emissive("W_Sculpture_ARMat", COL_NEON_GOLD, 12.0))
    cross = box("W_Sculpture_A_C", 1.2, 0.15, 0.3, loc=(cx + 18, cy + 19.1, 3.5))
    assign(cross, emissive("W_Sculpture_ACMat", COL_NEON_GOLD, 12.0))

    # Pérgola techada con vides
    pergola_positions = [(-25, -25), (-25, 25), (25, -25), (25, 25)]
    for i, (px, py) in enumerate(pergola_positions):
        # 4 postes
        for cdx, cdy in ((-2, -2), (-2, 2), (2, -2), (2, 2)):
            col = cyl(f"W_Pergola_{i}_Col_{cdx}_{cdy}", 0.15, 4,
                       loc=(cx + px + cdx, cy + py + cdy, 2), v=8)
            assign(col, mat(f"W_Pergola_{i}_ColMat", COL_CONCRETE_W, 0.5))
        # Techo de la pérgola
        roof_p = box(f"W_Pergola_{i}_Roof", 5, 5, 0.2,
                      loc=(cx + px, cy + py, 4.1))
        assign(roof_p, mat(f"W_Pergola_{i}_RoofMat",
                            COL_DIAFI_BLUE_B, 0.4, 0.5))
        # Luz cálida debajo
        light_p = box(f"W_Pergola_{i}_Light", 4, 4, 0.05,
                       loc=(cx + px, cy + py, 3.9))
        assign(light_p, emissive(f"W_Pergola_{i}_LightMat",
                                   COL_WARM_LED, 3.0))

    # Letrero "LIFESTYLE CENTER"
    for j, ch in enumerate("LIFESTYLE"):
        lt = box(f"W_Sign_LS_{j}", 1.0, 0.4, 1.8,
                  loc=(cx - 7 + j*1.4, cy + 17, 2))
        assign(lt, emissive(f"W_Sign_LS_Mat_{j}",
                              random.choice([COL_NEON_CYAN, COL_NEON_GREEN]), 13.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 06. CENTRO DIAFI + PORTAL HOLOGRÁFICO + REDCUP                    ║
# ╚════════════════════════════════════════════════════════════════════╝
def build_centro_diafi():
    """Plaza central con portal holográfico y avatar RedCup."""
    log("  → CENTRO DIAFI...")
    cx, cy = 0, 0

    # Columnas DIAFI monumentales (4)
    for i in range(4):
        ang = math.radians(i * 90 + 45)
        px = cx + math.cos(ang) * 15
        py = cy + math.sin(ang) * 15
        col = cyl(f"Center_Col_{i}", 1.0, 14, loc=(px, py, 7), v=12)
        assign(col, mat(f"Center_ColMat_{i}", COL_DIAFI_BLUE_B, 0.25, 0.85))
        # Capitel LED
        cap = box(f"Center_Col_{i}_Cap", 1.6, 1.6, 0.6,
                   loc=(px, py, 14.5))
        assign(cap, emissive(f"Center_Col_{i}_CapMat", COL_DIAFI_CYAN, 11.0))

    # Portal holográfico central (cilindro de luz)
    portal = cyl("Center_Portal", 8, 16, loc=(cx, cy, 8), v=64)
    assign(portal, mat("Center_PortalMat",
                        (0.40, 0.90, 1.00, 0.30), 0.05, 0.0,
                        COL_HOLOGRAM, 8.0))

    # Anillos rotatorios del portal
    for i, (z, rad) in enumerate([(2, 7), (6, 8), (10, 7.5), (14, 7)]):
        ring = torus(f"Center_PortalRing_{i}", rad, 0.15, loc=(cx, cy, z))
        assign(ring, emissive(f"Center_PortalRingMat_{i}",
                                COL_HOLOGRAM, 14.0))

    # Símbolo DIAFI en el portal (proyectado)
    # "D" estilizada grande
    diafi_d = box("Center_DIAFI_D", 0.3, 4, 6, loc=(cx - 6.5, cy, 8))
    assign(diafi_d, emissive("Center_DIAFI_DMat", COL_HOLOGRAM, 18.0))
    diafi_d2 = box("Center_DIAFI_D2", 3.5, 0.3, 6, loc=(cx - 5.0, cy + 2.0, 8))
    assign(diafi_d2, emissive("Center_DIAFI_D2Mat", COL_HOLOGRAM, 18.0))
    diafi_d3 = box("Center_DIAFI_D3", 3.5, 0.3, 6, loc=(cx - 5.0, cy - 2.0, 8))
    assign(diafi_d3, emissive("Center_DIAFI_D3Mat", COL_HOLOGRAM, 18.0))

    # ─── REDCUP (mascota Nestlé) ───
    log("  → RedCup avatar...")
    rc_x, rc_y = 25, 0

    # Cuerpo (tacita roja con asa)
    cup = cyl("RedCup_Body", 2.5, 4, loc=(rc_x, rc_y, 4), v=32)
    assign(cup, mat("RedCup_BodyMat", COL_NESTLE_RED, 0.3, 0.2,
                     COL_NESTLE_RED, 1.5))
    bevel(cup, 0.2, 6)

    # Base de la tacita (aplanada)
    base = cyl("RedCup_Base", 2.7, 0.5, loc=(rc_x, rc_y, 1.5), v=32)
    assign(base, mat("RedCup_BaseMat", COL_DARK_GLASS, 0.4, 0.5))

    # Interior oscuro (café)
    interior = cyl("RedCup_Inside", 2.2, 0.4, loc=(rc_x, rc_y, 5.7), v=32)
    assign(interior, mat("RedCup_InsideMat", (0.20, 0.10, 0.05, 1), 0.3, 0.0,
                          COL_WARM_LED, 1.5))

    # Asa (torus lateral)
    handle = torus("RedCup_Handle", 1.0, 0.25, loc=(rc_x + 2.7, rc_y, 4))
    handle.rotation_euler = (0, math.radians(90), 0)
    assign(handle, mat("RedCup_HandleMat", COL_NESTLE_RED, 0.3, 0.2,
                        COL_NESTLE_RED, 1.5))

    # Ojos (2 esferas blancas con pupilas)
    for ox in (-0.8, 0.8):
        eye = sphere(f"RedCup_Eye_{ox}", 0.55, loc=(rc_x + ox, rc_y - 2.2, 5))
        assign(eye, mat(f"RedCup_EyeMat_{ox}", COL_LOGO_WHITE, 0.1, 0.0))
        # Pupila
        pupil = sphere(f"RedCup_Pupil_{ox}", 0.25,
                        loc=(rc_x + ox, rc_y - 2.6, 5))
        assign(pupil, mat(f"RedCup_PupilMat_{ox}", (0.05, 0.05, 0.05, 1), 0.1))

    # Sonrisa
    smile = torus("RedCup_Smile", 0.8, 0.10, loc=(rc_x, rc_y - 2.4, 3.5))
    smile.rotation_euler = (math.radians(90), math.radians(180), 0)
    assign(smile, emissive("RedCup_SmileMat", COL_LOGO_WHITE, 4.0))

    # Brazos (cilindros pequeños a los lados)
    for side in (-1, 1):
        arm = cyl(f"RedCup_Arm_{side}", 0.30, 2,
                   loc=(rc_x + side*3.2, rc_y - 0.5, 4.5), v=12)
        assign(arm, mat(f"RedCup_ArmMat_{side}", COL_NESTLE_RED_B, 0.3, 0.2,
                         COL_NESTLE_RED, 1.0))
        # Manos (esferas)
        hand = sphere(f"RedCup_Hand_{side}", 0.4,
                       loc=(rc_x + side*3.5, rc_y - 0.5, 3.3))
        assign(hand, mat(f"RedCup_HandMat_{side}", COL_NESTLE_RED, 0.3, 0.2))

    # Piernas (cortas)
    for side in (-1, 1):
        leg = cyl(f"RedCup_Leg_{side}", 0.4, 1.5,
                   loc=(rc_x + side*1, rc_y - 0.5, 0.75), v=12)
        assign(leg, mat(f"RedCup_LegMat_{side}", COL_NESTLE_RED_B, 0.3, 0.2))
        # Zapatos
        shoe = sphere(f"RedCup_Shoe_{side}", 0.5,
                       loc=(rc_x + side*1, rc_y - 0.5, 0.25))
        assign(shoe, mat(f"RedCup_ShoeMat_{side}",
                          COL_DARK_GLASS, 0.3, 0.5))

    # Logo "NESTLE" en el cuerpo
    for j, ch in enumerate("NESCAFE"):
        lt = box(f"RedCup_Let_{j}", 0.3, 0.05, 0.8,
                  loc=(rc_x - 1.2 + j*0.4, rc_y - 2.55, 4))
        assign(lt, emissive(f"RedCup_LetMat_{j}", COL_LOGO_WHITE, 12.0))


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 07. ILUMINACIÓN                                                    ║
# ╚════════════════════════════════════════════════════════════════════╗
def build_lighting():
    log("    → luces...")
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o, do_unlink=True)

    # Sol atardecer Nestlé (cálido)
    bpy.ops.object.light_add(type='SUN',
                              location=(60, 80, 70),
                              rotation=(math.radians(55), math.radians(15), 0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 2.3
    sun.data.color = _rgb((1.0, 0.70, 0.45))

    # Ambient
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 130))
    amb = bpy.context.active_object
    amb.name = "HemiAmbient"
    amb.data.energy = 2200
    amb.data.color = _rgb((0.40, 0.45, 0.70))

    # Spots dramaticos en cada distrito
    district_spots = [
        ("Norte", 0, 100, COL_DIAFI_CYAN),
        ("Este", 100, 0, COL_NEON_GOLD),
        ("Sur", 0, -100, COL_NESTLE_RED),
        ("Oeste", -100, 0, COL_NEON_GREEN),
    ]
    for name, dx, dy, col in district_spots:
        bpy.ops.object.light_add(type='SPOT',
                                  location=(dx - 30, dy - 30, 50),
                                  rotation=(math.radians(55),
                                            math.radians(45), 0))
        spot = bpy.context.active_object
        spot.name = f"Spot_{name}"
        spot.data.energy = 1500
        spot.data.color = _rgb(col)
        spot.data.spot_size = math.radians(40)

    # Spot sobre RedCup
    bpy.ops.object.light_add(type='SPOT',
                              location=(25, 30, 30),
                              rotation=(math.radians(60),
                                        math.radians(290), 0))
    spot_rc = bpy.context.active_object
    spot_rc.name = "Spot_RedCup"
    spot_rc.data.energy = 2000
    spot_rc.data.color = _rgb((1.0, 0.5, 0.5))
    spot_rc.data.spot_size = math.radians(30)

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
        rim.data.energy = 700
        rim.data.color = _rgb(col)
        rim.data.size = 40.0


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 08. CÁMARA + CIELO + RENDER                                        ║
# ╚════════════════════════════════════════════════════════════════════╝
def setup_camera():
    # Vista panorámica alta del conjunto
    bpy.ops.object.camera_add(
        location=(200, -200, 160),
        rotation=(math.radians(35), 0, math.radians(45)))
    cam = bpy.context.active_object
    cam.name = "CinematicCamera"
    cam.data.lens = 32
    cam.data.sensor_width = 36
    cam.data.clip_end = 1500
    bpy.context.scene.camera = cam

def build_sky():
    world = bpy.data.worlds.new("WorldNestle")
    bpy.context.scene.world = world
    world.use_nodes = True
    ns = world.node_tree.nodes; ls = world.node_tree.links
    for n in ns: ns.remove(n)

    out = ns.new("ShaderNodeOutputWorld")
    bg = ns.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.04, 0.04, 0.10, 1)
    bg.inputs["Strength"].default_value = 0.35

    coord = ns.new("ShaderNodeTexCoord")
    mapping = ns.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    grad = ns.new("ShaderNodeTexGradient")
    grad.gradient_type = 'SPHERICAL'
    ramp = ns.new("ShaderNodeValToRGB")
    # Puesta de sol cálida con toque rojo Nestlé
    ramp.color_ramp.elements[0].color = (1.0, 0.45, 0.15, 1)
    ramp.color_ramp.elements[1].color = (0.06, 0.08, 0.20, 1)
    mid = ramp.color_ramp.elements.new(0.5)
    mid.color = (0.70, 0.20, 0.45, 1)

    ls.new(coord.outputs["Object"], mapping.inputs["Vector"])
    ls.new(mapping.outputs["Vector"], grad.inputs["Vector"])
    ls.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    ls.new(ramp.outputs["Color"], bg.inputs["Color"])
    ls.new(bg.outputs["Background"], out.inputs["Surface"])

    vol = ns.new("ShaderNodeVolumeScatter")
    vol.inputs["Color"].default_value = (0.10, 0.12, 0.25, 1)
    vol.inputs["Density"].default_value = 0.018
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
        scene.eevee.bloom_intensity = 1.4
        scene.eevee.bloom_threshold = 0.8
        scene.eevee.bloom_radius = 9.0
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
    safe_run("04 build_distrito_norte", build_distrito_norte)
    safe_run("05 build_distrito_este", build_distrito_este)
    safe_run("06 build_distrito_sur", build_distrito_sur)
    safe_run("07 build_distrito_oeste", build_distrito_oeste)
    safe_run("08 build_centro_diafi", build_centro_diafi)
    safe_run("09 build_lighting", build_lighting)
    safe_run("10 setup_camera", setup_camera)
    safe_run("11 setup_render", setup_render)

    log("\n>>> Guardando .blend...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log(f">>> .blend guardado en {BLEND_PATH}")

    log("\n>>> Renderizando...")
    bpy.ops.render.render(write_still=True)
    log(f">>> Render guardado en {RENDER_PATH}")

    log("\n" + "=" * 70)
    log("NESTLÉ CITY — COMPLETADO")
    log("=" * 70)

except Exception:
    log(f"\nFATAL:\n{traceback.format_exc()}")
    raise
