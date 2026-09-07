"""
ESTRUCTURA 6 — CONCESIONARIA FERRARI PREMIUM
Showroom de cristal + panel rojo Ferrari + Ferraris expuestos
Inspirado en la referencia: concesionaria Ferrari H.R. Owen al atardecer
"""
import bpy
import math
import random
from mathutils import Vector

random.seed(7)

# Limpiar
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ============================================================================
# PALETA FERRARI
# ============================================================================
FERRARI_RED = (0.85, 0.05, 0.08)
ROSSO_CORSA = (0.92, 0.08, 0.10)
DARK_RED = (0.5, 0.02, 0.05)
FERRARI_YELLOW = (1.0, 0.85, 0.0)
FERRARI_BLACK = (0.02, 0.02, 0.02)
GLASS_DARK = (0.05, 0.08, 0.12)
GLASS_LIT = (1.0, 0.85, 0.6)
WHITE_PURE = (0.95, 0.95, 0.95)
CONCRETE = (0.3, 0.3, 0.32)
WARM_WHITE = (1.0, 0.92, 0.78)
NIGHT_BLUE = (0.05, 0.07, 0.15)
SKY_BLUE = (0.15, 0.2, 0.35)
TREE_GREEN = (0.1, 0.3, 0.12)

# ============================================================================
# MATERIALES
# ============================================================================
def mat_simple(name, color, roughness=0.4, metallic=0.0, emissive=0.0, emit_color=None):
    """Material PBR simple"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emissive > 0:
        ec = emit_color if emit_color else color
        bsdf.inputs['Emission Color'].default_value = (*ec, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emissive
    return mat

def mat_glass(name, color=GLASS_DARK, alpha=0.3, emissive=2.0):
    """Material de cristal emisivo (ventana iluminada)"""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Alpha'].default_value = alpha
    bsdf.inputs['Emission Color'].default_value = (*GLASS_LIT, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emissive
    mat.blend_method = 'BLEND'
    return mat

# ============================================================================
# EDIFICIO CONCESIONARIA (2 niveles)
# ============================================================================

def create_building():
    """Edificio 2 pisos: cristal abajo + panel rojo arriba con logo"""

    # ========================================================================
    # PLANTA BAJA - SHOROOM DE CRISTAL
    # ========================================================================

    # Piso interior del showroom (concreto pulido)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.05))
    interior_floor = bpy.context.active_object
    interior_floor.name = "InteriorFloor"
    interior_floor.scale = (22, 11, 1)
    mat = mat_simple("InteriorFloorMat", (0.25, 0.22, 0.2), roughness=0.15, metallic=0.0)
    interior_floor.data.materials.append(mat)

    # ========================================================================
    # PARED TRASERA DEL SHOWROOM (con escritorios y luces)
    # ========================================================================
    # Pared trasera (dentro del showroom)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.4, 4))
    back_wall = bpy.context.active_object
    back_wall.name = "BackWall"
    back_wall.scale = (22, 0.4, 8)
    mat = mat_simple("BackWallMat", (0.7, 0.65, 0.6), roughness=0.5)
    back_wall.data.materials.append(mat)

    # ========================================================================
    # MARCO METÁLICO DEL CRISTAL (estructura de la fachada)
    # ========================================================================

    # Vigas verticales de la fachada (separadores de cristal)
    num_panels = 13  # 13 paneles de cristal
    facade_width = 22
    for i in range(num_panels + 1):
        x = -facade_width/2 + i * (facade_width / num_panels)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 5.5, 4))
        pillar = bpy.context.active_object
        pillar.name = f"FacadePillar_{i}"
        pillar.scale = (0.08, 0.15, 8)
        mat = mat_simple("PillarMat", (0.05, 0.05, 0.05), roughness=0.3, metallic=0.8)
        pillar.data.materials.append(mat)

    # Vigas horizontales de la fachada
    for y_pos in [-5.3, 5.3]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y_pos, 4))
        beam = bpy.context.active_object
        beam.name = f"FacadeBeam_{y_pos}"
        beam.scale = (22, 0.1, 0.15)
        mat = mat_simple("BeamMat", (0.05, 0.05, 0.05), roughness=0.3, metallic=0.8)
        beam.data.materials.append(mat)

    # Viga horizontal superior
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.5, 7.9))
    top_beam = bpy.context.active_object
    top_beam.name = "TopBeam"
    top_beam.scale = (22, 0.15, 0.2)
    mat = mat_simple("TopBeamMat", (0.05, 0.05, 0.05), roughness=0.3, metallic=0.8)
    top_beam.data.materials.append(mat)

    # ========================================================================
    # PANELES DE CRISTAL (entre los pilares) - 13 paneles iluminados
    # ========================================================================
    panel_width = facade_width / num_panels
    for i in range(num_panels):
        x = -facade_width/2 + (i + 0.5) * panel_width
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 5.4, 4))
        panel = bpy.context.active_object
        panel.name = f"GlassPanel_{i}"
        panel.scale = (panel_width - 0.12, 0.05, 7.7)
        mat = mat_glass(f"GlassMat_{i}", GLASS_DARK, alpha=0.4, emissive=3.0)
        panel.data.materials.append(mat)

    # ========================================================================
    # SEGUNDO NIVEL — PANEL ROJO FERRARI (con logo)
    # ========================================================================

    # Panel rojo principal (parte superior)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.7, 10))
    red_panel = bpy.context.active_object
    red_panel.name = "RedPanel"
    red_panel.scale = (24, 1.5, 4)
    mat = mat_simple("RedPanelMat", FERRARI_RED, roughness=0.2, metallic=0.1,
                     emissive=2.5, emit_color=FERRARI_RED)
    red_panel.data.materials.append(mat)

    # Panel rojo extendido hacia atrás
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.5, 10.2))
    red_top = bpy.context.active_object
    red_top.name = "RedTop"
    red_top.scale = (26, 3, 4.5)
    mat = mat_simple("RedTopMat", DARK_RED, roughness=0.3)
    red_top.data.materials.append(mat)

    # ========================================================================
    # LETRERO "Ferrari" (simulado con cilindros como letras estilizadas)
    # ========================================================================
    # Voy a usar texto 3D si está disponible, sino un cubo plano con texto como textura

    # Panel frontal con el letrero (cubo grande blanco donde va el texto)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-7, 6.4, 10.2))
    sign_panel = bpy.context.active_object
    sign_panel.name = "FerrariSign"
    sign_panel.scale = (7, 0.2, 2.2)
    mat = mat_simple("SignMat", WHITE_PURE, roughness=0.3, emissive=8.0, emit_color=WARM_WHITE)
    sign_panel.data.materials.append(mat)

    # Texto real con Text Object
    bpy.ops.object.text_add(location=(-7, 6.5, 10.2))
    text_obj = bpy.context.active_object
    text_obj.name = "FerrariText"
    text_obj.data.body = "Ferrari"
    text_obj.data.size = 1.2
    text_obj.data.extrude = 0.05
    text_obj.data.bevel_depth = 0.02
    text_obj.data.align_x = 'CENTER'
    text_obj.data.align_y = 'CENTER'
    text_obj.rotation_euler = (0, 0, 0)
    text_mat = mat_simple("FerrariTextMat", FERRARI_RED, roughness=0.3,
                          emissive=0.5, emit_color=FERRARI_RED)
    text_obj.data.materials.append(text_mat)

    # Segundo letrero "H.R. Owen" (lado derecho)
    bpy.ops.object.text_add(location=(7, 6.5, 10.2))
    text_obj2 = bpy.context.active_object
    text_obj2.name = "HROwenText"
    text_obj2.data.body = "H.R. Owen"
    text_obj2.data.size = 0.5
    text_obj2.data.extrude = 0.05
    text_obj2.data.bevel_depth = 0.01
    text_obj2.data.align_x = 'CENTER'
    text_obj2.data.align_y = 'CENTER'
    text_mat2 = mat_simple("HROwenMat", WARM_WHITE, roughness=0.3,
                           emissive=4.0, emit_color=WARM_WHITE)
    text_obj2.data.materials.append(text_mat2)

    # ========================================================================
    # CUBIERTA / TECHO DEL SEGUNDO NIVEL
    # ========================================================================
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5, 12.5))
    roof = bpy.context.active_object
    roof.name = "Roof"
    roof.scale = (25, 4, 0.3)
    mat = mat_simple("RoofMat", (0.15, 0.15, 0.17), roughness=0.4, metallic=0.3)
    roof.data.materials.append(mat)

    # ========================================================================
    # LATERALES DEL EDIFICIO (paredes laterales rojo oscuro)
    # ========================================================================
    for x_pos in [-12.5, 12.5]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 4, 7))
        side = bpy.context.active_object
        side.name = f"Side_{x_pos}"
        side.scale = (1.5, 10, 14)
        mat = mat_simple("SideMat", DARK_RED, roughness=0.4)
        side.data.materials.append(mat)

    # ========================================================================
    # UPLIGHTS EN LA PARED (luces rojas en el suelo apuntando arriba)
    # ========================================================================
    for x_pos in [-10, -5, 0, 5, 10]:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.15, depth=0.5,
            location=(x_pos, 4.0, 0.25)
        )
        uplight = bpy.context.active_object
        uplight.name = f"Uplight_{x_pos}"
        mat = mat_simple(f"UplightMat_{x_pos}", FERRARI_RED, emissive=10.0,
                         emit_color=FERRARI_RED)
        uplight.data.materials.append(mat)

    # ========================================================================
    # LOGO FERRARI (caballito rampante) - simplificado con cubos
    # ========================================================================
    # Logo izquierdo
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-10.5, 5.5, 11))
    logo_left = bpy.context.active_object
    logo_left.name = "FerrariLogo"
    logo_left.scale = (0.8, 0.1, 1.2)
    mat = mat_simple("LogoMat", FERRARI_YELLOW, roughness=0.2,
                     emissive=5.0, emit_color=FERRARI_YELLOW)
    logo_left.data.materials.append(mat)

    # Logo derecho
    bpy.ops.mesh.primitive_cube_add(size=1, location=(10.5, 5.5, 11))
    logo_right = bpy.context.active_object
    logo_right.name = "FerrariLogo2"
    logo_right.scale = (0.8, 0.1, 1.2)
    logo_right.data.materials.append(mat_simple("LogoMat2", FERRARI_YELLOW,
                                                  roughness=0.2, emissive=5.0,
                                                  emit_color=FERRARI_YELLOW))


# ============================================================================
# FERRARIS (low-poly)
# ============================================================================
def create_ferrari(name, color, x, y, z=0.0, rotation=0):
    """Crea un Ferrari low-poly con cuerpo + cabina + ruedas"""
    parent = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(parent)
    parent.location = (x, y, z)
    parent.rotation_euler = (0, 0, rotation)

    # Cuerpo principal (forma de Ferrari - bajo y ancho)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    body = bpy.context.active_object
    body.name = f"{name}_body"
    body.scale = (1.8, 0.8, 0.35)
    body.parent = parent
    mat = mat_simple(f"{name}_body_mat", color, roughness=0.15, metallic=0.7,
                     emissive=0.3, emit_color=color)
    body.data.materials.append(mat)

    # Cabina (más pequeña, encima)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.1, 0, 0.78))
    cabin = bpy.context.active_object
    cabin.name = f"{name}_cabin"
    cabin.scale = (0.9, 0.7, 0.3)
    cabin.parent = parent
    mat = mat_simple(f"{name}_cabin_mat", color, roughness=0.1, metallic=0.8,
                     emissive=0.2, emit_color=color)
    cabin.data.materials.append(mat)

    # Capó frontal (más bajo y largo)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.7, 0, 0.45))
    hood = bpy.context.active_object
    hood.name = f"{name}_hood"
    hood.scale = (0.7, 0.75, 0.25)
    hood.parent = parent
    hood.data.materials.append(mat)

    # Parabrisas (oscuro, ligeramente inclinado)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.2, 0, 0.92))
    windshield = bpy.context.active_object
    windshield.name = f"{name}_windshield"
    windshield.scale = (0.7, 0.65, 0.1)
    windshield.parent = parent
    mat_glass = mat_simple(f"{name}_glass_mat", (0.05, 0.05, 0.1), roughness=0.05,
                           metallic=0.0, emissive=0.1, emit_color=(0.2, 0.4, 0.6))
    windshield.data.materials.append(mat_glass)

    # 4 ruedas (cilindros negros)
    wheel_positions = [
        (0.65, 0.45, 0.25),    # Delantera derecha
        (0.65, -0.45, 0.25),   # Delantera izquierda
        (-0.65, 0.45, 0.25),   # Trasera derecha
        (-0.65, -0.45, 0.25),  # Trasera izquierda
    ]
    for i, (wx, wy, wz) in enumerate(wheel_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.18, depth=0.15,
            location=(wx, wy, wz)
        )
        wheel = bpy.context.active_object
        wheel.name = f"{name}_wheel_{i}"
        wheel.rotation_euler = (math.pi/2, 0, 0)
        wheel.parent = parent
        mat_wheel = mat_simple(f"{name}_wheel_mat", FERRARI_BLACK, roughness=0.6)
        wheel.data.materials.append(mat_wheel)

    # Faros delanteros (emisivos)
    for wx in [0.95, 0.95]:
        for wy in [0.3, -0.3]:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.08, location=(wx, wy, 0.5)
            )
            light = bpy.context.active_object
            light.name = f"{name}_headlight"
            light.parent = parent
            mat_light = mat_simple(f"{name}_light_mat", WARM_WHITE, emissive=8.0,
                                    emit_color=(1.0, 0.95, 0.8))
            light.data.materials.append(mat_light)

    # Luces traseras rojas
    for wx in [-0.95, -0.95]:
        for wy in [0.3, -0.3]:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=0.07, location=(wx, wy, 0.5)
            )
            light = bpy.context.active_object
            light.name = f"{name}_taillight"
            light.parent = parent
            mat_light = mat_simple(f"{name}_taillight_mat", FERRARI_RED, emissive=4.0,
                                    emit_color=FERRARI_RED)
            light.data.materials.append(mat_light)

    return parent


def create_ferrari_lineup():
    """Línea de 7 Ferraris frente al showroom"""
    ferrari_data = [
        (FERRARI_YELLOW, -8, 9, 0.0),          # Amarillo al frente izquierda
        (ROSSO_CORSA, -4.5, 9.2, 0.05),        # Rojo clásico
        (WHITE_PURE, -1.5, 9, -0.05),          # Blanco
        (ROSSO_CORSA, 1.5, 9.2, 0.0),          # Rojo con franjas (otro rojo)
        (FERRARI_BLACK, 4.5, 9, 0.05),         # Negro
        (ROSSO_CORSA, 7.5, 9.2, -0.05),        # Rojo oscuro
        (FERRARI_YELLOW, 9.5, 7.5, 0.5),       # Extra (un poco atrás)
    ]

    for i, (color, x, y, rot) in enumerate(ferrari_data):
        create_ferrari(f"Ferrari_{i}", color, x, y, 0.0, rot)

    # Bandera amarilla Ferrari en un poste
    # Asta
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04, depth=4,
        location=(-9, 9, 2)
    )
    flagpole = bpy.context.active_object
    flagpole.name = "FlagPole"
    mat = mat_simple("FlagPoleMat", (0.3, 0.3, 0.3), roughness=0.3, metallic=0.8)
    flagpole.data.materials.append(mat)

    # Bandera (cuadrado amarillo plano)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-9, 9, 3))
    flag = bpy.context.active_object
    flag.name = "FerrariFlag"
    flag.scale = (1.2, 0.8, 1)
    flag.rotation_euler = (0, math.radians(20), math.radians(-30))
    mat = mat_simple("FlagMat", FERRARI_YELLOW, roughness=0.5,
                     emissive=0.5, emit_color=FERRARI_YELLOW)
    flag.data.materials.append(mat)

    # Logo en la bandera (caballito simplificado con cubo negro)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-9, 9, 3.1))
    flag_logo = bpy.context.active_object
    flag_logo.name = "FlagLogo"
    flag_logo.scale = (0.2, 0.15, 0.3)
    flag_logo.parent = flag
    flag_logo.rotation_euler = (0, math.radians(20), math.radians(-30))
    mat = mat_simple("FlagLogoMat", FERRARI_BLACK, roughness=0.4)
    flag_logo.data.materials.append(mat)


# ============================================================================
# ENTORNO (calle, árboles, farolas, personas)
# ============================================================================
def create_environment():
    """Calle, acera, árboles, farolas y personas"""

    # ========================================================================
    # CALLE / PAVIMENTO (asfalto)
    # ========================================================================
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 14, 0))
    street = bpy.context.active_object
    street.name = "Street"
    street.scale = (50, 16, 1)
    mat = mat_simple("StreetMat", (0.1, 0.1, 0.11), roughness=0.85, metallic=0.0)
    street.data.materials.append(mat)

    # ========================================================================
    # ACERA / PISO FRENTE AL SHOWROOM (empedrado)
    # ========================================================================
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 8.5, 0.05))
    sidewalk = bpy.context.active_object
    sidewalk.name = "Sidewalk"
    sidewalk.scale = (24, 3, 1)
    mat = mat_simple("SidewalkMat", (0.4, 0.38, 0.35), roughness=0.7)
    sidewalk.data.materials.append(mat)

    # Línea amarilla de la acera
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 7.2, 0.06))
    yellow_line = bpy.context.active_object
    yellow_line.name = "YellowLine"
    yellow_line.scale = (24, 0.1, 0.005)
    mat = mat_simple("YellowLineMat", FERRARI_YELLOW, roughness=0.4,
                     emissive=0.3, emit_color=FERRARI_YELLOW)
    yellow_line.data.materials.append(mat)

    # ========================================================================
    # ÁRBOLES (a los lados)
    # ========================================================================
    tree_positions = [
        (-14, 8.5), (-15.5, 7), (-16, 9),
        (14, 8.5), (15.5, 7), (16, 9),
    ]
    for i, (x, y) in enumerate(tree_positions):
        # Tronco
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.2, depth=3,
            location=(x, y, 1.5)
        )
        trunk = bpy.context.active_object
        trunk.name = f"Trunk_{i}"
        mat = mat_simple("TrunkMat", (0.25, 0.15, 0.08), roughness=0.9)
        trunk.data.materials.append(mat)

        # Follaje (3 esferas verdes grandes)
        for j, dy in enumerate([0, 0.4, -0.4]):
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=1.3 + random.uniform(-0.2, 0.3),
                location=(x + random.uniform(-0.3, 0.3), y + dy, 4 + j*0.3)
            )
            foliage = bpy.context.active_object
            foliage.name = f"Foliage_{i}_{j}"
            mat = mat_simple("FoliageMat", TREE_GREEN, roughness=0.85)
            foliage.data.materials.append(mat)

    # ========================================================================
    # FAROLAS (postes de luz con bombilla)
    # ========================================================================
    streetlamp_positions = [(-13, 11), (13, 11), (-6, 16), (6, 16)]
    for i, (x, y) in enumerate(streetlamp_positions):
        # Poste
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.08, depth=5,
            location=(x, y, 2.5)
        )
        pole = bpy.context.active_object
        pole.name = f"LampPost_{i}"
        mat = mat_simple("LampPostMat", (0.1, 0.1, 0.12), roughness=0.3, metallic=0.7)
        pole.data.materials.append(mat)

        # Brazo del poste
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y - 0.3, 5))
        arm = bpy.context.active_object
        arm.name = f"LampArm_{i}"
        arm.scale = (0.05, 0.5, 0.05)
        mat_arm = mat_simple("LampArmMat", (0.1, 0.1, 0.12), roughness=0.3, metallic=0.7)
        arm.data.materials.append(mat_arm)

        # Bombilla (emisiva)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.2, location=(x, y - 0.6, 4.9)
        )
        bulb = bpy.context.active_object
        bulb.name = f"Bulb_{i}"
        mat_bulb = mat_simple("BulbMat", WARM_WHITE, emissive=12.0,
                               emit_color=(1.0, 0.92, 0.7))
        bulb.data.materials.append(mat_bulb)

    # ========================================================================
    # PERSONAS (siluetas minimalistas - cilindro cuerpo + esfera cabeza)
    # ========================================================================
    person_positions = [
        (-10, 9, 0), (8, 9.5, 0), (12, 8.5, 0), (-2, 11, 0),
        (4, 11, 0), (10, 11, 0), (-7, 11, 0)
    ]
    for i, (x, y, _) in enumerate(person_positions):
        # Cuerpo
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.15, depth=0.8,
            location=(x, y, 0.9)
        )
        body = bpy.context.active_object
        body.name = f"PersonBody_{i}"
        body_color = random.choice([(0.1, 0.1, 0.15), (0.3, 0.25, 0.2),
                                     (0.4, 0.35, 0.3), (0.5, 0.4, 0.35)])
        mat = mat_simple(f"PersonMat_{i}", body_color, roughness=0.8)
        body.data.materials.append(mat)

        # Cabeza
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.12, location=(x, y, 1.45)
        )
        head = bpy.context.active_object
        head.name = f"PersonHead_{i}"
        mat_head = mat_simple(f"PersonHeadMat_{i}", (0.7, 0.55, 0.45), roughness=0.6)
        head.data.materials.append(mat_head)

        # Piernas (2 cilindros delgados)
        for side in [-0.08, 0.08]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.06, depth=0.6,
                location=(x + side, y, 0.3)
            )
            leg = bpy.context.active_object
            leg.name = f"PersonLeg_{i}"
            mat_leg = mat_simple(f"LegMat_{i}", body_color, roughness=0.8)
            leg.data.materials.append(mat_leg)


# ============================================================================
# ILUMINACIÓN DRAMÁTICA (atardecer cinematográfico)
# ============================================================================
def create_lighting():
    """Iluminación de atardecer con uplights rojos y luz cálida interior"""

    # Luz hemisférica (cielo cálido + suelo oscuro)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 20))
    sky = bpy.context.active_object
    sky.data.energy = 50
    sky.data.color = (0.4, 0.3, 0.6)  # Púrpura atardecer
    sky.data.size = 40

    # Key light desde el frente (atardecer cálido)
    bpy.ops.object.light_add(type='AREA', location=(0, 20, 15))
    key = bpy.context.active_object
    key.data.energy = 250
    key.data.color = (1.0, 0.5, 0.3)  # Naranja atardecer
    key.data.size = 25

    # Luz de relleno (lado contrario)
    bpy.ops.object.light_add(type='AREA', location=(0, -15, 10))
    fill = bpy.context.active_object
    fill.data.energy = 80
    fill.data.color = (0.3, 0.4, 0.7)  # Azul frío
    fill.data.size = 20

    # LUZ INTERIOR DEL SHOWROOM (cálida saliendo por el cristal)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    interior = bpy.context.active_object
    interior.data.energy = 200
    interior.data.color = (1.0, 0.85, 0.6)  # Cálido dorado
    interior.data.size = 20

    # Uplights rojos en pared del edificio
    for x_pos in [-10, -5, 0, 5, 10]:
        bpy.ops.object.light_add(type='SPOT', location=(x_pos, 4.5, 0.5))
        uplight = bpy.context.active_object
        uplight.data.energy = 800
        uplight.data.color = FERRARI_RED
        uplight.data.spot_size = math.radians(70)
        uplight.data.spot_blend = 0.8
        # Apuntar arriba
        direction = Vector((x_pos, 4.5, 12)) - uplight.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        uplight.rotation_euler = rot_quat.to_euler()


# ============================================================================
# CIELO DE ATARDECER
# ============================================================================
def create_sky():
    """Fondo de cielo de atardecer"""
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    # Cielo con degradado vertical (atardecer)
    bg_node = nodes.new('ShaderNodeBackground')

    # Gradient vertical
    tex = nodes.new('ShaderNodeTexGradient')
    tex.gradient_type = 'LINEAR'

    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    coord = nodes.new('ShaderNodeTexCoord')

    color_ramp = nodes.new('ShaderNodeValToRGB')
    # Cielo arriba: azul oscuro
    color_ramp.color_ramp.elements[0].color = (0.05, 0.07, 0.18, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.0

    # Medio: púrpura
    color_ramp.color_ramp.elements.new(0.5)
    color_ramp.color_ramp.elements[1].color = (0.3, 0.15, 0.35, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.5

    # Abajo: naranja atardecer
    color_ramp.color_ramp.elements.new(0.85)
    color_ramp.color_ramp.elements[2].color = (0.9, 0.4, 0.2, 1.0)
    color_ramp.color_ramp.elements[2].position = 0.85

    # Horizonte: rosa claro
    color_ramp.color_ramp.elements.new(1.0)
    color_ramp.color_ramp.elements[3].color = (0.5, 0.3, 0.4, 1.0)
    color_ramp.color_ramp.elements[3].position = 1.0

    # Conexiones
    world.node_tree.links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    world.node_tree.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    world.node_tree.links.new(tex.outputs['Fac'], color_ramp.inputs['Fac'])
    world.node_tree.links.new(color_ramp.outputs['Color'], bg_node.inputs['Color'])

    output = nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(bg_node.outputs['Background'], output.inputs['Surface'])


# ============================================================================
# CÁMARA Y RENDER
# ============================================================================
def setup_camera_and_render():
    """Cámara cinematográfica + render HD"""
    # Cámara (ángulo similar a la referencia - perspectiva 3/4 frontal)
    bpy.ops.object.camera_add(location=(15, 14, 6))
    cam = bpy.context.active_object
    cam.name = "MainCamera"
    cam.data.lens = 28  # Gran angular para capturar todo

    # Apuntar al centro del edificio
    direction = Vector((-2, 6, 8)) - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

    bpy.context.scene.camera = cam

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 96  # Calidad media para velocidad
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100

    # Color management para colores vibrantes
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    return scene


# ============================================================================
# EJECUCIÓN
# ============================================================================
print("="*70)
print("ESTRUCTURA 6 — CONCESIONARIA FERRARI PREMIUM")
print("="*70)

create_sky()
print("✓ Cielo de atardecer")

create_building()
print("✓ Edificio 2 niveles (cristal + panel rojo + letrero Ferrari)")

create_ferrari_lineup()
print("✓ 7 Ferraris low-poly en línea + bandera")

create_environment()
print("✓ Calle + acera + árboles + farolas + 7 personas")

create_lighting()
print("✓ Iluminación cinematográfica atardecer")

scene = setup_camera_and_render()
print("✓ Cámara + render configurado")

# Contar
total_objs = len([o for o in bpy.data.objects if o.type == 'MESH'])
total_lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
print(f"\n📊 {total_objs} objetos, {total_lights} luces")

# Render
output_path = '/Users/hectoraguilar/.hermes/image_cache/estructura6_ferrari.png'
scene.render.filepath = output_path
print(f"\n🎬 Renderizando → {output_path}")
bpy.ops.render.render(write_still=True)
print(f"✅ Render guardado")

# Guardar también el archivo .blend en la carpeta de estructura6 (junto al script)
blend_path = '/Users/hectoraguilar/Projects/edificio/edificios/estructura6/estructura6_ferrari.blend'
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"✅ .blend guardado en {blend_path}")
