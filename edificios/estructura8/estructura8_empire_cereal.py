"""
estructura8 — Caja de cereal "Empire" con textura empire.png
=============================================================

Crea una caja de cereal 3D renderizada con la imagen empire.png mapeada
como etiqueta/envoltura. Inspirado en la estética de la imagen: nocturna,
rascacielos con neón azul-púrpura, fondo oscuro.

Render → estructura8/imagenes/empire.png
Blend  → estructura8/empire.blend
"""

import bpy
import math
import os
import sys
import traceback

# Log a archivo para debuggear (Blender trunca stdout)
LOG_FILE = "/tmp/empire_script.log"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")
        f.flush()

# Limpiar log anterior
try:
    os.remove(LOG_FILE)
except FileNotFoundError:
    pass

log("=" * 60)
log("SCRIPT INICIADO")
log("=" * 60)
log(f"Blender {bpy.app.version_string}")
log(f"Python {sys.version.split()[0]}")


def safe_run(label, fn):
    """Ejecuta fn() capturando errores y escribiéndolos al log."""
    log(f"  {label}...")
    try:
        fn()
        log(f"  {label} OK")
    except Exception:
        log(f"  {label} ERROR:\n{traceback.format_exc()}")
        raise


try:
    # ─────────────────────────────────────────────────────────────────
    # RUTAS
    # ─────────────────────────────────────────────────────────────────
    SCRIPT_DIR = "/Users/hectoraguilar/Projects/edificio/edificios/estructura8"
    IMAGES_DIR = os.path.join(SCRIPT_DIR, "imagenes")
    TEXTURE_PATH = os.path.join(IMAGES_DIR, "empire_source.png")
    RENDER_PATH = os.path.join(IMAGES_DIR, "empire.png")
    BLEND_PATH = os.path.join(SCRIPT_DIR, "empire.blend")

    BOX_W = 0.20
    BOX_H = 0.30
    BOX_D = 0.08

    # ─────────────────────────────────────────────────────────────────
    # LIMPIAR ESCENA
    # ─────────────────────────────────────────────────────────────────
    safe_run("STEP 1: Limpiando escena",
        lambda: bpy.ops.wm.read_factory_settings(use_empty=True))

    # ─────────────────────────────────────────────────────────────────
    # CREAR CAJA
    # ─────────────────────────────────────────────────────────────────
    def create_box():
        global box
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, BOX_H / 2))
        box = bpy.context.active_object
        box.name = "EmpireCerealBox"
        box.scale = (BOX_W, BOX_D, BOX_H)
        bpy.ops.object.modifier_add(type="BEVEL")
        bevel = box.modifiers["Bevel"]
        bevel.width = 0.003
        bevel.segments = 2
    safe_run("STEP 2: Crear caja", create_box)

    # ─────────────────────────────────────────────────────────────────
    # MATERIAL CON TEXTURA
    # ─────────────────────────────────────────────────────────────────
    def create_material():
        global mat
        mat = bpy.data.materials.new(name="EmpireTexture")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        for node in nodes:
            nodes.remove(node)

        tex_coord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        tex_image = nodes.new("ShaderNodeTexImage")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial")

        tex_coord.location = (-600, 0)
        mapping.location = (-400, 0)
        mapping.vector_type = "POINT"
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
        mapping.inputs["Location"].default_value = (0.0, 0.0, 0.0)

        img = bpy.data.images.load(TEXTURE_PATH)
        tex_image.image = img

        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Roughness"].default_value = 0.55
        bsdf.inputs["Specular IOR Level"].default_value = 0.3

        links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], tex_image.inputs["Vector"])
        links.new(tex_image.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        box.data.materials.append(mat)
    safe_run("STEP 3: Crear material con textura", create_material)

    # ─────────────────────────────────────────────────────────────────
    # ILUMINACIÓN
    # ─────────────────────────────────────────────────────────────────
    def create_lights():
        # Key light
        bpy.ops.object.light_add(type="AREA", location=(0.4, -0.3, 0.6))
        key = bpy.context.active_object
        key.data.energy = 80
        key.data.color = (1.0, 0.95, 0.88)
        key.data.size = 0.3
        key.name = "KeyLight"

        # Fill light
        bpy.ops.object.light_add(type="AREA", location=(-0.5, 0.3, 0.4))
        fill = bpy.context.active_object
        fill.data.energy = 30
        fill.data.color = (0.55, 0.65, 1.0)
        fill.data.size = 0.5
        fill.name = "FillLight"

        # Rim light
        bpy.ops.object.light_add(type="SPOT", location=(0.0, 0.6, 0.5))
        rim = bpy.context.active_object
        rim.data.energy = 50
        rim.data.color = (0.45, 0.50, 1.0)
        rim.data.spot_size = math.radians(60)
        rim.name = "RimNeonLight"
        rim.rotation_euler = (math.radians(180), 0, 0)

        # Neon accent
        bpy.ops.object.light_add(type="SPOT", location=(0.15, -0.4, 0.45))
        neon = bpy.context.active_object
        neon.data.energy = 40
        neon.data.color = (0.45, 0.50, 1.0)
        neon.data.spot_size = math.radians(45)
        neon.rotation_euler = (math.radians(50), 0, 0)
        neon.name = "NeonAccent"
    safe_run("STEP 4: Crear 4 luces", create_lights)

    # ─────────────────────────────────────────────────────────────────
    # PISO
    # ─────────────────────────────────────────────────────────────────
    def create_floor():
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
        floor = bpy.context.active_object
        floor.name = "Floor"

        fmat = bpy.data.materials.new("FloorMat")
        fmat.use_nodes = True
        fbsdf = fmat.node_tree.nodes["Principled BSDF"]
        fbsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.07, 1)
        fbsdf.inputs["Roughness"].default_value = 0.6
        floor.data.materials.append(fmat)
    safe_run("STEP 5: Crear piso", create_floor)

    # ─────────────────────────────────────────────────────────────────
    # FONDO (World)
    # ─────────────────────────────────────────────────────────────────
    def setup_world():
        world = bpy.data.worlds.new("EmpireWorld")
        bpy.context.scene.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes["Background"]
        bg.inputs["Color"].default_value = (0.02, 0.02, 0.04, 1.0)
        bg.inputs["Strength"].default_value = 0.3
    safe_run("STEP 6: Configurar fondo", setup_world)

    # ─────────────────────────────────────────────────────────────────
    # CÁMARA
    # ─────────────────────────────────────────────────────────────────
    def create_camera():
        bpy.ops.object.camera_add(location=(0.5, -0.6, 0.35),
                                   rotation=(math.radians(75), 0, math.radians(50)))
        cam = bpy.context.active_object
        bpy.context.scene.camera = cam
        cam.data.lens = 50
        cam.data.sensor_width = 36
    safe_run("STEP 7: Crear cámara", create_camera)

    # ─────────────────────────────────────────────────────────────────
    # RENDER
    # ─────────────────────────────────────────────────────────────────
    def configure_render():
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.film_transparent = False
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.filepath = RENDER_PATH
    safe_run("STEP 8: Configurar render", configure_render)

    log("")
    log(f"📊 {len(bpy.data.objects)} objetos, {len(bpy.data.lights)} luces")
    log(f"🎬 Renderizando → {RENDER_PATH}")

    bpy.ops.render.render(write_still=True)
    log("✅ Render completado")

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    log(f"✅ .blend guardado en {BLEND_PATH}")

except Exception:
    log(f"\n❌ SCRIPT ABORTADO:\n{traceback.format_exc()}")
    raise

log("=" * 60)
log("SCRIPT FINALIZADO OK")
log("=" * 60)
