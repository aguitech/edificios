"""
edificio2.blend — Torre residencial de lujo al atardecer

Inspirado en arquitectura contemporánea premium:
- ~25 pisos con fachada de cristal negro reflectante
- Balcones perimetrales en zigzag (voladizo variable por piso)
- Cornisas horizontales blancas gruesas entre cada piso
- Ventanas iluminadas color ambar (golden hour)
- Sky shader atardecer degradado naranja->magenta->azul
- Vista urbana con city skyline al fondo y el mar
"""

import bpy
import math
import os
import shutil
import random
from datetime import datetime
from mathutils import Vector

# ============== CONFIG ==============
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edificio2.blend")
REPO_DIR = os.path.dirname(OUTPUT)
IMGS_DIR = os.path.join(REPO_DIR, "imagenes")
os.makedirs(IMGS_DIR, exist_ok=True)

# Dimensiones de la torre
ANCHO = 14.0          # torre mas esbelta
PROFUNDO = 14.0
NUM_PISOS = 25
ALTURA_PISO = 3.0     # un poco mas bajo para que parezca residencial de lujo
ALTURA_TOTAL = NUM_PISOS * ALTURA_PISO
BALCON_BASE = 1.2     # balcon perimetral base
CORNISA_H = 0.45      # grosor de la cornisa blanca horizontal
VOLADIZO_EXTRA = 1.8  # cuanto sobresalen los balcones "grandes"

# ============== LIMPIAR ESCENA ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

# ============== COLLECTION ==============
torre = bpy.data.collections.new("TorreAtardecer")
bpy.context.scene.collection.children.link(torre)
entorno = bpy.data.collections.new("Entorno")
bpy.context.scene.collection.children.link(entorno)

# ============== TEXTURAS PROCEDURALES ==============
def img_blanca_vacia(name, size=512):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_fachada_cristal(name="CristalReflectante", size=512, seed=123):
    """Cristal oscuro reflectante con reflejos sutiles."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base oscura azul-negro
    for y in range(size):
        for x in range(size):
            put(x, y, 0.08, 0.10, 0.14)

    # Reflejos sutiles verticales (cielo reflejado en el cristal)
    for y in range(size):
        # Degradado de mas oscuro arriba a un poco mas claro abajo (reflejo del suelo)
        factor = y / size
        r = 0.08 + factor * 0.15
        g = 0.10 + factor * 0.12
        b = 0.14 + factor * 0.18
        for x in range(size):
            # Variacion sutil pixel-a-pixel
            r_var = r + (random.random() - 0.5) * 0.04
            g_var = g + (random.random() - 0.5) * 0.04
            b_var = b + (random.random() - 0.5) * 0.04
            put(x, y, max(0, min(1, r_var)), max(0, min(1, g_var)), max(0, min(1, b_var)))

    # Highlights horizontales (reflejos del sol)
    for refl_y in [int(size*0.2), int(size*0.45), int(size*0.7)]:
        for x in range(size):
            intensity = (math.sin(x * 0.05) + 1) / 2 * 0.3 + 0.7
            put(x, refl_y, 0.25 * intensity, 0.18 * intensity, 0.10 * intensity)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_ventanas_iluminadas(name="VentanasAmbar", size=512, seed=77):
    """Patrón de ventanas iluminadas cálido, apagadas y a media luz."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base cristal oscuro
    for y in range(size):
        for x in range(size):
            put(x, y, 0.05, 0.07, 0.10)

    # Grid de ventanas (4 columnas x 8 filas en el tile)
    cols, rows = 4, 8
    cell_w, cell_h = size / cols, size / rows
    ventana_w, ventana_h = cell_w * 0.7, cell_h * 0.7

    for fila in range(rows):
        for col in range(cols):
            # Centro de la ventana
            cx = int(col * cell_w + cell_w / 2)
            cy = int(fila * cell_h + cell_h / 2)
            w = int(ventana_w / 2)
            h = int(ventana_h / 2)

            # 30% iluminada completa, 20% a media luz, 20% tenue, 30% apagada
            r = random.random()
            if r < 0.30:
                # Totalmente iluminada (amarillo ambar)
                color = (1.0, 0.72, 0.25)
            elif r < 0.50:
                # Media luz (amarillo palido)
                color = (0.85, 0.65, 0.30)
            elif r < 0.70:
                # Tenue (casi transparente)
                color = (0.30, 0.25, 0.15)
            else:
                # Apagada
                color = (0.05, 0.07, 0.10)

            for dy in range(-h, h):
                for dx in range(-w, w):
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        # Borde de ventana (mas oscuro)
                        if abs(dx) > w*0.85 or abs(dy) > h*0.85:
                            put(px, py, 0.15, 0.10, 0.05)
                        else:
                            # Interior con variacion
                            r_var = color[0] * (0.85 + random.random() * 0.15)
                            g_var = color[1] * (0.85 + random.random() * 0.15)
                            b_var = color[2] * (0.85 + random.random() * 0.15)
                            put(px, py, r_var, g_var, b_var)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_cornisa(name="CornisaBlanca", size=256, seed=42):
    """Hormigon blanco arquitectónico premium."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base blanco
    for y in range(size):
        for x in range(size):
            put(x, y, 0.92, 0.91, 0.89)

    # Textura sutil de concreto arquitectonico
    for _ in range(200):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        radio = random.randint(1, 3)
        r = random.randint(225, 245) / 255
        g = random.randint(220, 240) / 255
        b = random.randint(215, 235) / 255
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                if dx*dx + dy*dy <= radio*radio:
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        put(px, py, r, g, b)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas premium...")
tex_cristal = tex_fachada_cristal()
tex_ventanas = tex_ventanas_iluminadas()
tex_cornisa = tex_cornisa()
print("✅ Texturas listas")

# ============== MATERIALES PBR ==============
def make_pbr(name, base_color, roughness, metallic, textura=None):
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
    return mat

# Materiales principales
mat_cristal_negro = make_pbr("CristalNegro", (0.08, 0.10, 0.14), 0.15, 0.0, tex_cristal)
mat_cristal_negro.node_tree.nodes["Principled BSDF"].inputs['Metallic'].default_value = 0.3
# Subir IOR para reflejo realista
for inp in mat_cristal_negro.node_tree.nodes["Principled BSDF"].inputs:
    if 'OR' in inp.name and inp.name != 'Base Color':
        inp.default_value = 1.45

mat_ventanas_ambar = make_pbr("VentanasAmbar", (1.0, 0.72, 0.25), 0.3, 0.0, tex_ventanas)
# Emissive para que las ventanas brillen de noche
bsdf_v = mat_ventanas_ambar.node_tree.nodes["Principled BSDF"]
try:
    bsdf_v.inputs['Emission Color'].default_value = (1.0, 0.6, 0.2, 1.0)
    bsdf_v.inputs['Emission Strength'].default_value = 2.5
except:
    pass

mat_cornisa = make_pbr("CornisaBlanca", (0.92, 0.91, 0.89), 0.5, 0.0, tex_cornisa)
mat_metal_negro = make_pbr("MetalNegro", (0.05, 0.05, 0.06), 0.25, 0.95)
mat_concreto_oscuro = make_pbr("ConcretoOscuro", (0.18, 0.18, 0.20), 0.7, 0.0)
mat_mar = make_pbr("Mar", (0.15, 0.25, 0.35), 0.4, 0.0)
mat_cielo_naranja = make_pbr("CieloAtardecer", (1.0, 0.5, 0.25), 0.9, 0.0)

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

random.seed(2026)  # reproducible

# ============== NUCLEO DE LA TORRE ==============
print("🏗️  Construyendo nucleo cristalino...")
add_box(torre, "nucleo", (0, 0, ALTURA_TOTAL/2),
        (ANCHO, PROFUNDO, ALTURA_TOTAL),
        mat_cristal_negro, uv_unwrap=True)

# Paneles de ventanas iluminadas (se aplican como "skin" sobre las fachadas)
# Fachada +X, -X, +Y, -Y: panel con la textura de ventanas iluminadas
add_box(torre, "panel_ventanas_X", (ANCHO/2 + 0.05, 0, ALTURA_TOTAL/2),
        (0.05, PROFUNDO - 0.2, ALTURA_TOTAL - 1.0),
        mat_ventanas_ambar)
add_box(torre, "panel_ventanas_Xn", (-ANCHO/2 - 0.05, 0, ALTURA_TOTAL/2),
        (0.05, PROFUNDO - 0.2, ALTURA_TOTAL - 1.0),
        mat_ventanas_ambar)
add_box(torre, "panel_ventanas_Y", (0, PROFUNDO/2 + 0.05, ALTURA_TOTAL/2),
        (ANCHO - 0.2, 0.05, ALTURA_TOTAL - 1.0),
        mat_ventanas_ambar)
add_box(torre, "panel_ventanas_Yn", (0, -PROFUNDO/2 - 0.05, ALTURA_TOTAL/2),
        (ANCHO - 0.2, 0.05, ALTURA_TOTAL - 1.0),
        mat_ventanas_ambar)

# ============== BALCONES ZIGZAG POR PISO ==============
# Patron irregular: cada piso tiene un nivel de voladizo distinto
# Los balcones envuelven perimetro completo (como el edificio anterior)
print("🌇 Construyendo balcones zigzag en cada piso...")
voladizos_por_piso = {}
for piso in range(1, NUM_PISOS):  # 1 a 24
    # Patrón irregular: a veces balcon chico, a veces balcon grande
    seed = (piso * 37) % 100
    if seed < 30:
        v = BALCON_BASE  # balcon normal
    elif seed < 60:
        v = BALCON_BASE + 0.5  # balcon medio
    elif seed < 85:
        v = BALCON_BASE + 1.0  # balcon grande
    else:
        v = BALCON_BASE + 1.5  # balcon gigante (terraza)
    voladizos_por_piso[piso] = v

for piso in range(1, NUM_PISOS):
    v = voladizos_por_piso[piso]
    z_suelo_piso = piso * ALTURA_PISO
    z_centro_losa = z_suelo_piso - CORNISA_H/2

    # Losa del balcon perimetral (los 4 lados)
    # Fachada +X
    add_box(torre, f"losa_X_{piso}",
            (ANCHO/2 + v/2, 0, z_centro_losa),
            (v, PROFUNDO, CORNISA_H),
            mat_concreto_oscuro)
    add_box(torre, f"losa_Xn_{piso}",
            (-ANCHO/2 - v/2, 0, z_centro_losa),
            (v, PROFUNDO, CORNISA_H),
            mat_concreto_oscuro)
    add_box(torre, f"losa_Y_{piso}",
            (0, PROFUNDO/2 + v/2, z_centro_losa),
            (ANCHO, v, CORNISA_H),
            mat_concreto_oscuro)
    add_box(torre, f"losa_Yn_{piso}",
            (0, -PROFUNDO/2 - v/2, z_centro_losa),
            (ANCHO, v, CORNISA_H),
            mat_concreto_oscuro)

    # Barandilla de cristal (negra, casi invisible como en la referencia)
    h_bar = 1.1
    add_box(torre, f"barandilla_X_{piso}",
            (ANCHO/2 + v, 0, z_centro_losa + CORNISA_H/2 + h_bar/2),
            (0.04, PROFUNDO - 1.0, h_bar),
            mat_metal_negro)
    add_box(torre, f"barandilla_Xn_{piso}",
            (-ANCHO/2 - v, 0, z_centro_losa + CORNISA_H/2 + h_bar/2),
            (0.04, PROFUNDO - 1.0, h_bar),
            mat_metal_negro)
    add_box(torre, f"barandilla_Y_{piso}",
            (0, PROFUNDO/2 + v, z_centro_losa + CORNISA_H/2 + h_bar/2),
            (ANCHO - 1.0, 0.04, h_bar),
            mat_metal_negro)
    add_box(torre, f"barandilla_Yn_{piso}",
            (0, -PROFUNDO/2 - v, z_centro_losa + CORNISA_H/2 + h_bar/2),
            (ANCHO - 1.0, 0.04, h_bar),
            mat_metal_negro)

# ============== CORNISAS HORIZONTALES BLANCAS (signature de la referencia) ==============
print("🪟 Cornisas blancas gruesas por piso (marca de la casa)...")
for piso in range(0, NUM_PISOS + 1):
    z_cornisa = piso * ALTURA_PISO - CORNISA_H/2 if piso > 0 else -CORNISA_H/2
    # Cornisa perimetral (anillo blanco que sobresale un poco)
    overh = 0.3  # sobresale 30cm del nucleo
    add_box(torre, f"cornisa_inf_{piso}",
            (0, 0, z_cornisa),
            (ANCHO + 2*overh, PROFUNDO + 2*overh, CORNISA_H),
            mat_cornisa)

# Cornisa en la AZOTEA (la "corona" gruesa arriba)
add_box(torre, "corona",
        (0, 0, ALTURA_TOTAL + 1.0),
        (ANCHO + 0.5, PROFUNDO + 0.5, 2.0),
        mat_cornisa)

# Caseta de maquinas / helipuerto (cubierta encima de la corona)
add_box(torre, "caseta", (-ANCHO/4, -PROFUNDO/4, ALTURA_TOTAL + 2.5),
        (ANCHO/2, PROFUNDO/2, 1.5),
        mat_metal_negro)

# ============== ILUMINACION INTERNA DE VENTANAS (puntos de luz) ==============
print("💡 Luces internas aleatorias (gente en casa)...")
for piso in range(1, NUM_PISOS + 1):
    z_piso = piso * ALTURA_PISO - ALTURA_PISO/2
    # 2-4 ventanas iluminadas por piso (point lights)
    n_lights = random.randint(2, 4)
    for i in range(n_lights):
        ang = (i / n_lights) * 2 * math.pi + random.random()
        radio = random.uniform(2, ANCHO/2 - 1)
        x = math.cos(ang) * radio
        y = math.sin(ang) * radio

        bpy.ops.object.light_add(type='POINT', location=(x, y, z_piso))
        luz = bpy.context.active_object
        luz.name = f"luz_{piso}_{i}"
        luz.data.energy = random.uniform(3, 12)
        luz.data.color = (1.0, random.uniform(0.6, 0.8), random.uniform(0.2, 0.4))
        # Mover a la coleccion torre
        for col in luz.users_collection:
            col.objects.unlink(luz)
        torre.objects.link(luz)

# ============== ENTORNO URBANO ==============
print("🌆 Skyline al fondo + mar...")

# Mar al fondo (plano grande azul oscuro)
add_box(entorno, "mar", (0, 80, -2),
        (200, 60, 0.5),
        mat_mar)

# Cielo (esfera gigante con shader golden hour)
bpy.ops.mesh.primitive_uv_sphere_add(radius=150, location=(0, 0, 30))
cielo_esfera = bpy.context.active_object
cielo_esfera.name = "cielo_atardecer"
# Material del cielo: gradiente dorado -> magenta -> azul
mat_cielo = bpy.data.materials.new("CieloGoldenHour")
mat_cielo.use_nodes = True
bsdf_cielo = mat_cielo.node_tree.nodes.get("Principled BSDF")
# Hacer emisivo
try:
    bsdf_cielo.inputs['Emission Color'].default_value = (1.0, 0.5, 0.25, 1.0)
    bsdf_cielo.inputs['Emission Strength'].default_value = 0.5
except:
    pass
# Color base
bsdf_cielo.inputs['Base Color'].default_value = (0.15, 0.20, 0.35, 1.0)
cielo_esfera.data.materials.append(mat_cielo)
for col in cielo_esfera.users_collection:
    col.objects.unlink(cielo_esfera)
entorno.objects.link(cielo_esfera)

# City skyline al fondo (silueta de edificios pequenos)
print("🏙️  Edificios del fondo (silueta)...")
for i in range(15):
    x = random.uniform(-60, 60)
    y = random.uniform(40, 70)
    h = random.uniform(8, 25)
    w = random.uniform(3, 7)
    d = random.uniform(3, 7)
    # Edificios lejanos: color muy oscuro (silueta)
    mat_silueta = make_pbr(f"silueta_{i}", (0.08, 0.08, 0.10), 0.9, 0.0)
    add_box(entorno, f"city_{i}", (x, y, h/2),
            (w, d, h),
            mat_silueta)

# ============== ILUMINACION ==============
print("☀️ Sol bajo en el horizonte (golden hour)...")
# Sol naranja-bajo (atardecer detras del edificio)
bpy.ops.object.light_add(type='SUN', location=(40, -60, 15))
sun = bpy.context.active_object
sun.name = "SolAtardecer"
sun.data.energy = 4.0
sun.data.color = (1.0, 0.55, 0.25)
sun.rotation_euler = (math.radians(15), 0, math.radians(45))
sun.data.angle = math.radians(3)

# Luz de relleno fria (azul del cielo detras)
bpy.ops.object.light_add(type='AREA', location=(-30, 50, 20))
fill = bpy.context.active_object
fill.data.energy = 250
fill.data.color = (0.4, 0.5, 0.85)
fill.data.size = 15

# Luz rim (contra-luz detras del edificio para silueta)
bpy.ops.object.light_add(type='SPOT', location=(40, -60, 18))
rim = bpy.context.active_object
rim.data.energy = 800
rim.data.color = (1.0, 0.55, 0.25)
rim.data.spot_size = math.radians(40)
# Apuntar a la torre
direction = Vector((0, 0, ALTURA_TOTAL/2)) - rim.location
rim.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# ============== CAMARA DRAMATICA ==============
print("📷 Cámara dramatica (angulo ascendente)...")
# Vista ascendente, mirando la torre desde abajo-frente
# Posicion: a unos 35m de distancia, ligeramente a la izquierda
cam_x = -22
cam_y = -28
cam_z = 8  # baja, para vista ascendente

bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
cam = bpy.context.active_object
cam.name = "CamGolden"

# Apuntar a la parte media-alta del edificio (mas dramatico)
target = Vector((0, 0, ALTURA_TOTAL * 0.55))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 32  # telefoto ligero para comprimir

bpy.context.scene.camera = cam

# ============== SKY SHADER (para el background de la camara) ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links

for node in list(world_nodes):
    world_nodes.remove(node)

# Gradient: naranja abajo, magenta medio, azul oscuro arriba
gradient = world_nodes.new('ShaderNodeTexGradient')
gradient.gradient_type = 'LINEAR'
mapping = world_nodes.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value = (math.radians(180), 0, 0)
world_links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])

color_ramp = world_nodes.new('ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.05, 0.10, 0.30, 1.0)  # azul oscuro arriba
color_ramp.color_ramp.elements[1].color = (1.0, 0.45, 0.20, 1.0)  # naranja abajo
# Agregar punto intermedio magenta
elem_mid = color_ramp.color_ramp.elements.new(0.55)
elem_mid.color = (0.85, 0.30, 0.45, 1.0)  # magenta

world_links.new(gradient.outputs['Color'], color_ramp.inputs['Fac'])

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 1.2

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(color_ramp.outputs['Color'], bg.inputs['Color'])
world_links.new(bg.outputs['Background'], out.inputs['Surface'])

# ============== RENDER SETTINGS ==============
print("🎨 Renderizando en HD...")
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1920  # vertical tipo foto de referencia
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.exposure = 1.0
bpy.context.scene.eevee.taa_render_samples = 64
# Bloom en Blender 5.2 — API nueva
try:
    bpy.context.scene.eevee.use_bloom = True
    bpy.context.scene.eevee.bloom_intensity = 0.8
    bpy.context.scene.eevee.bloom_threshold = 0.9
except AttributeError:
    pass

# ============== GUARDAR ==============
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print(f"\n✅ Guardado en: {OUTPUT}")

# Renderizar
preview = OUTPUT.replace(".blend", "_preview.png")
bpy.context.scene.render.filepath = preview
bpy.ops.render.render(write_still=True)
print(f"🖼️  Preview: {preview}")

# Mover a imagenes/
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
destino = os.path.join(IMGS_DIR, f"render_{timestamp}.png")
shutil.move(preview, destino)
print(f"📁 Movido a: {destino}")

link = os.path.join(IMGS_DIR, "render_ultimo.png")
if os.path.islink(link) or os.path.exists(link):
    os.remove(link)
os.symlink(os.path.basename(destino), link)
print(f"🔗 {os.path.basename(destino)}")

n_torre = len([o for o in bpy.data.objects if o.name in [obj.name for obj in torre.objects]])
n_entorno = len([o for o in bpy.data.objects if o.name in [obj.name for obj in entorno.objects]])
print(f"📦 Torre: {n_torre} objetos, Entorno: {n_entorno} objetos, Total: {n_torre + n_entorno}")
