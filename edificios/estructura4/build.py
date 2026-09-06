"""
estructura4.blend — Showroom interior premium (galería de experiencia urbana)

Inspirado en lobby/showroom de centro comercial o galería de ventas inmobiliaria:
- Sala de doble altura con vigas expuestas
- Showroom circular central con maqueta de ciudad iluminada
- 3 anillos LED suspendidos del techo (luces cian)
- Pantallas gigantes curvas con cityscape nocturno
- Pisos reflectantes oscuros
- LED strips perimetrales en bases
- Iluminacion nocturna dramatica con bloom
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

# Dimensiones de la sala
ANCHO = 30.0       # X
PROFUNDO = 18.0    # Y
ALTURA = 7.5       # doble altura (techo alto)

# Showroom central
RADIO_SHOWROOM = 3.5
ALTURA_SHOWROOM = 0.7

random.seed(2026)

# ============== LIMPIAR ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

# ============== COLLECTIONS ==============
sala = bpy.data.collections.new("Sala")
bpy.context.scene.collection.children.link(sala)
showroom_col = bpy.data.collections.new("ShowroomCentral")
bpy.context.scene.collection.children.link(showroom_col)
leds = bpy.data.collections.new("IluminacionLED")
bpy.context.scene.collection.children.link(leds)
pantallas = bpy.data.collections.new("Pantallas")
bpy.context.scene.collection.children.link(pantallas)

# ============== TEXTURAS ==============
def img_vacia(name, size=256):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    img.pixels.foreach_set([0.0] * (size * size * 4))
    img.pack()
    return img

def tex_piso_reflectante(name="PisoReflectante", size=512, seed=11):
    """Piso oscuro con acabado tipo concreto pulido o marmol negro."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base gris muy oscuro
    for y in range(size):
        for x in range(size):
            put(x, y, 0.10, 0.11, 0.13)

    # Variacion sutil (juntas de placas)
    for junta_y in range(0, size, 128):
        for x in range(size):
            put(x, junta_y, 0.06, 0.07, 0.08)
            if junta_y + 1 < size:
                put(x, junta_y+1, 0.07, 0.08, 0.09)
    for junta_x in range(0, size, 128):
        for y in range(size):
            put(junta_x, y, 0.06, 0.07, 0.08)
            if junta_x + 1 < size:
                put(junta_x+1, y, 0.07, 0.08, 0.09)

    # Highlights sutiles (brillo del material pulido)
    for _ in range(100):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        radio = random.randint(8, 20)
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                d = math.sqrt(dx*dx + dy*dy)
                if d <= radio:
                    factor = 1 - (d / radio)
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = (py * size + px) * 4
                        pixels[idx] += factor * 0.04
                        pixels[idx+1] += factor * 0.04
                        pixels[idx+2] += factor * 0.05

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_pantalla_cityscape(name="CityscapeNocturno", size=512, seed=22):
    """Pantalla LED con imagen nocturna de rascacielos iluminados."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Cielo nocturno (gradiente oscuro arriba, naranja en el horizonte)
    for y in range(size):
        f = y / size
        if f < 0.4:
            # arriba: azul oscuro
            r = 0.02 + f * 0.05
            g = 0.04 + f * 0.10
            b = 0.15 + f * 0.20
        elif f < 0.7:
            # horizonte: morado-azul
            r = 0.04 + (f - 0.4) * 0.15
            g = 0.05 + (f - 0.4) * 0.10
            b = 0.25 + (f - 0.4) * 0.20
        else:
            # ciudad: oscuro
            r = 0.05
            g = 0.05
            b = 0.08
        for x in range(size):
            r_var = r + random.uniform(-0.02, 0.02)
            g_var = g + random.uniform(-0.02, 0.02)
            b_var = b + random.uniform(-0.02, 0.02)
            put(x, y, max(0, min(1, r_var)), max(0, min(1, g_var)), max(0, min(1, b_var)))

    # Edificios (siluetas iluminadas)
    x_actual = 0
    while x_actual < size:
        ancho_edif = random.randint(15, 50)
        alto_edif = random.randint(int(size*0.3), int(size*0.85))
        y_base = size - int(size * 0.25)  # sobre la "ciudad"
        # Cuerpo del edificio (silueta oscura)
        for dy in range(alto_edif):
            for dx in range(ancho_edif):
                if x_actual + dx < size and y_base - dy >= 0:
                    put(x_actual + dx, y_base - dy, 0.04, 0.05, 0.08)

        # Ventanas iluminadas (puntos amarillos)
        for v_y in range(0, alto_edif, 4):
            for v_x in range(2, ancho_edif-2, 4):
                if random.random() < 0.4:
                    wx = x_actual + v_x
                    wy = y_base - v_y - 2
                    if 0 <= wx < size and 0 <= wy < size:
                        # Color de ventana (amarillo calido o blanco o apagado)
                        r_color = random.choice([(1.0, 0.9, 0.5), (0.95, 0.95, 0.9), (0.6, 0.4, 0.2), (1.0, 0.6, 0.3)])
                        put(wx, wy, *r_color)

        x_actual += ancho_edif + random.randint(2, 8)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_cielo_nocturno(name="CieloNocturno", size=256, seed=33):
    """Cielo nocturno oscuro."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    for y in range(size):
        f = y / size
        for x in range(size):
            r = 0.01 + (1-f) * 0.04
            g = 0.02 + (1-f) * 0.06
            b = 0.08 + (1-f) * 0.15
            put(x, y, r, g, b)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas...")
tex_piso = tex_piso_reflectante()
tex_cityscape = tex_pantalla_cityscape()
tex_cielo = tex_cielo_nocturno()
print("✅ Texturas listas")

# ============== MATERIALES ==============
def make_pbr(name, base_color, roughness, metallic, textura=None, emissive=None, emissive_strength=0):
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

    # Emissive (para LEDs y pantallas)
    if emissive:
        try:
            bsdf.inputs['Emission Color'].default_value = (*emissive, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emissive_strength
        except:
            pass

    return mat

# Materiales de la sala
mat_piso = make_pbr("PisoReflectante", (0.10, 0.11, 0.13), 0.25, 0.2, tex_piso)
mat_pared_oscura = make_pbr("ParedOscura", (0.12, 0.14, 0.18), 0.7, 0.0)
mat_pared_clara = make_pbr("ParedClara", (0.45, 0.47, 0.50), 0.6, 0.0)
mat_techo = make_pbr("Techo", (0.18, 0.20, 0.22), 0.6, 0.0)
mat_viga = make_pbr("VigaMetal", (0.10, 0.10, 0.11), 0.4, 0.7)
mat_metal_negro = make_pbr("MetalNegro", (0.04, 0.04, 0.05), 0.25, 0.9)

# Materiales LED (emissive)
mat_led_cian = make_pbr("LEDCian", (0.0, 0.8, 1.0), 0.3, 0.0,
                         emissive=(0.0, 0.8, 1.0), emissive_strength=15.0)
mat_led_blanco = make_pbr("LEDBlanco", (1.0, 0.95, 0.85), 0.3, 0.0,
                           emissive=(1.0, 0.95, 0.85), emissive_strength=12.0)
mat_led_calido = make_pbr("LEDCalido", (1.0, 0.85, 0.6), 0.3, 0.0,
                           emissive=(1.0, 0.85, 0.6), emissive_strength=10.0)
mat_led_strip = make_pbr("LEDStripBlanco", (1.0, 1.0, 1.0), 0.3, 0.0,
                          emissive=(1.0, 0.95, 0.85), emissive_strength=8.0)
mat_led_strip_azul = make_pbr("LEDStripAzul", (0.3, 0.6, 1.0), 0.3, 0.0,
                               emissive=(0.3, 0.6, 1.0), emissive_strength=6.0)

# Pantalla emisiva
mat_pantalla = make_pbr("PantallaLED", (0.5, 0.5, 0.5), 0.1, 0.0, tex_cityscape,
                        emissive=(0.5, 0.5, 0.5), emissive_strength=2.5)

# Showroom
mat_showroom_base = make_pbr("ShowroomBase", (0.60, 0.62, 0.65), 0.3, 0.2)
mat_showroom_top = make_pbr("ShowroomTop", (0.20, 0.22, 0.25), 0.4, 0.3)

# Maqueta ciudad
mat_maqueta_edificio = make_pbr("MaquetaEdificio", (0.15, 0.15, 0.18), 0.5, 0.1)
mat_maqueta_ventana = make_pbr("MaquetaVentana", (1.0, 0.95, 0.7), 0.2, 0.0)

# Verde para plantas
mat_planta = make_pbr("Planta", (0.15, 0.40, 0.12), 0.85, 0.0)

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

def add_cylinder(parent, name, loc, radius, depth, mat, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc)
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

def add_torus(parent, name, loc, major_r, minor_r, mat, axis='Z'):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_r, minor_radius=minor_r,
                                       location=loc, major_segments=64, minor_segments=16)
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

# ============== ESTRUCTURA DE LA SALA ==============
print("🏛️  Construyendo sala de doble altura...")

# Piso reflectante
add_box(sala, "piso",
        (0, 0, -0.05),
        (ANCHO, PROFUNDO, 0.1),
        mat_piso, uv_unwrap=True)

# Techo
add_box(sala, "techo",
        (0, 0, ALTURA + 0.1),
        (ANCHO, PROFUNDO, 0.15),
        mat_techo)

# Paredes perimetrales
# Pared trasera (-Y)
add_box(sala, "pared_trasera",
        (0, -PROFUNDO/2, ALTURA/2),
        (ANCHO, 0.25, ALTURA),
        mat_pared_oscura)
# Pared derecha (+X)
add_box(sala, "pared_derecha",
        (ANCHO/2, 0, ALTURA/2),
        (0.25, PROFUNDO, ALTURA),
        mat_pared_clara)
# Pared izquierda (-X)
add_box(sala, "pared_izquierda",
        (-ANCHO/2, 0, ALTURA/2),
        (0.25, PROFUNDO, ALTURA),
        mat_pared_oscura)
# Pared frontal (la camara mira hacia aca, asi que la dejamos abierta o con pared lejana)
add_box(sala, "pared_frontal",
        (0, PROFUNDO/2, ALTURA/2),
        (ANCHO, 0.25, ALTURA),
        mat_pared_oscura)

# Vigas expuestas del techo
print("🔩 Vigas metalicas del techo...")
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

# ============== PANTALLAS GIGANTES CURVAS ==============
print("📺 Pantallas LED curvas en pared izquierda...")
# Pantallas curvas: 3 paneles enormes apilados verticalmente
n_pantallas_x = 3
for i in range(n_pantallas_x):
    y_centro = -PROFUNDO/2 + 3.0 + i * 4.5
    # Crear panel curvo (cilindro seccionado)
    bpy.ops.mesh.primitive_cylinder_add(radius=8, depth=3.5,
                                          location=(-ANCHO/2 - 5.5, y_centro, 2.8),
                                          rotation=(0, math.radians(90), 0),
                                          vertices=32, end_fill_type='NOTHING')
    pantalla = bpy.context.active_object
    pantalla.name = f"pantalla_curva_{i}"
    # Cortar a la mitad visible
    # (Para simplicidad, dejo el cilindro completo, el lado no visible queda fuera)
    pantalla.data.materials.append(mat_pantalla)
    for col in pantalla.users_collection:
        col.objects.unlink(pantalla)
    pantallas.objects.link(pantalla)

# Pantallas curvas a la derecha (mas pequenas, decorativas)
for i in range(2):
    y_centro = PROFUNDO/2 - 3.0 - i * 3.5
    bpy.ops.mesh.primitive_cylinder_add(radius=5, depth=2.5,
                                          location=(ANCHO/2 + 3.5, y_centro, 2.5),
                                          rotation=(0, math.radians(90), 0),
                                          vertices=32, end_fill_type='NOTHING')
    pantalla = bpy.context.active_object
    pantalla.name = f"pantalla_curva_R_{i}"
    pantalla.data.materials.append(mat_pantalla)
    for col in pantalla.users_collection:
        col.objects.unlink(pantalla)
    pantallas.objects.link(pantalla)

# ============== 3 ANILLOS LED SUSPENDIDOS ==============
print("💍 3 anillos LED suspendidos del techo...")
# Anillos concentricos sobre el showroom central
altura_anillos = 5.5
radios_anillos = [3.0, 4.5, 6.5]
for i, radio in enumerate(radios_anillos):
    add_torus(leds, f"anillo_LED_{i}",
              (0, 0, altura_anillos),
              radio, 0.08,
              mat_led_cian, axis='Z')

# Anillo exterior mas ancho (en plano horizontal cerca del techo)
add_torus(leds, "anillo_horizonte",
          (0, 0, ALTURA - 1.2),
          8.5, 0.05,
          mat_led_blanco, axis='Z')

# ============== SHOWROOM CIRCULAR CENTRAL ==============
print("🏛️  Showroom circular central con maqueta...")

# Base circular (plataforma blanca pulida)
add_cylinder(showroom_col, "showroom_base",
             (0, 0, ALTURA_SHOWROOM/2),
             RADIO_SHOWROOM + 0.3, ALTURA_SHOWROOM,
             mat_showroom_base, axis='Z')

# Plataforma superior (donde va la maqueta)
add_cylinder(showroom_col, "showroom_top",
             (0, 0, ALTURA_SHOWROOM + 0.05),
             RADIO_SHOWROOM, 0.1,
             mat_showroom_top, axis='Z')

# LED strip en el borde inferior del showroom (la linea blanca que brilla)
add_torus(showroom_col, "showroom_LED_inferior",
          (0, 0, ALTURA_SHOWROOM - 0.1),
          RADIO_SHOWROOM + 0.32, 0.04,
          mat_led_strip, axis='Z')

# Maqueta de ciudad (edificios pequenos iluminados)
print("🏙️  Maqueta de ciudad iluminada en el showroom...")
random.seed(99)
n_maquetas = 60
for i in range(n_maquetas):
    # Distribuir en circulo sobre el showroom
    ang = (i / n_maquetas) * 2 * math.pi + random.uniform(-0.2, 0.2)
    radio_maq = random.uniform(0, RADIO_SHOWROOM - 0.5)
    x = radio_maq * math.cos(ang)
    y = radio_maq * math.sin(ang)
    h = random.uniform(0.15, 0.7)
    w = random.uniform(0.08, 0.18)
    d = random.uniform(0.08, 0.18)
    add_box(showroom_col, f"maq_edif_{i}",
            (x, y, ALTURA_SHOWROOM + 0.1 + h/2),
            (w, d, h),
            mat_maqueta_edificio)
    # Ventanas iluminadas (1-3 puntos por edificio)
    n_vent = random.randint(1, 3)
    for v in range(n_vent):
        vx = x + random.uniform(-w/3, w/3)
        vy = y + random.uniform(-d/3, d/3)
        vz = ALTURA_SHOWROOM + 0.1 + random.uniform(0.05, h - 0.05)
        add_box(showroom_col, f"maq_vent_{i}_{v}",
                (vx, vy, vz),
                (0.015, 0.015, 0.025),
                mat_maqueta_ventana)

# Spotlights enfocando el showroom desde arriba
print("💡 Spotlights sobre el showroom...")
for i in range(5):
    ang = i * (2*math.pi/5)
    r = 2.0
    x = r * math.cos(ang)
    y = r * math.sin(ang)
    bpy.ops.object.light_add(type='SPOT', location=(x, y, ALTURA - 0.5))
    spot = bpy.context.active_object
    spot.name = f"spot_showroom_{i}"
    spot.data.energy = 200
    spot.data.color = (1.0, 0.97, 0.90)
    spot.data.spot_size = math.radians(30)
    # Apuntar al centro del showroom
    direction = Vector((0, 0, ALTURA_SHOWROOM)) - spot.location
    spot.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    for col in spot.users_collection:
        col.objects.unlink(spot)
    leds.objects.link(spot)

# ============== LED STRIPS PERIMETRALES EN BASES ==============
print("✨ LED strips en bases...")
# Strip en base del showroom (ya hecho arriba)
# Strip en zocalos de las paredes
add_box(leds, "zocalo_izq",
        (-ANCHO/2 + 0.2, 0, 0.15),
        (0.05, PROFUNDO - 0.5, 0.3),
        mat_led_strip)
add_box(leds, "zocalo_der",
        (ANCHO/2 - 0.2, 0, 0.15),
        (0.05, PROFUNDO - 0.5, 0.3),
        mat_led_strip)
add_box(leds, "zocalo_trasero",
        (0, -PROFUNDO/2 + 0.2, 0.15),
        (ANCHO - 0.5, 0.05, 0.3),
        mat_led_strip_azul)

# Linea LED azul en interseccion pared/techo (el efecto del fondo de la referencia)
for fachada in ["X", "Xn", "Y", "Yn"]:
    if fachada == "X":
        loc = (ANCHO/2 - 0.05, 0, ALTURA - 0.6)
        size = (0.03, PROFUNDO, 0.06)
    elif fachada == "Xn":
        loc = (-ANCHO/2 + 0.05, 0, ALTURA - 0.6)
        size = (0.03, PROFUNDO, 0.06)
    elif fachada == "Y":
        loc = (0, PROFUNDO/2 - 0.05, ALTURA - 0.6)
        size = (ANCHO, 0.03, 0.06)
    else:
        loc = (0, -PROFUNDO/2 + 0.05, ALTURA - 0.6)
        size = (ANCHO, 0.03, 0.06)
    add_box(leds, f"led_techo_{fachada}", loc, size, mat_led_cian)

# ============== SEGUNDO SHOWROOM (A LA DERECHA) ==============
print("🏛️  Segundo showroom a la derecha...")
# Plataforma circular pequena
add_cylinder(showroom_col, "showroom2_base",
             (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.4),
             2.0, 0.8,
             mat_showroom_base, axis='Z')
add_cylinder(showroom_col, "showroom2_top",
             (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.85),
             1.85, 0.05,
             mat_showroom_top, axis='Z')
add_torus(showroom_col, "showroom2_LED",
          (ANCHO/2 - 6, -PROFUNDO/2 + 4, 0.4),
          2.02, 0.03,
          mat_led_strip, axis='Z')

# Edificios en este showroom
random.seed(44)
for i in range(15):
    ang = random.uniform(0, 2*math.pi)
    r = random.uniform(0, 1.5)
    x = ANCHO/2 - 6 + r * math.cos(ang)
    y = -PROFUNDO/2 + 4 + r * math.sin(ang)
    h = random.uniform(0.2, 0.6)
    w = random.uniform(0.06, 0.12)
    add_box(showroom_col, f"show2_maq_{i}",
            (x, y, 0.95 + h/2),
            (w, w, h),
            mat_maqueta_edificio)

# ============== DECORACION: PLANTAS Y OTROS ==============
print("🌿 Plantas decorativas...")
# Macetas con plantas cerca del showroom
for i, (x, y) in enumerate([(-6, -5), (-6, 5), (6, -5), (6, 5), (-10, 0)]):
    # Maceta
    add_box(sala, f"maceta_{i}",
            (x, y, 0.3),
            (0.5, 0.5, 0.6),
            mat_metal_negro)
    # Follaje
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, y, 0.95))
    planta = bpy.context.active_object
    planta.name = f"planta_{i}"
    planta.data.materials.append(mat_planta)
    for col in planta.users_collection:
        col.objects.unlink(planta)
    sala.objects.link(planta)

# Sillas decorativas (cilindros bajos)
print("🪑 Mobiliario...")
for x in [-9, -7, 7, 9]:
    for y in [-5, 0, 5]:
        add_cylinder(sala, f"silla_{x}_{y}",
                     (x, y, 0.25),
                     0.5, 0.5,
                     mat_metal_negro, axis='Z')

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
print("☀️ Iluminacion nocturna...")
# Ambient muy bajo (la sala es nocturna)
bpy.ops.object.light_add(type='AREA', location=(0, 0, ALTURA - 0.3))
ambient = bpy.context.active_object
ambient.data.energy = 100
ambient.data.color = (0.7, 0.85, 1.0)  # azul frio
ambient.data.size = 25
for col in ambient.users_collection:
    col.objects.unlink(ambient)
leds.objects.link(ambient)

# ============== CAMARA ==============
print("📷 Camara con vista frontal dramatica...")
# Camara al frente, ligeramente abajo, mirando al showroom central
bpy.ops.object.camera_add(location=(0, PROFUNDO/2 - 5, 1.5))
cam = bpy.context.active_object
cam.name = "CamShowroom"
target = Vector((0, 0, 1.5))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 24  # gran angular para capturar todo

bpy.context.scene.camera = cam

# ============== SKY (no se ve mucho en interior) ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links
for node in list(world_nodes):
    world_nodes.remove(node)

# Fondo negro azulado (noche interior)
bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.02, 0.03, 0.06, 1.0)
bg.inputs['Strength'].default_value = 0.5

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(bg.outputs['Background'], out.inputs['Surface'])

# ============== RENDER ==============
print("🎨 Renderizando...")
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080  # horizontal esta vez (como la ref)
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.exposure = 1.0
bpy.context.scene.eevee.taa_render_samples = 64
# Bloom activado para que los LEDs brillen
try:
    bpy.context.scene.eevee.use_bloom = True
    bpy.context.scene.eevee.bloom_intensity = 0.5
    bpy.context.scene.eevee.bloom_threshold = 0.8
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
print(f"📦 Sala: {n_sala}, Showroom: {n_show}, LEDs: {n_leds}, Pantallas: {n_pan}, Total: {n_sala+n_show+n_leds+n_pan}")
