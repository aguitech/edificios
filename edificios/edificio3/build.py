"""
edificio3.blend — Torre residencial costera v2 (alineada, con cariño)

Inspirado en arquitectura contemporanea costera (Trump Tower Punta del Este):
- 35 pisos con fachada 100% cristal azul reflectante
- GRID PERFECTO de ventanas: misma cantidad por piso, alineadas verticalmente
- Cornisas finas blancas entre cada piso
- Corona negra con helipuerto
- Dia soleado, mar al fondo, parque con arboles
"""

import bpy
import math
import os
import shutil
import random
from datetime import datetime
from mathutils import Vector

# ============== CONFIG ==============
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edificio3.blend")
REPO_DIR = os.path.dirname(OUTPUT)
IMGS_DIR = os.path.join(REPO_DIR, "imagenes")
os.makedirs(IMGS_DIR, exist_ok=True)

# Dimensiones esbeltas pero proporcionadas
ANCHO = 13.0
PROFUNDO = 13.0
NUM_PISOS = 35
ALTURA_PISO = 3.0
ALTURA_TOTAL = NUM_PISOS * ALTURA_PISO  # 105 m

# GRID: 5 columnas por fachada, todas alineadas
COLUMNAS_X = 5  # columnas en fachadas +X / -X
FILAS_Y = 5     # filas en fachadas +Y / -Y

# Dimensiones de paneles
ANCHO_PANEL = (ANCHO - 0.2) / COLUMNAS_X  # dejar margen a los bordes
ALTO_PANEL = ALTURA_PISO * 0.85
GROSOR_PANEL = 0.10  # paneles casi rasantes al muro

CORNISA_H = 0.15  # cornisa FINA entre pisos (la firma de la referencia)

random.seed(2026)

# ============== LIMPIAR ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

torre = bpy.data.collections.new("TorreCostera")
bpy.context.scene.collection.children.link(torre)
entorno = bpy.data.collections.new("Entorno")
bpy.context.scene.collection.children.link(entorno)

# ============== TEXTURAS (sutiles, casi imperceptibles) ==============
def img_vacia(name, size=256):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    img.pixels.foreach_set([0.0] * (size * size * 4))
    img.pack()
    return img

def tex_cristal_azul_limpio(name="CristalAzulLimpio", size=512, seed=99):
    """Cristal azul cielo limpio, reflejos sutiles del horizonte."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base: gradiente azul cielo (mas claro arriba, mas oscuro cerca horizonte)
    for y in range(size):
        f = y / size  # 0 arriba, 1 abajo
        # Cielo profundo arriba
        r_base = 0.30 - f * 0.10
        g_base = 0.55 - f * 0.10
        b_base = 0.85 - f * 0.15

        for x in range(size):
            r = r_base + random.uniform(-0.02, 0.02)
            g = g_base + random.uniform(-0.02, 0.02)
            b = b_base + random.uniform(-0.02, 0.02)
            put(x, y, max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)))

    # Reflejos del sol: bandas horizontales muy sutiles
    for refl_y in [int(size*0.30), int(size*0.65)]:
        for x in range(size):
            intensity = (math.sin(x * 0.04) + 1) / 2 * 0.15
            r, g, b = 0.6 + intensity, 0.75 + intensity, 0.95 + intensity
            put(x, refl_y, r, g, b)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_mullion(name="Mullion", size=128, seed=42):
    """Mullion (marcacion vertical entre ventanas) gris oscuro."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base gris metalico
    for y in range(size):
        for x in range(size):
            put(x, y, 0.18, 0.20, 0.22)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas...")
tex_cristal = tex_cristal_azul_limpio()
tex_mullion_img = tex_mullion()
print("✅ Texturas listas")

# ============== MATERIALES ==============
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

mat_cristal_azul = make_pbr("CristalAzul", (0.30, 0.55, 0.85), 0.10, 0.0, tex_cristal)
# IOR alto para reflejo realista
for inp in mat_cristal_azul.node_tree.nodes["Principled BSDF"].inputs:
    if inp.name == 'IOR':
        inp.default_value = 1.5

mat_mullion = make_pbr("MullionMetal", (0.18, 0.20, 0.22), 0.35, 0.7, tex_mullion_img)
mat_metal_negro = make_pbr("MetalNegro", (0.04, 0.04, 0.05), 0.3, 0.9)
mat_mar = make_pbr("Mar", (0.20, 0.42, 0.62), 0.25, 0.0)
mat_arena = make_pbr("Arena", (0.88, 0.80, 0.65), 0.95, 0.0)
mat_pasto = make_pbr("PastoVerde", (0.28, 0.55, 0.22), 0.85, 0.0)
mat_arboles = make_pbr("Arboles", (0.22, 0.48, 0.20), 0.9, 0.0)
mat_calle = make_pbr("Calle", (0.18, 0.18, 0.20), 0.9, 0.0)
mat_concreto = make_pbr("ConcretoClaro", (0.85, 0.84, 0.82), 0.8, 0.0)
mat_cornisa = make_pbr("CornisaMetal", (0.55, 0.56, 0.58), 0.4, 0.6)
mat_helipad = make_pbr("HelipadConcreto", (0.65, 0.65, 0.62), 0.85, 0.0)

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

# ============== NUCLEO DE LA TORRE ==============
print("🏗️  Construyendo nucleo cristalino azul...")
add_box(torre, "nucleo", (0, 0, ALTURA_TOTAL/2),
        (ANCHO, PROFUNDO, ALTURA_TOTAL),
        mat_cristal_azul, uv_unwrap=True)

# ============== GRID PERFECTO DE VENTANAS ==============
print("🪟 Grid PERFECTO de ventanas alineadas...")

for piso in range(NUM_PISOS):
    z_centro_piso = piso * ALTURA_PISO + ALTURA_PISO / 2

    # Fachada +X: 5 columnas alineadas verticalmente
    for col in range(COLUMNAS_X):
        x_centro = -ANCHO/2 + (col + 0.5) * (ANCHO / COLUMNAS_X)
        add_box(torre, f"vent_X_{piso}_{col}",
                (ANCHO/2 + GROSOR_PANEL/2, x_centro, z_centro_piso),
                (GROSOR_PANEL, ANCHO_PANEL * 0.92, ALTO_PANEL),
                mat_cristal_azul)

    # Fachada -X
    for col in range(COLUMNAS_X):
        x_centro = -ANCHO/2 + (col + 0.5) * (ANCHO / COLUMNAS_X)
        add_box(torre, f"vent_Xn_{piso}_{col}",
                (-ANCHO/2 - GROSOR_PANEL/2, x_centro, z_centro_piso),
                (GROSOR_PANEL, ANCHO_PANEL * 0.92, ALTO_PANEL),
                mat_cristal_azul)

    # Fachada +Y
    for fila in range(FILAS_Y):
        y_centro = -PROFUNDO/2 + (fila + 0.5) * (PROFUNDO / FILAS_Y)
        add_box(torre, f"vent_Y_{piso}_{fila}",
                (y_centro, PROFUNDO/2 + GROSOR_PANEL/2, z_centro_piso),
                (ANCHO_PANEL * 0.92, GROSOR_PANEL, ALTO_PANEL),
                mat_cristal_azul)

    # Fachada -Y
    for fila in range(FILAS_Y):
        y_centro = -PROFUNDO/2 + (fila + 0.5) * (PROFUNDO / FILAS_Y)
        add_box(torre, f"vent_Yn_{piso}_{fila}",
                (y_centro, -PROFUNDO/2 - GROSOR_PANEL/2, z_centro_piso),
                (ANCHO_PANEL * 0.92, GROSOR_PANEL, ALTO_PANEL),
                mat_cristal_azul)

# ============== MULLIONS VERTICALES (marcaciones entre ventanas) ==============
print("🪞 Mullions verticales (cuadricula fina entre ventanas)...")
for piso in range(NUM_PISOS):
    z_centro_piso = piso * ALTURA_PISO + ALTURA_PISO / 2

    # Mullions verticales en +X (entre cada columna)
    for col in range(COLUMNAS_X + 1):
        x_pos = -ANCHO/2 + col * (ANCHO / COLUMNAS_X)
        add_box(torre, f"mullion_X_{piso}_{col}",
                (ANCHO/2 + GROSOR_PANEL + 0.01, x_pos, z_centro_piso),
                (0.03, 0.04, ALTO_PANEL + 0.1),
                mat_mullion)

    for col in range(COLUMNAS_X + 1):
        x_pos = -ANCHO/2 + col * (ANCHO / COLUMNAS_X)
        add_box(torre, f"mullion_Xn_{piso}_{col}",
                (-ANCHO/2 - GROSOR_PANEL - 0.01, x_pos, z_centro_piso),
                (0.03, 0.04, ALTO_PANEL + 0.1),
                mat_mullion)

    for fila in range(FILAS_Y + 1):
        y_pos = -PROFUNDO/2 + fila * (PROFUNDO / FILAS_Y)
        add_box(torre, f"mullion_Y_{piso}_{fila}",
                (y_pos, PROFUNDO/2 + GROSOR_PANEL + 0.01, z_centro_piso),
                (0.04, 0.03, ALTO_PANEL + 0.1),
                mat_mullion)

    for fila in range(FILAS_Y + 1):
        y_pos = -PROFUNDO/2 + fila * (PROFUNDO / FILAS_Y)
        add_box(torre, f"mullion_Yn_{piso}_{fila}",
                (y_pos, -PROFUNDO/2 - GROSOR_PANEL - 0.01, z_centro_piso),
                (0.04, 0.03, ALTO_PANEL + 0.1),
                mat_mullion)

# ============== CORNISAS FINAS (entre cada piso) ==============
print("🏛️  Cornisas finas por piso (alineadas al grid)...")
for piso in range(NUM_PISOS + 1):
    z_cornisa = piso * ALTURA_PISO
    # Cornisa perimetral fina que sobresale un poquito
    overhang = 0.08
    add_box(torre, f"cornisa_{piso}",
            (0, 0, z_cornisa + CORNISA_H/2),
            (ANCHO + 2*overhang, PROFUNDO + 2*overhang, CORNISA_H),
            mat_cornisa)

# ============== CORONA NEGRA ARRIBA ==============
print("👑 Corona negra + helipuerto...")
# Base de la corona
add_box(torre, "corona_base",
        (0, 0, ALTURA_TOTAL + 1.0),
        (ANCHO + 0.6, PROFUNDO + 0.6, 2.0),
        mat_metal_negro)

# Helipuerto circular
bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=0.4, location=(0, 0, ALTURA_TOTAL + 2.2))
helipad = bpy.context.active_object
helipad.name = "helipad"
helipad.data.materials.append(mat_helipad)
for col in helipad.users_collection:
    col.objects.unlink(helipad)
torre.objects.link(helipad)

# Circulo blanco de helipuerto
bpy.ops.mesh.primitive_cylinder_add(radius=4.2, depth=0.02, location=(0, 0, ALTURA_TOTAL + 2.4))
circulo = bpy.context.active_object
circulo.name = "circulo_helipad"
circulo.data.materials.append(make_pbr("HelipadPintura", (1.0, 1.0, 1.0), 0.6, 0.0))
for col in circulo.users_collection:
    col.objects.unlink(circulo)
torre.objects.link(circulo)

# Letra H del helipuerto
add_box(torre, "helipad_H_barra1",
        (0, 1.5, ALTURA_TOTAL + 2.45),
        (3.5, 0.35, 0.04),
        make_pbr("HelipadH", (1.0, 1.0, 1.0), 0.5, 0.0))
add_box(torre, "helipad_H_barra2",
        (0, -1.5, ALTURA_TOTAL + 2.45),
        (3.5, 0.35, 0.04),
        make_pbr("HelipadH", (1.0, 1.0, 1.0), 0.5, 0.0))
add_box(torre, "helipad_H_vert",
        (0, 0, ALTURA_TOTAL + 2.45),
        (0.35, 3.4, 0.04),
        make_pbr("HelipadH", (1.0, 1.0, 1.0), 0.5, 0.0))

# Antena / mástil
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=10, location=(ANCHO/4, -PROFUNDO/4, ALTURA_TOTAL + 5))
mastil = bpy.context.active_object
mastil.name = "mastil"
mastil.data.materials.append(mat_metal_negro)
for col in mastil.users_collection:
    col.objects.unlink(mastil)
torre.objects.link(mastil)

# ============== ENTORNO COSTERO ==============
print("🌊 Entorno costero...")

# Mar
add_box(entorno, "mar", (0, 80, -2),
        (350, 100, 0.5),
        mat_mar)

# Esfera cielo
bpy.ops.mesh.primitive_uv_sphere_add(radius=200, segments=64, ring_count=32, location=(0, 0, 50))
cielo_esfera = bpy.context.active_object
cielo_esfera.name = "cielo_dia"
mat_cielo = bpy.data.materials.new("CieloDespejado")
mat_cielo.use_nodes = True
bsdf_cielo = mat_cielo.node_tree.nodes.get("Principled BSDF")
try:
    bsdf_cielo.inputs['Emission Color'].default_value = (0.4, 0.65, 0.95, 1.0)
    bsdf_cielo.inputs['Emission Strength'].default_value = 0.35
except:
    pass
bsdf_cielo.inputs['Base Color'].default_value = (0.55, 0.78, 1.0, 1.0)
cielo_esfera.data.materials.append(mat_cielo)
for col in cielo_esfera.users_collection:
    col.objects.unlink(cielo_esfera)
entorno.objects.link(cielo_esfera)

# Playa
add_box(entorno, "playa", (0, 60, -0.5),
        (300, 30, 0.5),
        mat_arena)

# Parque con pasto
add_box(entorno, "parque", (-35, 25, 0.05),
        (60, 70, 0.1),
        mat_pasto)

# Edificios vecinos
print("🏙️  Edificios vecinos...")
random.seed(77)
for i in range(25):
    x = random.uniform(-90, 90)
    y = random.uniform(-30, 50)
    # No tapar la torre principal
    if abs(x) < 16 and abs(y) < 16:
        continue
    h = random.uniform(8, 30)
    w = random.uniform(4, 14)
    d = random.uniform(4, 10)
    gris = random.uniform(0.72, 0.92)
    mat_vecino = make_pbr(f"vecino_{i}", (gris, gris*0.98, gris*0.92), 0.7, 0.0)
    add_box(entorno, f"vecino_{i}", (x, y, h/2),
            (w, d, h),
            mat_vecino)
    # Ventanas del vecino
    for fila in range(int(h / 3)):
        for col_x in range(int(w / 2)):
            add_box(entorno, f"vent_vecino_{i}_{fila}_{col_x}",
                    (x - w/2 + 1 + col_x*2, y + d/2 + 0.02, 1.5 + fila*3),
                    (1.2, 0.05, 1.5),
                    mat_cristal_azul)

# Arboles del parque
print("🌳 Arboles...")
random.seed(55)
for i in range(50):
    x = random.uniform(-60, -10)
    y = random.uniform(0, 50)
    add_box(entorno, f"tronco_{i}", (x, y, 1.5),
            (0.3, 0.3, 3.0),
            mat_metal_negro)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5, 2.5),
                                          location=(x, y, 4.0))
    copa = bpy.context.active_object
    copa.name = f"copa_{i}"
    copa.data.materials.append(mat_arboles)
    for col in copa.users_collection:
        col.objects.unlink(copa)
    entorno.objects.link(copa)

# Calles
add_box(entorno, "calle_principal", (0, -12, 0.05),
        (250, 6, 0.05),
        mat_calle)
add_box(entorno, "calle_secundaria", (-45, 25, 0.05),
        (6, 70, 0.05),
        mat_calle)
# Linea blanca central
add_box(entorno, "linea_central", (0, -12, 0.06),
        (250, 0.15, 0.01),
        make_pbr("LineaBlanca", (1.0, 1.0, 0.95), 0.6, 0.0))

# ============== ILUMINACION (DIA SOLEADO PERO DRAMATICO) ==============
print("☀️ Sol bajo lateral (para sombras dramaticas)...")
# Sol LATERAL (no encima) para crear contraste fuerte entre lado iluminado y lado en sombra
bpy.ops.object.light_add(type='SUN', location=(40, -50, 30))
sun = bpy.context.active_object
sun.name = "SolDia"
sun.data.energy = 6.5
sun.data.color = (1.0, 0.96, 0.88)
sun.rotation_euler = (math.radians(35), 0, math.radians(45))
sun.data.angle = math.radians(1.5)  # sol mas pequeno = sombras mas marcadas

# Fill azul (rebote del cielo)
bpy.ops.object.light_add(type='AREA', location=(-20, 30, 30))
fill = bpy.context.active_object
fill.data.energy = 300
fill.data.color = (0.65, 0.80, 1.0)
fill.data.size = 20

# ============== CAMARA ==============
print("📷 Camara con vista lateral dramatica...")
# Vista lateral, ligeramente baja, para ver ambas fachadas
cam_x = -28
cam_y = -18
cam_z = 8

bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
cam = bpy.context.active_object
cam.name = "CamCostera"

target = Vector((0, 0, ALTURA_TOTAL * 0.50))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 35

bpy.context.scene.camera = cam

# ============== SKY SHADER ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links
for node in list(world_nodes):
    world_nodes.remove(node)

tex_sky = world_nodes.new('ShaderNodeTexSky')
tex_sky.sky_type = 'HOSEK_WILKIE'
tex_sky.sun_direction = (0.4, -0.5, 0.75)
tex_sky.turbidity = 2
tex_sky.altitude = 1.5

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.6

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(tex_sky.outputs['Color'], bg.inputs['Color'])
world_links.new(bg.outputs['Background'], out.inputs['Surface'])

# ============== RENDER ==============
print("🎨 Renderizando...")
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1920
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.exposure = 1.0
bpy.context.scene.eevee.taa_render_samples = 64

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

n_torre = len([o for o in bpy.data.objects if o.name in [obj.name for obj in torre.objects]])
n_entorno = len([o for o in bpy.data.objects if o.name in [obj.name for obj in entorno.objects]])
print(f"📦 Torre: {n_torre}, Entorno: {n_entorno}, Total: {n_torre + n_entorno}")
