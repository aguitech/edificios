"""
Test minimalista - verificar que el render funciona
"""
import bpy
import math
from mathutils import Vector

# Limpiar
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Mundo negro
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
nodes.clear()
bg = nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1.0)
output = nodes.new('ShaderNodeOutputWorld')
world.node_tree.links.new(bg.outputs['Background'], output.inputs['Surface'])

# Plano del suelo (referencia espacial)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
plane = bpy.context.active_object
mat = bpy.data.materials.new("PlaneMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.3
plane.data.materials.append(mat)

# Cubo ROJO
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube_red = bpy.context.active_object
mat_red = bpy.data.materials.new("RedMat")
mat_red.use_nodes = True
bsdf = mat_red.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (1.0, 0.1, 0.1, 1.0)
bsdf.inputs['Emission Color'].default_value = (1.0, 0.1, 0.1, 1.0)
bsdf.inputs['Emission Strength'].default_value = 3.0
cube_red.data.materials.append(mat_red)

# Esfera VERDE
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(3, 0, 1.2))
sphere_green = bpy.context.active_object
mat_green = bpy.data.materials.new("GreenMat")
mat_green.use_nodes = True
bsdf = mat_green.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.1, 1.0, 0.2, 1.0)
bsdf.inputs['Emission Color'].default_value = (0.1, 1.0, 0.2, 1.0)
bsdf.inputs['Emission Strength'].default_value = 3.0
sphere_green.data.materials.append(mat_green)

# Toro AZUL
bpy.ops.mesh.primitive_torus_add(location=(-3, 0, 1.5), major_radius=1.0, minor_radius=0.3)
torus_blue = bpy.context.active_object
mat_blue = bpy.data.materials.new("BlueMat")
mat_blue.use_nodes = True
bsdf = mat_blue.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 1.0, 1.0)
bsdf.inputs['Emission Color'].default_value = (0.1, 0.3, 1.0, 1.0)
bsdf.inputs['Emission Strength'].default_value = 3.0
torus_blue.data.materials.append(mat_blue)

# Luz principal
bpy.ops.object.light_add(type='AREA', location=(0, 0, 10))
light = bpy.context.active_object
light.data.energy = 500
light.data.size = 10
light.data.color = (1.0, 1.0, 1.0)

# Luz de color magenta
bpy.ops.object.light_add(type='POINT', location=(5, 5, 5))
light2 = bpy.context.active_object
light2.data.energy = 500
light2.data.color = (1.0, 0.0, 1.0)

# Cámara
bpy.ops.object.camera_add(location=(10, -8, 6))
cam = bpy.context.active_object
cam.data.lens = 35
direction = Vector((0, 0, 1)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# Render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

scene.render.filepath = '/Users/hectoraguilar/.hermes/image_cache/test_minimal.png'

print("🎬 Renderizando test...")
bpy.ops.render.render(write_still=True)
print("✅ Test render OK")
