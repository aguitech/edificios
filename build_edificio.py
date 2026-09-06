"""
Genera el edificio moderno en Blender (5 pisos, voladizos en zigzag, balcones cristal, esquina).

Uso:
    /Applications/Blender.app/Contents/MacOS/Blender --background --python build_edificio.py
"""

import bpy
import math
import sys

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# ============== CONFIG ==============
OUTPUT = "/Users/hectoraguilar/Projects/edificio/edificio.blend"
NUM_PISOS = 5
ALTURA_PISO = 3.2
ANCHO = 22.0
PROFUNDO = 16.0
ESPESOR_LOSA = 0.35
ESPESOR_MURO = 0.25
VOLADIZO = 1.8

# ============== MATERIALES ==============
def make_material(name, color, roughness=0.5, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    # Transmission (puede estar renombrado en 5.2)
    for inp in bsdf.inputs:
        if 'rans' in inp.name.lower():
            inp.default_value = transmission
            break
    return mat

mat_white    = make_material("EstructuraBlanca", (0.92, 0.92, 0.93), roughness=0.4)
mat_glass    = make_material("Cristal",          (0.4, 0.5, 0.6), roughness=0.1, transmission=0.0)
mat_concrete = make_material("Concreto",         (0.65, 0.65, 0.66), roughness=0.85)
mat_wood     = make_material("Madera",           (0.45, 0.28, 0.16), roughness=0.7)
mat_metal    = make_material("Metal",            (0.18, 0.18, 0.20), roughness=0.3, metallic=0.8)
mat_floor    = make_material("Piso",             (0.18, 0.16, 0.14), roughness=0.6)
mat_asfalto  = make_material("Asfalto",          (0.18, 0.18, 0.19), roughness=0.9)

# ============== COLLECTION ==============
collection = bpy.data.collections.new("Edificio")
bpy.context.scene.collection.children.link(collection)

# ============== HELPERS ==============
def add_box(name, loc, size, mat):
    """Crea cubo en `loc` con dimensiones `size`. Aplica transforms ANTES de mover."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.location = loc
    obj.scale = size
    # Mover de scene collection a nuestra collection
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# ============== ESTRUCTURA PRINCIPAL ==============
add_box("nucleo_central", (0, 0, NUM_PISOS*ALTURA_PISO/2),
        (ANCHO-4, PROFUNDO-4, NUM_PISOS*ALTURA_PISO),
        mat_concrete)

# ============== VOLADIZOS EN ZIGZAG ==============
for piso in range(NUM_PISOS):
    z_centro = ALTURA_PISO/2 + piso*ALTURA_PISO
    
    # Losa del piso
    if piso % 2 == 0:
        # Voladizo en +X
        add_box(f"losa_{piso}", (ANCHO/2 + VOLADIZO/2 - 0.5, 0, z_centro),
                (ANCHO + VOLADIZO, PROFUNDO, ESPESOR_LOSA),
                mat_white)
        # Cristal frontal (+X)
        add_box(f"cristal_x_{piso}", (ANCHO/2 + VOLADIZO/2 - 0.5, 0, z_centro + 1.1),
                (ANCHO + VOLADIZO, ESPESOR_MURO, ALTURA_PISO - 0.9),
                mat_glass)
    else:
        # Voladizo en +Y
        add_box(f"losa_{piso}", (0, PROFUNDO/2 + VOLADIZO/2 - 0.5, z_centro),
                (ANCHO, PROFUNDO + VOLADIZO, ESPESOR_LOSA),
                mat_white)
        # Cristal lateral (+Y)
        add_box(f"cristal_y_{piso}", (0, PROFUNDO/2 + VOLADIZO/2 - 0.5, z_centro + 1.1),
                (ESPESOR_MURO, PROFUNDO + VOLADIZO, ALTURA_PISO - 0.9),
                mat_glass)
    
    # Barandilla de cristal
    if piso % 2 == 0:
        add_box(f"barandilla_{piso}", (ANCHO + VOLADIZO - 0.15, 0, z_centro + ALTURA_PISO/2 - 0.5),
                (0.05, PROFUNDO, 1.0),
                mat_glass)
    else:
        add_box(f"barandilla_{piso}", (0, PROFUNDO + VOLADIZO - 0.15, z_centro + ALTURA_PISO/2 - 0.5),
                (ANCHO, 0.05, 1.0),
                mat_glass)

# ============== PLANTA BAJA: CRISTAL CURVO (restaurante) ==============
N_SEG = 16
radio_curva = 4.5
centro_curva_x = ANCHO/2 - 2
centro_curva_y = -PROFUNDO/2

for i in range(N_SEG):
    angulo = math.pi * (i + 0.5) / N_SEG - math.pi/2
    x = centro_curva_x + radio_curva * math.cos(angulo)
    y = centro_curva_y + radio_curva * math.sin(angulo)
    angulo_rot = math.atan2(math.cos(angulo), -math.sin(angulo))
    largo_segmento = 2 * radio_curva * math.sin(math.pi / (2*N_SEG)) * 1.05
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    seg = bpy.context.active_object
    seg.name = f"curva_{i}"
    seg.location = (x, y, ALTURA_PISO/2)
    seg.scale = (largo_segmento, 0.12, ALTURA_PISO - 0.4)
    seg.rotation_euler = (0, 0, angulo_rot)
    for col in seg.users_collection:
        col.objects.unlink(seg)
    collection.objects.link(seg)
    seg.data.materials.append(mat_glass)

# Losa planta baja (suelo del restaurante)
add_box("losa_planta_baja", (centro_curva_x, centro_curva_y, ESPESOR_LOSA/2),
        (radio_curva*2 + 2, radio_curva*2 + 2, ESPESOR_LOSA),
        mat_concrete)

# Muro trasero del restaurante
add_box("muro_trasero_rest", (centro_curva_x, centro_curva_y - radio_curva - 1, ALTURA_PISO/2),
        (radio_curva*1.5, 0.3, ALTURA_PISO - 0.6),
        mat_concrete)

# Sillas y mesas del restaurante (decoración)
for i in range(4):
    add_box(f"mesa_{i}", (centro_curva_x - 3 + i*2, centro_curva_y - 1, 0.5),
            (1.0, 1.0, 0.05), mat_wood)
    for dx in [-0.8, 0.8]:
        for dy in [-0.8, 0.8]:
            add_box(f"silla_{i}_{dx}_{dy}", (centro_curva_x - 3 + i*2 + dx, centro_curva_y - 1 + dy, 0.3),
                    (0.4, 0.4, 0.6), mat_metal)

# ============== TECHOS Y CUBIERTA ==============
add_box("techo_principal", (0, 0, NUM_PISOS*ALTURA_PISO + ESPESOR_LOSA/2),
        (ANCHO + VOLADIZO + 1, PROFUNDO + VOLADIZO + 1, ESPESOR_LOSA),
        mat_white)

# Cubierta superior más alta
add_box("cubierta_alta", (-2, 0, NUM_PISOS*ALTURA_PISO + 1.5),
        (ANCHO - 8, PROFUNDO - 4, 2.5),
        mat_white)

# Pérgola en esquina superior
for i in range(6):
    add_box(f"pergola_v_{i}", (-2 + i*1.5, PROFUNDO/2 + VOLADIZO - 0.3, NUM_PISOS*ALTURA_PISO + 0.8),
            (0.1, 0.1, 1.2),
            mat_metal)
add_box("pergola_top", (-2 + 5*0.75, PROFUNDO/2 + VOLADIZO - 0.3, NUM_PISOS*ALTURA_PISO + 1.4),
        (8.5, 0.1, 0.08),
        mat_metal)

# ============== CALLE Y ACERA ==============
add_box("acera", (ANCHO/4, -PROFUNDO/2 + 4, 0.05), (40, 8, 0.1), mat_concrete)
add_box("calle", (ANCHO/4 + 6, -PROFUNDO/2 + 9, 0.02), (40, 8, 0.04), mat_asfalto)

# Líneas peatonales
for i in range(6):
    add_box(f"linea_{i}", (ANCHO/4 - 1.5 + i*0.6, -PROFUNDO/2 + 12.5, 0.05),
            (0.4, 0.8, 0.01), mat_white)

# Edificio de fondo (a la izquierda)
add_box("edificio_fondo", (-18, 0, 6), (8, 12, 12), mat_concrete)
# Ventanas del edificio de fondo
for fila in range(3):
    for col in range(4):
        add_box(f"vent_fondo_{fila}_{col}", (-18 + col*1.7 - 2.5, -6, 3 + fila*3),
                (1.0, 0.05, 1.5), mat_glass)

# ============== ILUMINACIÓN Y CÁMARA ==============
bpy.ops.object.camera_add(location=(ANCHO + 18, -PROFUNDO - 5, 8))
cam = bpy.context.active_object
cam.name = "CamPrincipal"
# Apuntar al centro del edificio
cam.rotation_euler = (math.radians(57), 0, math.radians(50))
bpy.context.scene.camera = cam

# Sol
bpy.ops.object.light_add(type='SUN', location=(15, -10, 25))
sun = bpy.context.active_object
sun.name = "Sol"
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
sun.data.color = (1.0, 0.95, 0.85)

# Luz de relleno
bpy.ops.object.light_add(type='AREA', location=(-10, 15, 12))
fill = bpy.context.active_object
fill.data.energy = 200
fill.data.size = 8

# ============== SKY ==============
if bpy.context.scene.world is None:
    bpy.context.scene.world = bpy.data.worlds.new("World")
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
bg = world_nodes.get("Background")
if bg is None:
    bg = world_nodes.new("ShaderNodeBackground")
    # Conectar a world output
    out = world_nodes.get("World Output")
    if out:
        world_links = bpy.context.scene.world.node_tree.links
        for link in world_links:
            pass
bg.inputs['Color'].default_value = (0.55, 0.75, 0.95, 1.0)
bg.inputs['Strength'].default_value = 1.5

# ============== RENDER SETTINGS ==============
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.view_settings.exposure = 1.0

# ============== GUARDAR ==============
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
print(f"\n✅ Edificio guardado en: {OUTPUT}")

# Renderizar preview
preview_path = OUTPUT.replace(".blend", "_preview.png")
bpy.context.scene.render.filepath = preview_path
bpy.ops.render.render(write_still=True)
print(f"🖼️  Preview: {preview_path}")

# Contar objetos
n = len([o for o in bpy.data.objects if o.name in [obj.name for obj in collection.objects]])
print(f"📦 Objetos en colección Edificio: {n}")
