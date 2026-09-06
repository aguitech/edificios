"""
estructura4.blend — Showroom premium V2 (más iluminación + más detalles)

MEJORAS v2:
- Iluminacion dramatica 3-puntos (key + fill + rim)
- Spotlights adicionales con gobos/colores
- Pasarela perimetral elevada con barandas de cristal
- Carteles luminosos con logo
- Maqueta con rascacielos mas altos (rascacielos iconicos)
- 4 personas silhouette baja poly
- Jardin vertical en pared
- Pantallas LED en el piso
- Mas anillos LED con colores mixtos (cian + magenta + blanco)
- Reflejos en piso mas marcados
"""

import bpy
import math
import os
import shutil
import random
from datetime import datetime
from mathutils import Vector

# ============== CONFIG ==============
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estructura4.blend")
REPO_DIR = os.path.dirname(OUTPUT)
IMGS_DIR = os.path.join(REPO_DIR, "imagenes")
os.makedirs(IMGS_DIR, exist_ok=True)

ANCHO = 30.0
PROFUNDO = 18.0
ALTURA = 7.5
RADIO_SHOWROOM = 3.8
ALTURA_SHOWROOM = 0.7

random.seed(2026)

# ============== LIMPIAR ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

sala = bpy.data.collections.new("Sala")
bpy.context.scene.collection.children.link(sala)
showroom_col = bpy.data.collections.new("ShowroomCentral")
bpy.context.scene.collection.children.link(showroom_col)
leds = bpy.data.collections.new("IluminacionLED")
bpy.context.scene.collection.children.link(leds)
pantallas = bpy.data.collections.new("Pantallas")
bpy.context.scene.collection.children.link(pantallas)
detalles = bpy.data.collections.new("Detalles")
bpy.context.scene.collection.children.link(detalles)
personas = bpy.data.collections.new("Personas")
bpy.context.scene.collection.children.link(personas)

# ============== TEXTURAS (MEJORADAS) ==============
def img_vacia(name, size=256):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    img.pixels.foreach_set([0.0] * (size * size * 4))
    img.pack()
    return img

def tex_piso_brillante(name="PisoBrillante", size=512, seed=11):
    """Piso oscuro pulido tipo mármol con alto reflejo."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base gris muy oscuro con tinte azul
    for i in range(size * size):
        pixels[i*4] = 0.06
        pixels[i*4+1] = 0.07
        pixels[i*4+2] = 0.10

    # Juntas de placas (placas grandes 4x4 metros)
    for junta_y in range(0, size, 256):
        for x in range(size):
            put(x, junta_y, 0.03, 0.03, 0.05)
    for junta_x in range(0, size, 256):
        for y in range(size):
            put(junta_x, y, 0.03, 0.03, 0.05)

    # Variacion sutil de marmol (vetas)
    for _ in range(20):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        largo = random.randint(100, 250)
        ang = random.uniform(0, math.pi)
        for s in range(largo):
            x = int(cx + s * math.cos(ang)) % size
            y = int(cy + s * math.sin(ang)) % size
            idx = (y * size + x) * 4
            pixels[idx] += random.uniform(0.01, 0.03)
            pixels[idx+1] += random.uniform(0.01, 0.03)
            pixels[idx+2] += random.uniform(0.01, 0.03)

    # Highlights brillantes (zonas pulidas)
    for _ in range(80):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        radio = random.randint(20, 60)
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                d = math.sqrt(dx*dx + dy*dy)
                if d <= radio:
                    factor = (1 - d/radio) * 0.5
                    px, py = (cx+dx) % size, (cy+dy) % size
                    idx = (py * size + px) * 4
                    pixels[idx] += factor * 0.08
                    pixels[idx+1] += factor * 0.10
                    pixels[idx+2] += factor * 0.15

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_pantalla_cityscape(name="CityscapeNocturno", size=512, seed=22):
    """Pantalla LED con rascacielos iluminados y nubes sutiles."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Cielo nocturno
    for y in range(size):
        f = y / size
        if f < 0.5:
            r = 0.03 + f * 0.10
            g = 0.05 + f * 0.12
            b = 0.18 + f * 0.35
        else:
            r = 0.08 + (f - 0.5) * 0.10
            g = 0.10 + (f - 0.5) * 0.10
            b = 0.30 + (f - 0.5) * 0.10
        for x in range(size):
            r_var = r + random.uniform(-0.02, 0.02)
            g_var = g + random.uniform(-0.02, 0.02)
            b_var = b + random.uniform(-0.02, 0.02)
            put(x, y, max(0, min(1, r_var)), max(0, min(1, g_var)), max(0, min(1, b_var)))

    # Luna
    luna_x, luna_y = int(size*0.75), int(size*0.18)
    luna_r = 25
    for dx in range(-luna_r, luna_r+1):
        for dy in range(-luna_r, luna_r+1):
            d = math.sqrt(dx*dx + dy*dy)
            if d <= luna_r:
                factor = 1 - d/luna_r
                px, py = luna_x + dx, luna_y + dy
                if 0 <= px < size and 0 <= py < size:
                    idx = (py * size + px) * 4
                    pixels[idx] = 0.85 + factor * 0.15
                    pixels[idx+1] = 0.85 + factor * 0.15
                    pixels[idx+2] = 0.95 + factor * 0.05

    # Estrellas
    for _ in range(50):
        sx = random.randint(0, size-1)
        sy = random.randint(0, int(size*0.5))
        if random.random() < 0.7:
            put(sx, sy, 1.0, 1.0, 1.0)

    # Edificios (rascacielos iconicos)
    x_actual = 0
    while x_actual < size:
        ancho_edif = random.randint(20, 60)
        alto_edif = random.randint(int(size*0.4), int(size*0.92))
        y_base = size - int(size * 0.20)

        # Cuerpo del edificio
        for dy in range(alto_edif):
            for dx in range(ancho_edif):
                if x_actual + dx < size and y_base - dy >= 0:
                    r = 0.04 + (dy / alto_edif) * 0.03
                    g = 0.05 + (dy / alto_edif) * 0.03
                    b = 0.08 + (dy / alto_edif) * 0.03
                    put(x_actual + dx, y_base - dy, r, g, b)

        # Antena o helipuerto
        if random.random() < 0.3 and alto_edif > size*0.7:
            antena_x = x_actual + ancho_edif // 2
            for dy in range(int(size*0.1)):
                if y_base - alto_edif - dy >= 0:
                    put(antena_x, y_base - alto_edif - dy, 0.02, 0.02, 0.03)
                    if antena_x + 1 < size:
                        put(antena_x+1, y_base - alto_edif - dy, 0.02, 0.02, 0.03)

        # Ventanas iluminadas (mas densas, con colores variados)
        for fila_vent in range(0, alto_edif, 3):
            for col_vent in range(2, ancho_edif-2, 3):
                if random.random() < 0.5:
                    wx = x_actual + col_vent
                    wy = y_base - fila_vent - 2
                    if 0 <= wx < size and 0 <= wy < size:
                        # Mas variedad: amarillo, blanco, naranja, rojo
                        r_color = random.choice([
                            (1.0, 0.85, 0.4),   # amarillo calido
                            (0.95, 0.95, 0.9),  # blanco
                            (1.0, 0.6, 0.2),    # naranja
                            (1.0, 0.4, 0.3),    # rojo
                            (0.6, 0.8, 1.0),    # azul frio
                            (0.4, 0.9, 0.7),    # verde-azul
                        ])
                        put(wx, wy, *r_color)
                        for off in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            if 0 <= wx+off[0] < size and 0 <= wy+off[1] < size and random.random() < 0.4:
                                put(wx+off[0], wy+off[1], *r_color)

        x_actual += ancho_edif + random.randint(1, 5)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_jardin_vertical(name="JardinVertical", size=512, seed=77):
    """Jardin vertical verde con plantas."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base oscura (panel donde crecen las plantas)
    for y in range(size):
        for x in range(size):
            put(x, y, 0.08, 0.06, 0.04)

    # Follaje (muchas hojas pequeñas)
    for _ in range(3000):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        radio = random.randint(2, 8)
        # Variedad de verdes
        verde = random.choice([
            (0.15, 0.45, 0.12),
            (0.20, 0.55, 0.18),
            (0.10, 0.35, 0.10),
            (0.25, 0.50, 0.15),
            (0.30, 0.60, 0.25),
        ])
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                if dx*dx + dy*dy <= radio*radio:
                    px, py = (cx+dx) % size, (cy+dy) % size
                    idx = (py * size + px) * 4
                    pixels[idx] = verde[0] + random.uniform(-0.03, 0.03)
                    pixels[idx+1] = verde[1] + random.uniform(-0.03, 0.03)
                    pixels[idx+2] = verde[2] + random.uniform(-0.03, 0.03)

    # Algunas flores pequeñas
    for _ in range(50):
        fx = random.randint(0, size-1)
        fy = random.randint(0, size-1)
        color = random.choice([(1.0, 0.3, 0.5), (1.0, 0.9, 0.3), (0.9, 0.4, 0.9), (1.0, 0.6, 0.2)])
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if random.random() < 0.6:
                    px, py = (fx+dx) % size, (fy+dy) % size
                    idx = (py * size + px) * 4
                    pixels[idx] = color[0]
                    pixels[idx+1] = color[1]
                    pixels[idx+2] = color[2]

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_logo(name="LogoCity", size=128, seed=88):
    """Logo brillante tipo ciudad/rascacielos."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Fondo oscuro
    for y in range(size):
        for x in range(size):
            put(x, y, 0.02, 0.02, 0.05)

    # Texto/Logo estilizado: tres rascacielos
    colores = [(1.0, 0.95, 0.85), (0.4, 0.85, 1.0), (1.0, 0.6, 0.3)]
    alturas_edifs = [int(size*0.65), int(size*0.80), int(size*0.55)]
    anchos_edifs = [18, 25, 16]
    x_inicio = (size - (sum(anchos_edifs) + 20)) // 2

    x_actual = x_inicio
    for i, (h, w, color) in enumerate(zip(alturas_edifs, anchos_edifs, colores)):
        # Edificio
        y_base = size - 15
        for dy in range(h):
            for dx in range(w):
                if 0 <= x_actual + dx < size and 0 <= y_base - dy < size:
                    put(x_actual + dx, y_base - dy, color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)
        # Ventanas brillantes
        for vy in range(0, h, 4):
            for vx in range(2, w-2, 3):
                if random.random() < 0.7:
                    wx = x_actual + vx
                    wy = y_base - vy - 1
                    if 0 <= wx < size and 0 <= wy < size:
                        put(wx, wy, color[0], color[1], color[2])
        x_actual += w + 10

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas mejoradas...")
tex_piso = tex_piso_brillante()
tex_cityscape = tex_pantalla_cityscape()
tex_jardin = tex_jardin_vertical()
tex_logo_img = tex_logo()
print("✅ Texturas listas")

# ============== MATERIALES ==============
def make_pbr(name, base_color, roughness, metallic, textura=None,
             emissive=None, emissive_strength=0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    if textura:
        tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.image = textura
        mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
        uv_node.uv_map = "UVMap"
        mat.node_tree.links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])

    if emissive:
        try:
            bsdf.inputs['Emission Color'].default_value = (*emissive, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emissive_strength
        except:
            pass

    return mat

# Materiales estructurales
mat_piso = make_pbr("PisoBrillante", (0.08, 0.09, 0.11), 0.18, 0.1, tex_piso)
mat_pared_oscura = make_pbr("ParedOscura", (0.10, 0.12, 0.16), 0.65, 0.0)
mat_pared_clara = make_pbr("ParedClara", (0.55, 0.58, 0.62), 0.5, 0.0)
mat_techo = make_pbr("Techo", (0.15, 0.17, 0.20), 0.7, 0.0)
mat_viga = make_pbr("VigaMetal", (0.08, 0.08, 0.10), 0.35, 0.8)
mat_metal_negro = make_pbr("MetalNegro", (0.03, 0.03, 0.04), 0.20, 0.95)

# LEDs emisivos
mat_led_cian = make_pbr("LEDCian", (0.0, 0.85, 1.0), 0.2, 0.0,
                         emissive=(0.0, 0.85, 1.0), emissive_strength=20.0)
mat_led_magenta = make_pbr("LEDMagenta", (1.0, 0.2, 0.8), 0.2, 0.0,
                            emissive=(1.0, 0.2, 0.8), emissive_strength=15.0)
mat_led_blanco = make_pbr("LEDBlanco", (1.0, 0.95, 0.9), 0.2, 0.0,
                           emissive=(1.0, 0.95, 0.9), emissive_strength=18.0)
mat_led_amarillo = make_pbr("LEDAmarillo", (1.0, 0.85, 0.3), 0.2, 0.0,
                             emissive=(1.0, 0.85, 0.3), emissive_strength=15.0)
mat_led_strip = make_pbr("LEDStripBlanco", (1.0, 1.0, 1.0), 0.2, 0.0,
                          emissive=(1.0, 0.95, 0.85), emissive_strength=10.0)
mat_led_strip_azul = make_pbr("LEDStripAzul", (0.3, 0.6, 1.0), 0.2, 0.0,
                               emissive=(0.3, 0.6, 1.0), emissive_strength=8.0)
mat_led_strip_magenta = make_pbr("LEDStripMagenta", (1.0, 0.2, 0.8), 0.2, 0.0,
                                  emissive=(1.0, 0.2, 0.8), emissive_strength=8.0)

# Pantallas
mat_pantalla = make_pbr("PantallaLED", (0.5, 0.5, 0.5), 0.05, 0.0, tex_cityscape,
                        emissive=(0.6, 0.6, 0.6), emissive_strength=3.5)
mat_pantalla_piso = make_pbr("PantallaPiso", (0.3, 0.4, 0.7), 0.05, 0.0,
                              emissive=(0.3, 0.4, 0.7), emissive_strength=4.0)

# Showroom
mat_showroom_base = make_pbr("ShowroomBase", (0.75, 0.77, 0.80), 0.25, 0.15)
mat_showroom_top = make_pbr("ShowroomTop", (0.20, 0.22, 0.25), 0.35, 0.3)

# Maquetas
mat_maqueta_edificio = make_pbr("MaquetaEdificio", (0.12, 0.12, 0.15), 0.5, 0.1)
mat_maqueta_ventana = make_pbr("MaquetaVentana", (1.0, 0.92, 0.65), 0.2, 0.0,
                                emissive=(1.0, 0.92, 0.65), emissive_strength=8.0)
mat_maqueta_ventana_azul = make_pbr("MaquetaVentanaAzul", (0.4, 0.85, 1.0), 0.2, 0.0,
                                     emissive=(0.4, 0.85, 1.0), emissive_strength=8.0)
mat_maqueta_ventana_mag = make_pbr("MaquetaVentanaMag", (1.0, 0.4, 0.85), 0.2, 0.0,
                                    emissive=(1.0, 0.4, 0.85), emissive_strength=8.0)

# Decoración
mat_planta = make_pbr("Planta", (0.15, 0.42, 0.12), 0.85, 0.0)
mat_jardin_v = make_pbr("JardinVertical", (0.20, 0.45, 0.18), 0.9, 0.0, tex_jardin)
mat_logo = make_pbr("LogoBrillante", (1.0, 0.85, 0.4), 0.3, 0.0, tex_logo_img,
                     emissive=(1.0, 0.85, 0.4), emissive_strength=6.0)

# Cristal
mat_cristal = make_pbr("Cristal", (0.6, 0.7, 0.85), 0.05, 0.0)

print("🎨 Materiales listos")

# ============== HELPERS ==============
def add_box(parent, name, loc, size, mat, uv_unwrap=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if uv_unwrap:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
    for col in obj.users_collection:
        col.objects.unlink(obj)
    parent.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def add_cylinder(parent, name, loc, radius, depth, mat, axis='Z', vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc,
                                         vertices=vertices, end_fill_type='NGON')
    obj = bpy.context.active_object
    obj.name = name
    if axis == 'X':
        obj.rotation_euler = (0, math.radians(90), 0)
    elif axis == 'Y':
        obj.rotation_euler = (math.radians(90), 0, 0)
    for col in obj.users_collection:
        col.objects.unlink(obj)
    parent.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def add_torus(parent, name, loc, major_r, minor_r, mat, axis='Z',
              major_segments=64):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r,
                                       location=loc, major_segments=major_segments, minor_segments=16)
    obj = bpy.context.active_object
    obj.name = name
    if axis == 'Z':
        obj.rotation_euler = (math.radians(90), 0, 0)
    elif axis == 'X':
        obj.rotation_euler = (0, math.radians(90), 0)
    for col in obj.users_collection:
        col.objects.unlink(obj)
    parent.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

def add_sphere(parent, name, loc, radius, mat, segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=segments)
    obj = bpy.context.active_object
    obj.name = name
    for col in obj.users_collection:
        col.objects.unlink(obj)
    parent.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# ============== ESTRUCTURA DE LA SALA ==============
print("🏛️  Sala de doble altura...")
add_box(sala, "piso",
        (0, 0, -0.05),
        (ANCHO, PROFUNDO, 0.1),
        mat_piso, uv_unwrap=True)

add_box(sala, "techo",
        (0, 0, ALTURA + 0.1),
        (ANCHO, PROFUNDO, 0.15),
        mat_techo)

# Paredes
add_box(sala, "pared_trasera",
        (0, -PROFUNDO/2, ALTURA/2),
        (ANCHO, 0.25, ALTURA),
        mat_pared_oscura)
add_box(sala, "pared_derecha",
        (ANCHO/2, 0, ALTURA/2),
        (0.25, PROFUNDO, ALTURA),
        mat_pared_clara)
add_box(sala, "pared_izquierda",
        (-ANCHO/2, 0, ALTURA/2),
        (0.25, PROFUNDO, ALTURA),
        mat_pared_oscura)
add_box(sala, "pared_frontal",
        (0, PROFUNDO/2, ALTURA/2),
        (ANCHO, 0.25, ALTURA),
        mat_pared_oscura)

# Jardin vertical en pared trasera
print("🌿 Jardin vertical...")
add_box(detalles, "jardin_vertical",
        (0, -PROFUNDO/2 + 0.15, 3.5),
        (ANCHO - 8, 0.1, 4.0),
        mat_jardin_v, uv_unwrap=True)

# Vigas del techo
print("🔩 Vigas metalicas...")
n_vigas_x = 8
n_vigas_y = 6
for i in range(n_vigas_x):
    x = -ANCHO/2 + (i + 0.5) * (ANCHO / n_vigas_x)
    add_box(sala, f"viga_X_{i}",
            (x, 0, ALTURA - 0.2),
            (0.15, PROFUNDO, 0.4),
            mat_viga)
for i in range(n_vigas_y):
    y = -PROFUNDO/2 + (i + 0.5) * (PROFUNDO / n_vigas_y)
    add_box(sala, f"viga_Y_{i}",
            (0, y, ALTURA - 0.2),
            (ANCHO, 0.15, 0.4),
            mat_viga)

# ============== PANTALLAS LED CURVAS ==============
print("📺 Pantallas LED curvas...")
# Pared izquierda - 3 pantallas gigantes
for i in range(3):
    y_centro = -PROFUNDO/2 + 3.0 + i * 4.5
    add_cylinder(pantallas, f"pantalla_curva_{i}",
                 (-ANCHO/2 - 5.5, y_centro, 2.8),
                 8, 3.5, mat_pantalla, axis='X', vertices=32)
# Pared derecha - 2 pantallas
for i in range(2):
    y_centro = PROFUNDO/2 - 3.0 - i * 3.5
    add_cylinder(pantallas, f"pantalla_curva_R_{i}",
                 (ANCHO/2 + 3.5, y_centro, 2.5),
                 5, 2.5, mat_pantalla, axis='X', vertices=32)

# ============== ANILLOS LED SUSPENDIDOS (multiples) ==============
print("💍 Anillos LED suspendidos con varios colores...")
# Anillos principales (cian, el color de la referencia)
altura_anillos = 5.8
radios_anillos = [3.2, 4.6, 6.4]
for i, radio in enumerate(radios_anillos):
    add_torus(leds, f"anillo_LED_principal_{i}",
              (0, 0, altura_anillos),
              radio, 0.10,
              mat_led_cian, axis='Z')

# Anillos secundarios (magenta + amarillo, decorativos)
for i, (radio, mat, z) in enumerate([
    (2.0, mat_led_magenta, 4.5),
    (7.5, mat_led_amarillo, 6.2),
    (1.2, mat_led_cian, 4.0),
    (8.5, mat_led_blanco, 6.5),
]):
    add_torus(leds, f"anillo_decor_{i}",
              (0, 0, z),
              radio, 0.06,
              mat, axis='Z')

# Anillo horizonte cerca del techo
add_torus(leds, "anillo_horizonte",
          (0, 0, ALTURA - 1.0),
          9.0, 0.05,
          mat_led_blanco, axis='Z')

# ============== SHOWROOM CIRCULAR CENTRAL ==============
print("🏛️  Showroom circular central...")
add_cylinder(showroom_col, "showroom_base",
             (0, 0, ALTURA_SHOWROOM/2),
             RADIO_SHOWROOM + 0.3, ALTURA_SHOWROOM,
             mat_showroom_base, axis='Z')
add_cylinder(showroom_col, "showroom_top",
             (0, 0, ALTURA_SHOWROOM + 0.05),
             RADIO_SHOWROOM, 0.1,
             mat_showroom_top, axis='Z')
add_torus(showroom_col, "showroom_LED_inferior",
          (0, 0, ALTURA_SHOWROOM - 0.1),
          RADIO_SHOWROOM + 0.32, 0.05,
          mat_led_strip, axis='Z')
add_torus(showroom_col, "showroom_LED_superior",
          (0, 0, ALTURA_SHOWROOM + 0.1),
          RADIO_SHOWROOM + 0.32, 0.04,
          mat_led_strip_magenta, axis='Z')

# Maqueta de ciudad con rascacielos más altos
print("🏙️  Maqueta con rascacielos más altos...")
random.seed(99)
n_maquetas = 70
tipos_ventana = [mat_maqueta_ventana, mat_maqueta_ventana_azul, mat_maqueta_ventana_mag]
for i in range(n_maquetas):
    ang = (i / n_maquetas) * 2 * math.pi + random.uniform(-0.15, 0.15)
    radio_maq = random.uniform(0, RADIO_SHOWROOM - 0.4)
    x = radio_maq * math.cos(ang)
    y = radio_maq * math.sin(ang)

    # Rascacielos más altos y variados
    categoria = random.random()
    if categoria < 0.15:
        # Rascacielos icónico (muy alto)
        h = random.uniform(0.9, 1.4)
        w = random.uniform(0.10, 0.14)
    elif categoria < 0.4:
        # Torre mediana
        h = random.uniform(0.5, 0.8)
        w = random.uniform(0.08, 0.12)
    else:
        # Edificio bajo
        h = random.uniform(0.15, 0.4)
        w = random.uniform(0.06, 0.10)

    d = w * random.uniform(0.8, 1.2)
    add_box(showroom_col, f"maq_edif_{i}",
            (x, y, ALTURA_SHOWROOM + 0.1 + h/2),
            (w, d, h),
            mat_maqueta_edificio)
    # Antena para rascacielos altos
    if categoria < 0.15:
        add_box(showroom_col, f"maq_antena_{i}",
                (x, y, ALTURA_SHOWROOM + 0.1 + h + 0.05),
                (0.01, 0.01, 0.1),
                mat_metal_negro)

    # Ventanas iluminadas (muchas mas, con colores variados)
    n_vent_filas = max(1, int(h / 0.06))
    for vf in range(n_vent_filas):
        for vc in range(max(1, int(w / 0.05))):
            if random.random() < 0.55:
                vx = x + random.uniform(-w*0.35, w*0.35)
                vy = y + random.uniform(-d*0.35, d*0.35)
                vz = ALTURA_SHOWROOM + 0.1 + 0.05 + vf * (h * 0.8 / n_vent_filas)
                mat_vent = random.choice(tipos_ventana)
                add_box(showroom_col, f"maq_vent_{i}_{vf}_{vc}",
                        (vx, vy, vz),
                        (0.012, 0.012, 0.02),
                        mat_vent)

# Spotlights sobre el showroom (más fuertes)
print("💡 Spotlights dramaticos sobre el showroom...")
for i in range(6):
    ang = i * (2*math.pi/6)
    r = 2.2
    x = r * math.cos(ang)
    y = r * math.sin(ang)
    bpy.ops.object.light_add(type='SPOT', location=(x, y, ALTURA - 0.4))
    spot = bpy.context.active_object
    spot.name = f"spot_showroom_{i}"
    spot.data.energy = 350  # más fuerte
    spot.data.color = (1.0, 0.95, 0.85)
    spot.data.spot_size = math.radians(25)
    direction = Vector((0, 0, ALTURA_SHOWROOM)) - spot.location
    spot.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    for col in spot.users_collection:
        col.objects.unlink(spot)
    leds.objects.link(spot)

# ============== LED STRIPS PERIMETRALES ==============
print("✨ LED strips perimetrales...")
add_box(leds, "zocalo_izq",
        (-ANCHO/2 + 0.2, 0, 0.18),
        (0.06, PROFUNDO - 0.5, 0.35),
        mat_led_strip_azul)
add_box(leds, "zocalo_der",
        (ANCHO/2 - 0.2, 0, 0.18),
        (0.06, PROFUNDO - 0.5, 0.35),
        mat_led_strip_azul)
add_box(leds, "zocalo_trasero",
        (0, -PROFUNDO/2 + 0.2, 0.18),
        (ANCHO - 0.5, 0.06, 0.35),
        mat_led_strip_magenta)
add_box(leds, "zocalo_frontal",
        (0, PROFUNDO/2 - 0.2, 0.18),
        (ANCHO - 0.5, 0.06, 0.35),
        mat_led_strip_azul)

# LED strip en unión techo-pared
for fachada in ["X", "Xn", "Y", "Yn"]:
    if fachada == "X":
        loc = (ANCHO/2 - 0.06, 0, ALTURA - 0.5)
        size = (0.04, PROFUNDO, 0.08)
    elif fachada == "Xn":
        loc = (-ANCHO/2 + 0.06, 0, ALTURA - 0.5)
        size = (0.04, PROFUNDO, 0.08)
    elif fachada == "Y":
        loc = (0, PROFUNDO/2 - 0.06, ALTURA - 0.5)
        size = (ANCHO, 0.04, 0.08)
    else:
        loc = (0, -PROFUNDO/2 + 0.06, ALTURA - 0.5)
        size = (ANCHO, 0.04, 0.08)
    add_box(leds, f"led_techo_{fachada}", loc, size, mat_led_cian)

# ============== SEGUNDO SHOWROOM ==============
print("🏛️  Segundo showroom...")
add_cylinder(showroom_col, "showroom2_base",
             (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.4),
             2.0, 0.8, mat_showroom_base, axis='Z')
add_cylinder(showroom_col, "showroom2_top",
             (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.85),
             1.85, 0.05, mat_showroom_top, axis='Z')
add_torus(showroom_col, "showroom2_LED",
          (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.4),
          2.05, 0.04, mat_led_strip_azul, axis='Z')

random.seed(44)
for i in range(20):
    ang = random.uniform(0, 2*math.pi)
    r = random.uniform(0, 1.5)
    x = ANCHO/2 - 6 + r * math.cos(ang)
    y = -PROFUNDO/2 + 4 + r * math.sin(ang)
    h = random.uniform(0.2, 0.7)
    w = random.uniform(0.06, 0.12)
    add_box(showroom_col, f"show2_maq_{i}",
            (x, y, 0.95 + h/2),
            (w, w, h),
            mat_maqueta_edificio)
    # Ventanas
    for vf in range(max(1, int(h/0.08))):
        if random.random() < 0.6:
            add_box(showroom_col, f"show2_vent_{i}_{vf}",
                    (x + random.uniform(-w/3, w/3), y + random.uniform(-w/3, w/3),
                     0.95 + 0.05 + vf * 0.06),
                    (0.01, 0.01, 0.015),
                    random.choice(tipos_ventana))

# ============== PANTALLAS LED EN EL PISO ==============
print("📺 Pantallas LED en el piso...")
for i in range(4):
    pos_x = random.uniform(-8, 8)
    pos_y = random.uniform(-5, 5)
    # Evitar que caigan encima del showroom
    if math.sqrt(pos_x**2 + pos_y**2) < RADIO_SHOWROOM + 1:
        continue
    add_box(pantallas, f"pantalla_piso_{i}",
            (pos_x, pos_y, 0.05),
            (1.5, 1.5, 0.08),
            mat_pantalla_piso)

# ============== CARTEL LUMINOSO EN PARED ==============
print("💡 Cartel luminoso...")
add_box(detalles, "cartel_principal",
        (-ANCHO/2 + 0.3, -3, 4.5),
        (0.05, 4, 1.2),
        mat_logo)
add_box(detalles, "cartel_lateral",
        (ANCHO/2 - 0.3, -3, 4.5),
        (0.05, 3, 0.8),
        mat_logo)

# ============== PERSONAS (silueta low-poly) ==============
print("👤 Personas en la sala...")
random.seed(33)
def agregar_persona(parent, x, y):
    """Persona stylized: cabeza + cuerpo + piernas como cilindros simples."""
    z_base = 0
    # Cuerpo
    add_box(parent, f"persona_{x}_{y}_cuerpo",
            (x, y, z_base + 0.9),
            (0.25, 0.20, 0.7),
            mat_metal_negro)
    # Cabeza
    add_sphere(parent, f"persona_{x}_{y}_cabeza",
               (x, y, z_base + 1.45), 0.13, mat_metal_negro, segments=12)
    # Piernas (cilindros)
    add_cylinder(parent, f"persona_{x}_{y}_pierna_izq",
                 (x - 0.07, y, z_base + 0.35),
                 0.07, 0.7, mat_metal_negro, axis='Z', vertices=8)
    add_cylinder(parent, f"persona_{x}_{y}_pierna_der",
                 (x + 0.07, y, z_base + 0.35),
                 0.07, 0.7, mat_metal_negro, axis='Z', vertices=8)

# 5 personas dispersas por la sala
for i in range(5):
    px = random.uniform(-10, 10)
    py = random.uniform(-6, 6)
    if math.sqrt(px**2 + py**2) < RADIO_SHOWROOM + 1.5:
        continue
    agregar_persona(personas, px, py)

# ============== PASARELA ELEVADA ==============
print("🌉 Pasarela elevada...")
# Pasarela semicircular alrededor del showroom
n_segmentos = 16
radio_pasarela = RADIO_SHOWROOM + 2.5
altura_pasarela = 1.5
for i in range(n_segmentos):
    ang = i * (2 * math.pi / n_segmentos)
    x = radio_pasarela * math.cos(ang)
    y = radio_pasarela * math.sin(ang)
    if abs(y) > PROFUNDO/2 - 1: continue  # no salir de la sala
    add_box(detalles, f"pasarela_{i}",
            (x, y, altura_pasarela),
            (1.2, 0.8, 0.15),
            mat_metal_negro)
    # Baranda de cristal a los lados
    add_box(detalles, f"baranda_pas_{i}_ext",
            (x * (radio_pasarela + 0.4)/radio_pasarela, y * (radio_pasarela + 0.4)/radio_pasarela,
             altura_pasarela + 0.5),
            (1.2, 0.05, 1.0),
            mat_cristal)

# Escalones para subir a la pasarela
for j in range(5):
    add_box(detalles, f"escalon_{j}",
            (radio_pasarela + 1.2, -PROFUNDO/2 + 1, j * 0.3),
            (1.2, 0.4, 0.16),
            mat_metal_negro)

# ============== DECORACION EXTRA ==============
print("🌿 Plantas + macetas + sillas...")
# Plantas
for i, (x, y) in enumerate([(-7, -5), (-7, 5), (7, -5), (7, 5), (-11, 0), (11, 0)]):
    add_box(sala, f"maceta_{i}",
            (x, y, 0.3),
            (0.5, 0.5, 0.6),
            mat_metal_negro)
    add_sphere(sala, f"planta_{i}",
               (x, y, 0.95), 0.5, mat_planta, segments=16)

# Sillas
for x in [-9, -7, 7, 9]:
    for y in [-5, 0, 5]:
        add_cylinder(sala, f"silla_{x}_{y}",
                     (x, y, 0.25),
                     0.5, 0.5, mat_metal_negro, axis='Z', vertices=16)

# Mostrador curvo a la izquierda
for i in range(8):
    ang = math.pi - (i + 0.5) * (math.pi / 8)
    x = -ANCHO/2 + 6 * math.cos(ang)
    y = 4 * math.sin(ang)
    add_box(sala, f"mostrador_{i}",
            (x, y, 0.5),
            (0.6, 1.2, 1.0),
            mat_showroom_base)

# ============== ILUMINACION PRINCIPAL ==============
print("☀️ Iluminacion dramatica 3-puntos...")

# KEY LIGHT - Spot fuerte desde el frente-arriba
bpy.ops.object.light_add(type='SPOT', location=(8, 12, 6.5))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 1500
key.data.color = (1.0, 0.95, 0.88)
key.data.spot_size = math.radians(50)
direction = Vector((0, 0, 2)) - key.location
key.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
for col in key.users_collection:
    col.objects.unlink(key)
leds.objects.link(key)

# FILL LIGHT - Area suave azul desde el otro lado
bpy.ops.object.light_add(type='AREA', location=(-10, -8, 5))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 200
fill.data.color = (0.4, 0.65, 1.0)
fill.data.size = 20
for col in fill.users_collection:
    col.objects.unlink(fill)
leds.objects.link(fill)

# RIM LIGHT - Detras, para silueta
bpy.ops.object.light_add(type='AREA', location=(-5, -15, 4))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 350
rim.data.color = (1.0, 0.4, 0.8)  # magenta para rim dramático
rim.data.size = 15
for col in rim.users_collection:
    col.objects.unlink(rim)
leds.objects.link(rim)

# AMBIENT - General bajo
bpy.ops.object.light_add(type='AREA', location=(0, 0, ALTURA - 0.3))
ambient = bpy.context.active_object
ambient.name = "Ambient"
ambient.data.energy = 80
ambient.data.color = (0.7, 0.85, 1.0)
ambient.data.size = 25
for col in ambient.users_collection:
    col.objects.unlink(ambient)
leds.objects.link(ambient)

# ============== CAMARA ==============
print("📷 Camara...")
bpy.ops.object.camera_add(location=(0, PROFUNDO/2 - 5, 1.6))
cam = bpy.context.active_object
cam.name = "CamShowroom"
target = Vector((0, 0, 1.5))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 26

bpy.context.scene.camera = cam

# ============== SKY ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links
for node in list(world_nodes):
    world_nodes.remove(node)

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.015, 0.02, 0.04, 1.0)
bg.inputs['Strength'].default_value = 0.4

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(bg.outputs['Background'], out.inputs['Surface'])

# ============== RENDER ==============
print("🎨 Renderizando...")
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.exposure = 1.2
bpy.context.scene.eevee.taa_render_samples = 96
# Bloom fuerte para que los LEDs brillen mucho
try:
    bpy.context.scene.eevee.use_bloom = True
    bpy.context.scene.eevee.bloom_intensity = 0.8
    bpy.context.scene.eevee.bloom_threshold = 0.6
except AttributeError:
    pass

# ============== GUARDAR ==============
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print(f"\n✅ Guardado: {OUTPUT}")

preview = OUTPUT.replace(".blend", "_preview.png")
bpy.context.scene.render.filepath = preview
bpy.ops.render.render(write_still=True)
print(f"🖼️  Preview: {preview}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
destino = os.path.join(IMGS_DIR, f"render_{timestamp}.png")
shutil.move(preview, destino)
print(f"📁 Movido: {destino}")

link = os.path.join(IMGS_DIR, "render_ultimo.png")
if os.path.islink(link) or os.path.exists(link):
    os.remove(link)
os.symlink(os.path.basename(destino), link)
print(f"🔗 {os.path.basename(destino)}")

n_sala = len([o for o in bpy.data.objects if o.name in [obj.name for obj in sala.objects]])
n_show = len([o for o in bpy.data.objects if o.name in [obj.name for obj in showroom_col.objects]])
n_leds = len([o for o in bpy.data.objects if o.name in [obj.name for obj in leds.objects]])
n_pan = len([o for o in bpy.data.objects if o.name in [obj.name for obj in pantallas.objects]])
n_det = len([o for o in bpy.data.objects if o.name in [obj.name for obj in detalles.objects]])
n_per = len([o for o in bpy.data.objects if o.name in [obj.name for obj in personas.objects]])
print(f"📦 Sala:{n_sala} Show:{n_show} LEDs:{n_leds} Pan:{n_pan} Det:{n_det} Per:{n_per} Total:{n_sala+n_show+n_leds+n_pan+n_det+n_per}")
