"""
Edificio moderno con balcones de 2m en ESQUINA + texturas PBR con baking
- Vista isométrica 45° exacta
- Materiales procedurales con Noise + ImageTexture (baking)
- 5 pisos + PB comercial con fachada curva
"""

import bpy
import bmesh
import math
import os
import shutil
from datetime import datetime
from mathutils import Vector

# ============== CONFIG ==============
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edificio1.blend")
REPO_DIR = os.path.dirname(OUTPUT)
IMGS_DIR = os.path.join(REPO_DIR, "imagenes")
os.makedirs(IMGS_DIR, exist_ok=True)

# Dimensiones
ANCHO = 18.0          # fachada principal (X)
PROFUNDO = 14.0       # fachada lateral (Y)
NUM_PISOS = 5
ALTURA_PISO = 3.2
ALTURA_TOTAL = NUM_PISOS * ALTURA_PISO
BALCON_PROFUNDO = 2.0   # ← BALCONES DE 2 METROS EN ESQUINA (regalo)
BALCON_ANCHO = 4.0      # ancho de cada balcón
ESPESOR_LOSA = 0.30
ESPESOR_MURO = 0.25

# ============== LIMPIAR ESCENA ==============
bpy.ops.wm.read_factory_settings(use_empty=True)

# ============== COLLECTION PRINCIPAL ==============
edificio = bpy.data.collections.new("Edificio")
bpy.context.scene.collection.children.link(edificio)

# ============== TEXTURAS PROCEDURALES (BAKING) ==============
# Generamos imágenes procedurales con Noise usando bpy.ops + Image
# Estas se hornean a UV maps de los meshes para uso como texturas

def crear_textura_procedural(name, size=512, base_color=(0.5, 0.5, 0.5), variation=0.1, seed=0):
    """Crea una imagen con ruido procedural para usar como textura."""
    import random
    random.seed(seed)
    img = bpy.data.images.new(name, width=size, height=size, alpha=False, float_buffer=False)

    pixels = []
    for y in range(size):
        for x in range(size):
            # Ruido pseudo-aleatorio por pixel + interpolación
            r1 = random.random()
            r2 = random.random()
            r3 = random.random()
            # Mezcla color base + variación
            r = max(0, min(1, base_color[0] + (r1 - 0.5) * variation))
            g = max(0, min(1, base_color[1] + (r2 - 0.5) * variation))
            b = max(0, min(1, base_color[2] + (r3 - 0.5) * variation))
            pixels.extend([r, g, b, 1.0])
    img.pixels[:] = pixels
    img.pack()
    return img

def crear_textura_concreto(name="Concreto", size=512, seed=42):
    """Concreto con manchas, cimbra y juntas — usa solo bpy."""
    import random
    random.seed(seed)

    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put_pixel(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    # Base
    for y in range(size):
        for x in range(size):
            put_pixel(x, y, 180/255, 178/255, 175/255)

    # Manchas
    for _ in range(800):
        cx, cy = random.randint(0, size-1), random.randint(0, size-1)
        radio = random.randint(1, 4)
        r = random.randint(160, 200) / 255
        g = random.randint(155, 195) / 255
        b = random.randint(150, 190) / 255
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                if dx*dx + dy*dy <= radio*radio:
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        put_pixel(px, py, r, g, b)

    # Juntas de cimbra horizontales
    for junta_y in range(0, size, 64):
        for x in range(size):
            put_pixel(x, junta_y, 170/255, 168/255, 165/255)
            if junta_y + 1 < size:
                put_pixel(x, junta_y+1, 175/255, 173/255, 170/255)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def crear_textura_madera(name="Madera", size=512, seed=99):
    """Madera con vetas — solo bpy."""
    import random
    random.seed(seed)

    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put_pixel(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    for y in range(size):
        for x in range(size):
            veta = math.sin(y * 0.05 + x * 0.001) * 30
            ruido = (random.random() - 0.5) * 20
            r = max(0, min(255, 160 + veta * 0.5 + ruido)) / 255
            g = max(0, min(255, 110 + veta * 0.3 + ruido)) / 255
            b = max(0, min(255, 60 + veta * 0.2 + ruido)) / 255
            put_pixel(x, y, r, g, b)

    # Nudos
    for _ in range(5):
        cx = random.randint(50, size-50)
        cy = random.randint(50, size-50)
        radio = random.randint(10, 25)
        for dx in range(-radio, radio+1):
            for dy in range(-radio, radio+1):
                d = math.sqrt(dx*dx + dy*dy)
                if d <= radio:
                    factor = 1 - (d / radio)
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        idx = (py * size + px) * 4
                        pixels[idx] *= (1 - factor * 0.5)
                        pixels[idx+1] *= (1 - factor * 0.6)
                        pixels[idx+2] *= (1 - factor * 0.7)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

def crear_textura_metal(name="Metal", size=512, seed=7):
    """Metal cepillado — solo bpy."""
    import random
    random.seed(seed)

    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    pixels = [0.0] * (size * size * 4)

    def put_pixel(x, y, r, g, b):
        idx = (y * size + x) * 4
        pixels[idx] = r
        pixels[idx+1] = g
        pixels[idx+2] = b
        pixels[idx+3] = 1.0

    for y in range(size):
        for x in range(size):
            scratch = math.sin(y * 0.5) * 10 + (random.random() - 0.5) * 15
            r = max(0, min(255, 90 + scratch)) / 255
            g = max(0, min(255, 92 + scratch)) / 255
            b = max(0, min(255, 95 + scratch)) / 255
            put_pixel(x, y, r, g, b)

    # Manchas de óxido
    for _ in range(15):
        cx = random.randint(0, size-1)
        cy = random.randint(0, size-1)
        for dx in range(-10, 11):
            for dy in range(-10, 11):
                if random.random() < 0.3:
                    px, py = cx+dx, cy+dy
                    if 0 <= px < size and 0 <= py < size:
                        put_pixel(px, py, 140/255, 90/255, 40/255)

    img.pixels.foreach_set(pixels)
    img.pack()
    return img

print("🖼️  Generando texturas procedurales...")
tex_concreto = crear_textura_concreto()
tex_madera   = crear_textura_madera()
tex_metal    = crear_textura_metal()
print("✅ Texturas creadas")

# ============== MATERIALES PBR CON TEXTURAS ==============
def make_pbr(name, base_color, roughness, metallic, textura=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    if textura:
        # Crear nodo Image Texture
        tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex_node.image = textura
        # Conectar a Base Color
        mat.node_tree.links.new(
            tex_node.outputs['Color'],
            bsdf.inputs['Base Color']
        )
        # UV Map (asume que el objeto ya tiene UV unwrap)
        uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
        uv_node.uv_map = "UVMap"
        mat.node_tree.links.new(
            uv_node.outputs['UV'],
            tex_node.inputs['Vector']
        )

    return mat

mat_concreto_blanco = make_pbr("ConcretoBlanco", (0.85, 0.84, 0.82), 0.7, 0.0, tex_concreto)
mat_madera          = make_pbr("Madera",         (0.4, 0.25, 0.15), 0.6, 0.0, tex_madera)
mat_metal_negro     = make_pbr("MetalNegro",     (0.08, 0.08, 0.09), 0.3, 0.9, tex_metal)
mat_cristal         = make_pbr("CristalReflex",  (0.6, 0.7, 0.8), 0.05, 0.0)
mat_concreto_gris   = make_pbr("ConcretoGris",   (0.5, 0.5, 0.52), 0.85, 0.0, tex_concreto)
mat_ladrillo        = make_pbr("Ladrillo",       (0.55, 0.25, 0.18), 0.8, 0.0)
mat_asfalto         = make_pbr("Asfalto",        (0.12, 0.12, 0.13), 0.9, 0.0)

print("🎨 Materiales PBR listos")

# ============== HELPERS ==============
def add_box(name, loc, size, mat, uv_smart_project=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if uv_smart_project:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')
    for col in obj.users_collection:
        col.objects.unlink(obj)
    edificio.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# ============== NÚCLEO DEL EDIFICIO ==============
print("🏗️  Construyendo núcleo...")
add_box("nucleo_central", (0, 0, ALTURA_TOTAL/2),
        (ANCHO, PROFUNDO, ALTURA_TOTAL),
        mat_concreto_blanco, uv_smart_project=True)

# ============== BALCONES PERIMETRALES DE 2 METROS ==============
# Reglas:
# - TODO el perímetro (4 lados: +X, -X, +Y, -Y)
# - A la altura del suelo de cada piso (z_centro = piso * altura_piso - losa/2)
# - Pisos 1-4 SÍ tienen balcón, piso 5 NO
# - Cada balcón: losa + barandilla cristal + pasamanos madera
print("🌿 Construyendo balcones perimetrales de 2m (pisos 1-4)...")

for piso in range(1, NUM_PISOS):  # 1 a 4 (NO piso 5)
    # Altura: a nivel del suelo del piso (losa del piso actual)
    z_losa_piso = piso * ALTURA_PISO  # suelo del piso N
    z_centro_losa = z_losa_piso - ESPESOR_LOSA/2  # centro de la losa del balcón

    # ===== FACHADA +X (lado derecho, mirando hacia +X) =====
    add_box(f"losa_balcon_X_{piso}",
            (ANCHO/2 + BALCON_PROFUNDO/2, 0, z_centro_losa),
            (BALCON_PROFUNDO, PROFUNDO, ESPESOR_LOSA),
            mat_concreto_blanco)
    # Barandilla cristal
    add_box(f"barandilla_X_{piso}",
            (ANCHO/2 + BALCON_PROFUNDO, 0, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
            (0.05, PROFUNDO, 1.0),
            mat_cristal)
    # Pasamanos madera
    add_box(f"pasamanos_X_{piso}",
            (ANCHO/2 + BALCON_PROFUNDO, 0, z_centro_losa + ESPESOR_LOSA/2 + 1.08),
            (0.15, PROFUNDO, 0.08),
            mat_madera)
    # Montantes verticales cada 2m (barandilla)
    n_montantes_X = int(PROFUNDO / 2.0)
    for i in range(n_montantes_X + 1):
        y_pos = -PROFUNDO/2 + i * (PROFUNDO / n_montantes_X)
        add_box(f"montante_X_{piso}_{i}",
                (ANCHO/2 + BALCON_PROFUNDO, y_pos, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
                (0.08, 0.08, 1.0),
                mat_metal_negro)

    # ===== FACHADA -X (lado izquierdo) =====
    add_box(f"losa_balcon_Xn_{piso}",
            (-ANCHO/2 - BALCON_PROFUNDO/2, 0, z_centro_losa),
            (BALCON_PROFUNDO, PROFUNDO, ESPESOR_LOSA),
            mat_concreto_blanco)
    add_box(f"barandilla_Xn_{piso}",
            (-ANCHO/2 - BALCON_PROFUNDO, 0, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
            (0.05, PROFUNDO, 1.0),
            mat_cristal)
    add_box(f"pasamanos_Xn_{piso}",
            (-ANCHO/2 - BALCON_PROFUNDO, 0, z_centro_losa + ESPESOR_LOSA/2 + 1.08),
            (0.15, PROFUNDO, 0.08),
            mat_madera)
    n_montantes_Xn = int(PROFUNDO / 2.0)
    for i in range(n_montantes_Xn + 1):
        y_pos = -PROFUNDO/2 + i * (PROFUNDO / n_montantes_Xn)
        add_box(f"montante_Xn_{piso}_{i}",
                (-ANCHO/2 - BALCON_PROFUNDO, y_pos, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
                (0.08, 0.08, 1.0),
                mat_metal_negro)

    # ===== FACHADA +Y (lado frontal) =====
    add_box(f"losa_balcon_Y_{piso}",
            (0, PROFUNDO/2 + BALCON_PROFUNDO/2, z_centro_losa),
            (ANCHO, BALCON_PROFUNDO, ESPESOR_LOSA),
            mat_concreto_blanco)
    add_box(f"barandilla_Y_{piso}",
            (0, PROFUNDO/2 + BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
            (ANCHO, 0.05, 1.0),
            mat_cristal)
    add_box(f"pasamanos_Y_{piso}",
            (0, PROFUNDO/2 + BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 1.08),
            (ANCHO, 0.15, 0.08),
            mat_madera)
    n_montantes_Y = int(ANCHO / 2.0)
    for i in range(n_montantes_Y + 1):
        x_pos = -ANCHO/2 + i * (ANCHO / n_montantes_Y)
        add_box(f"montante_Y_{piso}_{i}",
                (x_pos, PROFUNDO/2 + BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
                (0.08, 0.08, 1.0),
                mat_metal_negro)

    # ===== FACHADA -Y (lado trasero) =====
    add_box(f"losa_balcon_Yn_{piso}",
            (0, -PROFUNDO/2 - BALCON_PROFUNDO/2, z_centro_losa),
            (ANCHO, BALCON_PROFUNDO, ESPESOR_LOSA),
            mat_concreto_blanco)
    add_box(f"barandilla_Yn_{piso}",
            (0, -PROFUNDO/2 - BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
            (ANCHO, 0.05, 1.0),
            mat_cristal)
    add_box(f"pasamanos_Yn_{piso}",
            (0, -PROFUNDO/2 - BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 1.08),
            (ANCHO, 0.15, 0.08),
            mat_madera)
    n_montantes_Yn = int(ANCHO / 2.0)
    for i in range(n_montantes_Yn + 1):
        x_pos = -ANCHO/2 + i * (ANCHO / n_montantes_Yn)
        add_box(f"montante_Yn_{piso}_{i}",
                (x_pos, -PROFUNDO/2 - BALCON_PROFUNDO, z_centro_losa + ESPESOR_LOSA/2 + 0.5),
                (0.08, 0.08, 1.0),
                mat_metal_negro)

    # ===== ESQUINAS: remate diagonal de barandilla =====
    # En las 4 esquinas, la barandilla continúa en diagonal
    esquinas = [
        (ANCHO/2 + BALCON_PROFUNDO, PROFUNDO/2 + BALCON_PROFUNDO, "+X+Y"),
        (-ANCHO/2 - BALCON_PROFUNDO, PROFUNDO/2 + BALCON_PROFUNDO, "-X+Y"),
        (ANCHO/2 + BALCON_PROFUNDO, -PROFUNDO/2 - BALCON_PROFUNDO, "+X-Y"),
        (-ANCHO/2 - BALCON_PROFUNDO, -PROFUNDO/2 - BALCON_PROFUNDO, "-X-Y"),
    ]
    for ex, ey, nombre in esquinas:
        # Cristal diagonal
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        bar_diag = bpy.context.active_object
        bar_diag.name = f"barandilla_diag_{nombre}_{piso}"
        bar_diag.location = (ex - BALCON_PROFUNDO/2 * 0.3 * (1 if "X" in nombre and "+X" in nombre else -1),
                              ey - BALCON_PROFUNDO/2 * 0.3 * (1 if "+Y" in nombre else -1),
                              z_centro_losa + ESPESOR_LOSA/2 + 0.5)
        bar_diag.scale = (1.4, 0.05, 1.0)
        # Rotar según esquina
        if nombre == "+X+Y":
            bar_diag.rotation_euler = (0, 0, math.radians(-45))
        elif nombre == "-X+Y":
            bar_diag.rotation_euler = (0, 0, math.radians(45))
        elif nombre == "+X-Y":
            bar_diag.rotation_euler = (0, 0, math.radians(45))
        elif nombre == "-X-Y":
            bar_diag.rotation_euler = (0, 0, math.radians(-45))
        for col in bar_diag.users_collection:
            col.objects.unlink(bar_diag)
        edificio.objects.link(bar_diag)
        bar_diag.data.materials.append(mat_cristal)

        # Pasamanos madera diagonal
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        pm_diag = bpy.context.active_object
        pm_diag.name = f"pasamanos_diag_{nombre}_{piso}"
        pm_diag.location = (bar_diag.location[0], bar_diag.location[1], bar_diag.location[2] + 0.58)
        pm_diag.scale = (1.5, 0.15, 0.08)
        pm_diag.rotation_euler = bar_diag.rotation_euler
        for col in pm_diag.users_collection:
            col.objects.unlink(pm_diag)
        edificio.objects.link(pm_diag)
        pm_diag.data.materials.append(mat_madera)

    # ===== MACETAS DECORATIVAS EN ESQUINAS DE BALCÓN =====
    # Una maceta en cada esquina del balcón perimetral
    for ex_sign in [-1, 1]:
        for ey_sign in [-1, 1]:
            ex = ex_sign * (ANCHO/2 + BALCON_PROFUNDO - 0.6)
            ey = ey_sign * (PROFUNDO/2 + BALCON_PROFUNDO - 0.6)
            add_box(f"maceta_perim_{piso}_{ex_sign}_{ey_sign}",
                    (ex, ey, z_centro_losa + ESPESOR_LOSA/2 + 0.2),
                    (0.4, 0.4, 0.4),
                    mat_concreto_gris)
            # Planta (esfera verde)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(ex, ey, z_centro_losa + ESPESOR_LOSA/2 + 0.75))
            planta = bpy.context.active_object
            planta.name = f"planta_perim_{piso}_{ex_sign}_{ey_sign}"
            for col in planta.users_collection:
                col.objects.unlink(planta)
            edificio.objects.link(planta)
            mat_verde = make_pbr("Verde", (0.15, 0.4, 0.12), 0.9, 0.0)
            planta.data.materials.append(mat_verde)

# ============== VENTANAS DE FACHADA (paneles grandes de cristal) ==============
print("🪟  Agregando ventanas...")
for piso in range(1, NUM_PISOS + 1):
    z_centro = piso * ALTURA_PISO - ALTURA_PISO/2
    
    # Fachada +X (5 ventanas de suelo a techo)
    for i in range(4):
        x = -ANCHO/2 + (i + 0.5) * (ANCHO / 4)
        add_box(f"ventana_X_{piso}_{i}",
                (x, PROFUNDO/2 + 0.05, z_centro),
                (ANCHO/5, 0.04, ALTURA_PISO - 0.6),
                mat_cristal)
    
    # Fachada +Y
    for i in range(3):
        y = -PROFUNDO/2 + (i + 0.5) * (PROFUNDO / 3)
        add_box(f"ventana_Y_{piso}_{i}",
                (ANCHO/2 + 0.05, y, z_centro),
                (0.04, PROFUNDO/4, ALTURA_PISO - 0.6),
                mat_cristal)
    
    # Fachada -X
    for i in range(4):
        x = -ANCHO/2 + (i + 0.5) * (ANCHO / 4)
        add_box(f"ventana_Xn_{piso}_{i}",
                (x, -PROFUNDO/2 - 0.05, z_centro),
                (ANCHO/5, 0.04, ALTURA_PISO - 0.6),
                mat_cristal)
    
    # Fachada -Y
    for i in range(3):
        y = -PROFUNDO/2 + (i + 0.5) * (PROFUNDO / 3)
        add_box(f"ventana_Yn_{piso}_{i}",
                (-ANCHO/2 - 0.05, y, z_centro),
                (0.04, PROFUNDO/4, ALTURA_PISO - 0.6),
                mat_cristal)

# ============== PLANTA BAJA: FACHADA CURVA COMERCIAL ==============
print("🛍️  Planta baja con fachada curva...")
N_SEG = 24
radio_curva = 5.5
centro_x = ANCHO/2 - 1
centro_y = PROFUNDO/2

for i in range(N_SEG):
    angulo = math.pi * (i + 0.5) / N_SEG
    x = centro_x + radio_curva * math.cos(angulo)
    y = centro_y + radio_curva * math.sin(angulo)
    angulo_rot = angulo + math.pi/2
    largo = 2 * radio_curva * math.sin(math.pi / (2*N_SEG)) * 1.04
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    seg = bpy.context.active_object
    seg.name = f"curva_PB_{i}"
    seg.location = (x, y, ALTURA_PISO/2)
    seg.scale = (largo, 0.18, ALTURA_PISO - 0.4)
    seg.rotation_euler = (0, 0, angulo_rot)
    for col in seg.users_collection:
        col.objects.unlink(seg)
    edificio.objects.link(seg)
    seg.data.materials.append(mat_cristal)

# Suelo comercial
add_box("suelo_PB", (centro_x - 1, centro_y, ESPESOR_LOSA/2),
        (radio_curva*2 + 4, radio_curva*2 + 4, ESPESOR_LOSA),
        mat_concreto_gris)

# Muro trasero con ladrillo visto
add_box("muro_ladrillo_PB",
        (centro_x - 2, centro_y + radio_curva + 1.5, ALTURA_PISO/2),
        (radio_curva*1.8, 0.35, ALTURA_PISO - 0.3),
        mat_ladrillo)

# Letrero "CAFÉ" o "RESTAURANT"
add_box("letrero_fondo", (centro_x, centro_y + 2, ALTURA_PISO - 0.6),
        (3.0, 0.05, 0.8),
        mat_metal_negro)

# Mostrador dentro
add_box("mostrador", (centro_x - 2, centro_y + 1, 0.55),
        (2.5, 0.7, 1.0),
        mat_madera)

# Sillas del café
for i in range(6):
    ang = i * (2*math.pi/6) + math.pi/6
    sx = centro_x - 2 + math.cos(ang) * 3.0
    sy = centro_y + 1 + math.sin(ang) * 1.5
    add_box(f"silla_cafe_{i}", (sx, sy, 0.45),
            (0.5, 0.5, 0.9),
            mat_metal_negro)
    add_box(f"mesa_cafe_{i}", (sx + 0.7, sy + 0.5, 0.5),
            (0.8, 0.8, 0.05),
            mat_madera)

# ============== CUBIERTA (último piso) ==============
print("🏠  Construyendo cubierta...")
add_box("techo_top", (0, 0, ALTURA_TOTAL + ESPESOR_LOSA/2),
        (ANCHO + 0.5, PROFUNDO + 0.5, ESPESOR_LOSA),
        mat_concreto_blanco)

# Caseta de máquinas (cuarto de ascensores)
add_box("caseta_ascensor", (ANCHO/4, -PROFUNDO/4, ALTURA_TOTAL + 1.5),
        (2.5, 2.5, 2.5),
        mat_concreto_blanco)

# Pérgola decorativa
print("🏛️  Construyendo pérgola...")
pergola_z = ALTURA_TOTAL + 0.05
for i in range(7):
    x_pos = -ANCHO/3 + i * (ANCHO*2/3/6)
    # Columna vertical
    add_box(f"pergola_col_{i}", (x_pos, PROFUNDO/2 + 1, pergola_z + 1.2),
            (0.15, 0.15, 2.4),
            mat_metal_negro)
    # Viga horizontal (se agrega después como una sola)
add_box("pergola_viga", (0, PROFUNDO/2 + 1, pergola_z + 2.4),
        (ANCHO*0.7, 0.15, 0.2),
        mat_metal_negro)
# Vigas secundarias perpendiculares
for j in range(5):
    y_pos = PROFUNDO/2 + 0.5 + j * 0.3
    add_box(f"pergola_viga_sec_{j}", (0, y_pos, pergola_z + 2.3),
            (ANCHO*0.7, 0.08, 0.15),
            mat_metal_negro)

# ============== ENTORNO URBANO ==============
print("🌆  Entorno urbano...")
# Acera ancha
add_box("acera_principal", (0, PROFUNDO/2 + 5, 0.05),
        (ANCHO + 8, 6, 0.12),
        mat_concreto_gris, uv_smart_project=True)
# Calle
add_box("calle", (0, PROFUNDO/2 + 12, 0.02),
        (ANCHO + 8, 8, 0.04),
        mat_asfalto)
# Línea blanca central de la calle
add_box("linea_calles", (0, PROFUNDO/2 + 12, 0.05),
        (ANCHO + 7, 0.15, 0.01),
        mat_concreto_blanco)

# Edificio vecino (izquierda)
add_box("vecino_izq", (-ANCHO/2 - 6, 0, 7),
        (6, 14, 14),
        mat_concreto_blanco)
# Ventanas del vecino
for fila in range(4):
    for col in range(3):
        add_box(f"vent_vecino_{fila}_{col}",
                (-ANCHO/2 - 9, -6 + col*4, 2 + fila*3),
                (0.05, 2.5, 1.8),
                mat_cristal)

# Edificio vecino (atrás)
add_box("vecino_atras", (0, -PROFUNDO/2 - 6, 6),
        (ANCHO + 6, 5, 12),
        mat_concreto_blanco)

# ============== ILUMINACIÓN ==============
print("💡  Configurando iluminación...")
# Sol
bpy.ops.object.light_add(type='SUN', location=(20, -15, 25))
sun = bpy.context.active_object
sun.name = "Sol"
sun.data.energy = 6.0  # subido de 4.5
sun.data.color = (1.0, 0.94, 0.82)
sun.rotation_euler = (math.radians(45), 0, math.radians(35))
sun.data.angle = math.radians(2)

# Fill light (rebote del cielo)
bpy.ops.object.light_add(type='AREA', location=(-12, 18, 12))
fill = bpy.context.active_object
fill.data.energy = 200  # subido de 120
fill.data.size = 10

# Ambient boost: bajar el strength del sky para que no aplaste todo
# (se hace en la sección SKY)

# ============== CÁMARA ISOMÉTRICA 45° ==============
print("📷  Cámara isométrica 45° exactos...")
# Distancia suficiente para ver todo
distancia = 38
angulo_azimut = math.radians(45)  # 45° respecto al eje X
altura_cam = ALTURA_TOTAL * 0.55

cam_x = distancia * math.cos(angulo_azimut)
cam_y = -distancia * math.sin(angulo_azimut)
cam_z = altura_cam

bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
cam = bpy.context.active_object
cam.name = 'CamPrincipal'

# Apuntar al centro del edificio (0, 0, ALTURA_TOTAL/2)
target = Vector((0, 0, ALTURA_TOTAL/2))
direction = target - cam.location
rot = direction.to_track_quat('-Z', 'Y').to_euler()
cam.rotation_euler = rot
cam.data.lens = 35  # lente normal, no gran angular

bpy.context.scene.camera = cam

# ============== SKY ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_links = bpy.context.scene.world.node_tree.links

# Limpiar
for node in list(world_nodes):
    world_nodes.remove(node)

# Sky shader
tex = world_nodes.new('ShaderNodeTexSky')
tex.sky_type = 'HOSEK_WILKIE'
tex.sun_direction = (0.5, -0.4, 0.7)
tex.turbidity = 3

bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.8  # bajado de 1.8 para no aplastar

out = world_nodes.new('ShaderNodeOutputWorld')
world_links.new(tex.outputs['Color'], bg.inputs['Color'])
world_links.new(bg.outputs['Background'], out.inputs['Surface'])

# ============== RENDER ==============
print("🎨  Renderizando...")
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.render.resolution_x = 1920   # HD
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.exposure = 1.5  # subido de 1.0
bpy.context.scene.eevee.taa_render_samples = 32

# Render preview
preview_path = OUTPUT.replace(".blend", "_preview.png")
bpy.context.scene.render.filepath = preview_path
bpy.ops.render.render(write_still=True)

# ============== GUARDAR ==============
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print(f"\n✅ Edificio guardado en: {OUTPUT}")

# Mover a imagenes/ con timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
destino = os.path.join(IMGS_DIR, f"render_{timestamp}.png")
shutil.move(preview_path, destino)
print(f"📁 Render guardado en: {destino}")

# Actualizar symlink
link_path = os.path.join(IMGS_DIR, "render_ultimo.png")
if os.path.islink(link_path) or os.path.exists(link_path):
    os.remove(link_path)
os.symlink(os.path.basename(destino), link_path)
print(f"🔗 render_ultimo.png -> {os.path.basename(destino)}")

n = len([o for o in bpy.data.objects if o.name in [obj.name for obj in edificio.objects]])
print(f"📦 Objetos en colección Edificio: {n}")
