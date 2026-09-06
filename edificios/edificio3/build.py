"""
edificio3.blend — Torre residencial costera (estilo Trump Tower Punta del Este)

Inspirado en arquitectura contemporánea costera:
- ~35 pisos con fachada 100% cristal azul reflectante
- Paneles de ventana con patron asimetrico (algunos sobresalen, otros retroceden)
- Corona negra gruesa arriba (helipuerto / cuarto de maquinas)
- Dia soleado perfecto, cielo azul vibrante
- Vista costera con mar al fondo
- Edificios vecinos bajos + parque
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

# Dimensiones de la torre (muy esbelta)
ANCHO = 12.0
PROFUNDO = 12.0
NUM_PISOS = 35
ALTURA_PISO = 3.0
ALTURA_TOTAL = NUM_PISOS * ALTURA_PISO  # 105 metros
ESPESOR_PANEL = 0.15

random.seed(2026)

# ============== LIMPIAR ESCENA ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

# ============== COLLECTIONS ==============
torre = bpy.data.collections.new("TorreCostera")
bpy.context.scene.collection.children.link(torre)
entorno = bpy.data.collections.new("Entorno")
bpy.context.scene.collection.children.link(entorno)

# ============== TEXTURAS ==============
def img_vacia(name, size=512):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)
    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_cristal_azul(name="CristalAzul", size=512, seed=99):
    """Cristal azul cielo reflectante — la firma de la referencia."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base azul cristalino (celeste profundo)
    for y in range(size):
        for x in range(size):
            # Variacion sutil celestes (reflejos del cielo)
            r = 0.35 + random.uniform(-0.05, 0.10)
            g = 0.55 + random.uniform(-0.05, 0.10)
            b = 0.78 + random.uniform(-0.05, 0.10)
            put(x, y, max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b)))

    # Reflejos verticales del horizonte (cielo arriba -> mar abajo)
    for y in range(size):
        factor = y / size  # 0 arriba, 1 abajo
        # Mas oscuro arriba, mas brillante cerca del horizonte
        if factor < 0.4:
            # arriba: azul oscuro
            r = 0.15 + factor * 0.3
            g = 0.30 + factor * 0.4
            b = 0.50 + factor * 0.4
        else:
            # abajo: celeste brillante
            r = 0.30 + (factor - 0.4) * 0.3
            g = 0.55 + (factor - 0.4) * 0.3
            b = 0.85 + (factor - 0.4) * 0.1

        for x in range(size):
            r_var = r + random.uniform(-0.04, 0.04)
            g_var = g + random.uniform(-0.04, 0.04)
            b_var = b + random.uniform(-0.04, 0.04)
            put(x, y, max(0, min(1, r_var)), max(0, min(1, g_var)), max(0, min(1, b_var)))

    # Highlights del sol (reflejos brillantes)
    for refl_y in [int(size*0.25), int(size*0.55), int(size*0.78)]:
        for x in range(size):
            intensity = (math.sin(x * 0.08) + 1) / 2 * 0.4 + 0.6
            put(x, refl_y, 0.8 * intensity, 0.9 * intensity, 1.0 * intensity)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_panel_ventana(name="PanelVentana", size=256, seed=11):
    """Panel individual con marco + cristal oscuro dentro (asi se ve cada ventana)."""
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Cristal oscuro azulado
    for y in range(size):
        for x in range(size):
            put(x, y, 0.20, 0.32, 0.45)

    # Marco negro grueso perimetral (mullion)
    marco = 12
    for y in range(size):
        for x in range(size):
            if x < marco or x > size - marco or y < marco or y > size - marco:
                put(x, y, 0.05, 0.05, 0.07)
            # Reflejo diagonal (estilo rascacielos)
            elif abs(x - y) < 6 or abs(x + y - size) < 6:
                put(x, y, 0.5, 0.65, 0.85)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def tex_pasto(name="Pasto", size=256, seed=33):
    """Cesped verde para el parque."""
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
        for x in range(size):
            # Verde con variacion
            v = 0.3 + random.uniform(-0.05, 0.10)
            put(x, y, 0.15 + v*0.3, 0.45 + v*0.3, 0.12 + v*0.2)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas costeras...")
tex_cristal = tex_cristal_azul()
tex_panel = tex_panel_ventana()
tex_pasto_img = tex_pasto()
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

mat_cristal_azul = make_pbr("CristalAzulReflectante", (0.35, 0.55, 0.78), 0.10, 0.2, tex_cristal)
# IOR alto para reflejo fuerte
for inp in mat_cristal_azul.node_tree.nodes["Principled BSDF"].inputs:
    if inp.name == 'IOR':
        inp.default_value = 1.6

mat_panel_ventana = make_pbr("PanelVentana", (0.18, 0.30, 0.42), 0.15, 0.4, tex_panel)
mat_metal_negro = make_pbr("MetalNegro", (0.04, 0.04, 0.05), 0.3, 0.9)
mat_mar = make_pbr("Mar", (0.25, 0.45, 0.65), 0.3, 0.0)
mat_arena = make_pbr("Arena", (0.85, 0.78, 0.62), 0.9, 0.0)
mat_pasto_mat = make_pbr("PastoVerde", (0.25, 0.50, 0.20), 0.8, 0.0, tex_pasto_img)
mat_arboles = make_pbr("Arboles", (0.20, 0.45, 0.18), 0.9, 0.0)
mat_calle = make_pbr("Calle", (0.18, 0.18, 0.20), 0.9, 0.0)
mat_concreto = make_pbr("ConcretoClaro", (0.78, 0.76, 0.74), 0.8, 0.0)

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

# ============== NUCLEO DE LA TORRE (cristal azul) ==============
print("🏗️  Construyendo nucleo cristalino azul...")
add_box(torre, "nucleo", (0, 0, ALTURA_TOTAL/2),
        (ANCHO, PROFUNDO, ALTURA_TOTAL),
        mat_cristal_azul, uv_unwrap=True)

# ============== PANELES DE VENTANAS ASIMETRICOS ==============
# Cada piso tiene paneles que sobresalen o retroceden (efecto mosaico 3D)
print("🪟 Paneles de ventana asimetricos...")
for piso in range(NUM_PISOS):
    z_centro_piso = piso * ALTURA_PISO + ALTURA_PISO / 2

    # Cantidad de paneles por fachada (entre 4 y 7)
    n_paneles = random.choice([4, 5, 5, 6, 6, 7])
    ancho_panel = ANCHO / n_paneles

    for fachada in ["X", "Xn", "Y", "Yn"]:
        if fachada == "X":
            pos_x = ANCHO/2
            fachada_dir = "x"
            fachada_extent = PROFUNDO
            n_fachada = n_paneles
            extent_total = ANCHO
            cross = "y"
        elif fachada == "Xn":
            pos_x = -ANCHO/2
            fachada_dir = "x"
            fachada_extent = PROFUNDO
            n_fachada = n_paneles
            extent_total = ANCHO
            cross = "y"
        elif fachada == "Y":
            pos_y = PROFUNDO/2
            fachada_dir = "y"
            fachada_extent = ANCHO
            n_fachada = n_paneles
            extent_total = PROFUNDO
            cross = "x"
        else:  # Yn
            pos_y = -PROFUNDO/2
            fachada_dir = "y"
            fachada_extent = ANCHO
            n_fachada = n_paneles
            extent_total = PROFUNDO
            cross = "x"

        for i in range(n_fachada):
            # Posicion a lo largo de la fachada
            if fachada_dir == "x":
                coord = -extent_total/2 + (i + 0.5) * (extent_total / n_fachada)
                offset_y = coord
                offset_x = 0
            else:
                coord = -extent_total/2 + (i + 0.5) * (extent_total / n_fachada)
                offset_x = coord
                offset_y = 0

            # Offset aleatorio (algunos paneles sobresalen, otros retroceden)
            offset_random = random.choice([-0.5, -0.3, -0.15, 0, 0.15, 0.3, 0.5])

            # Tamano del panel con variacion
            alto_panel = ALTURA_PISO - 0.15
            ancho_panel_var = (extent_total / n_fachada) * 0.85

            # Coordenadas finales
            if fachada == "X":
                loc = (pos_x + offset_random, offset_y, z_centro_piso)
                scale = (ESPESOR_PANEL, ancho_panel_var, alto_panel)
            elif fachada == "Xn":
                loc = (pos_x - offset_random, offset_y, z_centro_piso)
                scale = (ESPESOR_PANEL, ancho_panel_var, alto_panel)
            elif fachada == "Y":
                loc = (offset_x, pos_y + offset_random, z_centro_piso)
                scale = (ancho_panel_var, ESPESOR_PANEL, alto_panel)
            else:  # Yn
                loc = (offset_x, pos_y - offset_random, z_centro_piso)
                scale = (ancho_panel_var, ESPESOR_PANEL, alto_panel)

            add_box(torre, f"panel_{fachada}_{piso}_{i}",
                    loc, scale, mat_panel_ventana)

# ============== CORONA NEGRA (helipuerto) ==============
print("👑 Corona negra arriba...")
# Base gruesa
add_box(torre, "corona_base",
        (0, 0, ALTURA_TOTAL + 1.0),
        (ANCHO + 1.0, PROFUNDO + 1.0, 2.0),
        mat_metal_negro)

# Cilindro para helipuerto (helipad)
bpy.ops.mesh.primitive_cylinder_add(radius=4.5, depth=0.3, location=(0, 0, ALTURA_TOTAL + 2.2))
helipad = bpy.context.active_object
helipad.name = "helipad"
helipad.data.materials.append(mat_concreto)
for col in helipad.users_collection:
    col.objects.unlink(helipad)
torre.objects.link(helipad)

# Letras "H" en el helipad (cruz blanca)
for i, (dx, dy) in enumerate([(0, 0)]):  # una sola cruz al centro
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, ALTURA_TOTAL + 2.4))
    hbar = bpy.context.active_object
    hbar.name = f"hbar_{i}"
    hbar.scale = (3.5, 0.4, 0.05)
    hbar.data.materials.append(make_pbr("HelipadBlanco", (1.0, 1.0, 1.0), 0.5, 0.0))
    for col in hbar.users_collection:
        col.objects.unlink(hbar)
    torre.objects.link(hbar)

# Mastil / antena
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=8, location=(ANCHO/3, -PROFUNDO/3, ALTURA_TOTAL + 5))
mastil = bpy.context.active_object
mastil.name = "mastil"
mastil.data.materials.append(mat_metal_negro)
for col in mastil.users_collection:
    col.objects.unlink(mastil)
torre.objects.link(mastil)

# ============== ENTORNO COSTERO ==============
print("🌊 Entorno costero...")

# Mar al fondo
add_box(entorno, "mar", (0, 80, -2),
        (300, 80, 0.5),
        mat_mar)

# Cielo (esfera grande azul cielo)
bpy.ops.mesh.primitive_uv_sphere_add(radius=200, segments=64, ring_count=32, location=(0, 0, 50))
cielo_esfera = bpy.context.active_object
cielo_esfera.name = "cielo_dia"
# Material emisivo azul cielo
mat_cielo = bpy.data.materials.new("CieloDespejado")
mat_cielo.use_nodes = True
bsdf_cielo = mat_cielo.node_tree.nodes.get("Principled BSDF")
try:
    bsdf_cielo.inputs['Emission Color'].default_value = (0.4, 0.65, 0.95, 1.0)
    bsdf_cielo.inputs['Emission Strength'].default_value = 0.4
except:
    pass
bsdf_cielo.inputs['Base Color'].default_value = (0.55, 0.78, 1.0, 1.0)
cielo_esfera.data.materials.append(mat_cielo)
for col in cielo_esfera.users_collection:
    col.objects.unlink(cielo_esfera)
entorno.objects.link(cielo_esfera)

# Playa / costa
add_box(entorno, "playa", (0, 60, -0.5),
        (250, 30, 0.5),
        mat_arena)

# Parque con pasto
add_box(entorno, "parque", (-30, 25, 0.05),
        (50, 60, 0.1),
        mat_pasto_mat)

# Edificios vecinos (ciudad costera)
print("🏙️  Edificios vecinos (ciudad costera)...")
random.seed(77)
for i in range(20):
    x = random.uniform(-70, 70)
    y = random.uniform(-30, 50)
    if abs(x) < 15 and abs(y) < 15:  # no tapar la torre principal
        continue
    h = random.uniform(8, 30)
    w = random.uniform(4, 12)
    d = random.uniform(4, 10)
    # Color claro/beige como la referencia
    gris = random.uniform(0.7, 0.9)
    mat_vecino = make_pbr(f"vecino_{i}", (gris, gris*0.98, gris*0.92), 0.7, 0.0)
    add_box(entorno, f"vecino_{i}", (x, y, h/2),
            (w, d, h),
            mat_vecino)

# Arboles del parque
print("🌳 Arboles...")
random.seed(55)
for i in range(40):
    x = random.uniform(-50, -10)
    y = random.uniform(5, 45)
    # Tronco
    add_box(entorno, f"tronco_{i}", (x, y, 1.5),
            (0.3, 0.3, 3.0),
            mat_metal_negro)
    # Copa (esfera verde)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5, 2.5),
                                          location=(x, y, 3.5))
    copa = bpy.context.active_object
    copa.name = f"copa_{i}"
    copa.data.materials.append(mat_arboles)
    for col in copa.users_collection:
        col.objects.unlink(copa)
    entorno.objects.link(copa)

# Calles
add_box(entorno, "calle_principal", (0, -15, 0.05),
        (200, 6, 0.05),
        mat_calle)
add_box(entorno, "calle_secundaria", (-40, 25, 0.05),
        (6, 60, 0.05),
        mat_calle)

# ============== ILUMINACION (DIA SOLEADO) ==============
print("☀️ Sol brillante de mediodia...")
# Sol alto (como en la foto de referencia)
bpy.ops.object.light_add(type='SUN', location=(20, -30, 50))
sun = bpy.context.active_object
sun.name = "SolDia"
sun.data.energy = 7.0
sun.data.color = (1.0, 0.97, 0.90)
sun.rotation_euler = (math.radians(40), 0, math.radians(35))
sun.data.angle = math.radians(2)

# Ambient sky (rebote del cielo)
bpy.ops.object.light_add(type='AREA', location=(-20, 30, 30))
fill = bpy.context.active_object
fill.data.energy = 350
fill.data.color = (0.7, 0.85, 1.0)  # azul del cielo
fill.data.size = 20

# ============== CAMARA ==============
print("📷 Camara dramatica ascendente...")
# Vista desde un costado, mirando hacia arriba
cam_x = -20
cam_y = -25
cam_z = 6

bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
cam = bpy.context.active_object
cam.name = "CamCostera"

# Apuntar a la mitad superior del edificio
target = Vector((0, 0, ALTURA_TOTAL * 0.55))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 35

bpy.context.scene.camera = cam

# ============== SKY SHADER (FONDO) ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links

for node in list(world_nodes):
    world_nodes.remove(node)

# Cielo gradiente azul claro arriba -> mas claro en horizonte
tex = world_nodes.new('ShaderNodeTexSky')
tex.sky_type = 'HOSEK_WILKIE'
tex.sun_direction = (0.3, -0.4, 0.85)
tex.turbidity = 2  # cielo muy limpio
tex.altitude = 1.5

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.7

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(tex.outputs['Color'], bg.inputs['Color'])
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
print(f"\n✅ Guardado en: {OUTPUT}")

preview = OUTPUT.replace(".blend", "_preview.png")
bpy.context.scene.render.filepath = preview
bpy.ops.render.render(write_still=True)
print(f"🖼️  Preview: {preview}")

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
