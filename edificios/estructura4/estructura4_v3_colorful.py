"""
Estructura 4 v3 - SHOWROOM MULTICOLOR + MAGIA (versión simplificada y robusta)
"""
import bpy
import math
import random
from mathutils import Vector

random.seed(42)

# Limpiar
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ============================================================================
# PALETA DE COLORES
# ============================================================================
NEON_PINK = (1.0, 0.08, 0.58)
NEON_PURPLE = (0.7, 0.1, 1.0)
NEON_CYAN = (0.0, 0.95, 1.0)
NEON_BLUE = (0.1, 0.3, 1.0)
NEON_GREEN = (0.1, 1.0, 0.4)
NEON_YELLOW = (1.0, 0.9, 0.0)
NEON_ORANGE = (1.0, 0.5, 0.0)
NEON_MAGENTA = (1.0, 0.0, 0.8)
NEON_RED = (1.0, 0.1, 0.2)

GRADIENT = [NEON_RED, NEON_ORANGE, NEON_YELLOW, NEON_GREEN,
            NEON_CYAN, NEON_BLUE, NEON_PURPLE, NEON_MAGENTA]

# ============================================================================
# MATERIALES (simple y robusto)
# ============================================================================
def mat_emissive(name, color, strength=3.0):
    """Material emisivo simple"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = strength
    return mat

# ============================================================================
# CONSTRUIR ESCENA
# ============================================================================

# Suelo oscuro
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
mat = mat_emissive("FloorMat", (0.02, 0.02, 0.05), 0.1)
floor.data.materials.append(mat)

# Anillos LED multicolor (5 anillos concéntricos)
ring_radii = [(5.5, 7.5, 0.12), (4.2, 6.5, 0.10), (3.0, 5.5, 0.08),
              (7.0, 8.5, 0.06), (2.0, 4.0, 0.07)]

for idx, (radius, height, thickness) in enumerate(ring_radii):
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, height),
        major_radius=radius,
        minor_radius=thickness,
        major_segments=32,
        minor_segments=12
    )
    ring = bpy.context.active_object
    ring.name = f"Ring_{idx}"

    # Cada anillo un color sólido del gradiente (varía según idx)
    color = GRADIENT[idx % len(GRADIENT)]
    mat = mat_emissive(f"RingMat_{idx}", color, strength=5.0)
    ring.data.materials.append(mat)
    ring.rotation_euler[2] = idx * 0.3

# 8 pilares de luz verticales multicolor (en círculo)
pillar_positions = [
    (-7, -7), (7, -7), (-7, 7), (7, 7),
    (0, -8), (8, 0), (0, 8), (-8, 0)
]
pillar_colors = GRADIENT + [NEON_PINK, NEON_CYAN]

for idx, ((x, y), color) in enumerate(zip(pillar_positions, pillar_colors)):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.25, depth=7.0,
        location=(x, y, 3.5)
    )
    pillar = bpy.context.active_object
    pillar.name = f"Pillar_{idx}"
    mat = mat_emissive(f"PillarMat_{idx}", color, strength=4.0)
    pillar.data.materials.append(mat)

# Grid de líneas neón en el suelo (estilo Tron)
for i in range(-6, 7, 2):
    # Color varía según posición (degradado)
    t = (i + 6) / 12
    color = GRADIENT[int(t * (len(GRADIENT) - 1))]

    # Línea horizontal
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i, 0, 0.03))
    line = bpy.context.active_object
    line.name = f"StripX_{i}"
    line.scale = (0.04, 12, 0.005)
    mat = mat_emissive(f"StripXMat_{i}", color, strength=3.0)
    line.data.materials.append(mat)

    # Línea vertical
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, i, 0.03))
    line = bpy.context.active_object
    line.name = f"StripY_{i}"
    line.scale = (12, 0.04, 0.005)
    mat = mat_emissive(f"StripYMat_{i}", color, strength=3.0)
    line.data.materials.append(mat)

# Zonas circulares de color en el suelo (focos)
zone_positions = [(-4, -4), (4, -4), (-4, 4), (4, 4),
                  (0, 0), (-6, 0), (6, 0), (0, -6), (0, 6)]
zone_colors = [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN,
               NEON_PURPLE, NEON_ORANGE, NEON_MAGENTA, NEON_BLUE, NEON_RED]

for idx, ((x, y), color) in enumerate(zip(zone_positions, zone_colors)):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.0, depth=0.02,
        location=(x, y, 0.01)
    )
    zone = bpy.context.active_object
    zone.name = f"Zone_{idx}"
    mat = mat_emissive(f"ZoneMat_{idx}", color, strength=3.0)
    zone.data.materials.append(mat)

# 6 esferas brillantes (showroom central) - colores diferentes
for i in range(6):
    angle = (i / 6) * 2 * math.pi
    x = math.cos(angle) * 3
    y = math.sin(angle) * 3
    z = 1.5

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(x, y, z))
    sphere = bpy.context.active_object
    sphere.name = f"ShowSphere_{i}"
    color = GRADIENT[i]
    mat = mat_emissive(f"SphereMat_{i}", color, strength=5.0)
    sphere.data.materials.append(mat)

# Esfera central gigante (escultura)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 1.5))
center = bpy.context.active_object
center.name = "CentralSculpture"
mat = mat_emissive("CenterMat", NEON_MAGENTA, strength=6.0)
center.data.materials.append(mat)

# 30 partículas flotantes (chispas brillantes)
for i in range(30):
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    z = random.uniform(2, 6)

    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=random.uniform(0.1, 0.3),
        location=(x, y, z)
    )
    particle = bpy.context.active_object
    particle.name = f"Particle_{i}"
    color = random.choice(GRADIENT)
    mat = mat_emissive(f"ParticleMat_{i}", color, strength=8.0)
    particle.data.materials.append(mat)

# 4 anillos orbitales alrededor del centro
for i in range(4):
    angle = i * (math.pi / 4)
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, 1.5),
        major_radius=2.2,
        minor_radius=0.04,
        major_segments=32,
        minor_segments=8
    )
    orbital = bpy.context.active_object
    orbital.name = f"Orbital_{i}"
    orbital.rotation_euler = (angle, angle * 0.6, angle * 0.4)
    color = GRADIENT[i + 2]
    mat = mat_emissive(f"OrbitalMat_{i}", color, strength=6.0)
    orbital.data.materials.append(mat)

# ============================================================================
# ILUMINACIÓN
# ============================================================================

# Luz principal blanca (key light)
bpy.ops.object.light_add(type='AREA', location=(0, 0, 10))
key_light = bpy.context.active_object
key_light.data.energy = 400
key_light.data.color = (1.0, 0.95, 0.85)
key_light.data.size = 12

# Luz ambiental suave blanca
bpy.ops.object.light_add(type='AREA', location=(0, 0, 8))
ambient = bpy.context.active_object
ambient.data.energy = 100
ambient.data.color = (1.0, 1.0, 1.0)
ambient.data.size = 30

# 6 luces de colores en el perímetro
light_colors = [NEON_PINK, NEON_CYAN, NEON_GREEN,
                NEON_YELLOW, NEON_PURPLE, NEON_ORANGE]
for i, color in enumerate(light_colors):
    angle = (i / 6) * 2 * math.pi
    x = math.cos(angle) * 10
    y = math.sin(angle) * 10

    bpy.ops.object.light_add(type='POINT', location=(x, y, 4))
    light = bpy.context.active_object
    light.name = f"ColorLight_{i}"
    light.data.energy = 200
    light.data.color = color

# ============================================================================
# CÁMARA Y RENDER
# ============================================================================

# Cámara
bpy.ops.object.camera_add(location=(12, -10, 7))
cam = bpy.context.active_object
cam.name = "MainCamera"
cam.data.lens = 35

# Apuntar al centro
direction = Vector((0, 0, 2)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam

# Render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Background negro
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()
bg = nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.005, 0.005, 0.015, 1.0)
output = nodes.new('ShaderNodeOutputWorld')
world.node_tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

# Render
output_path = '/Users/hectoraguilar/.hermes/image_cache/estructura4_v3_colorful.png'
scene.render.filepath = output_path

print("="*70)
print("ESTRUCTURA 4 v3 - SHOWROOM MULTICOLOR + MAGIA")
print("="*70)

total_objs = len([o for o in bpy.data.objects if o.type == 'MESH'])
total_lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
print(f"\n📊 {total_objs} objetos, {total_lights} luces")
print("\n🎬 Renderizando...")
bpy.ops.render.render(write_still=True)
print(f"✅ Guardado en {output_path}")
