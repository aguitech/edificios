"""
ESTRUCTURA 7 — MANSIÓN NEOCLÁSICA PREMIUM
Inspirado en mansión Beverly Hills: rotonda con columnas, alberca, jardín
"""
import bpy
import math
import random
from mathutils import Vector

random.seed(11)

# Limpiar
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ============================================================================
# PALETA
# ============================================================================
MARBLE_WHITE = (0.96, 0.94, 0.90)
WALL_CREAM = (0.94, 0.92, 0.87)
ROOF_GRAY = (0.42, 0.40, 0.38)
ROOF_DARK = (0.32, 0.30, 0.28)
WINDOW_DARK = (0.10, 0.10, 0.13)
WINDOW_FRAME = (0.85, 0.83, 0.80)
IRON_BLACK = (0.08, 0.08, 0.10)
CURTAIN_WHITE = (0.95, 0.93, 0.88)
POOL_TILE = (0.85, 0.92, 0.95)
POOL_WATER = (0.15, 0.55, 0.78)
POOL_DEEP = (0.05, 0.35, 0.65)
GRASS_GREEN = (0.30, 0.55, 0.25)
TREE_GREEN = (0.20, 0.45, 0.18)
TREE_DARK = (0.12, 0.30, 0.10)
WOOD_BROWN = (0.45, 0.28, 0.15)
WOOD_LIGHT = (0.65, 0.50, 0.32)
CUSHION_STRIPE = (0.95, 0.92, 0.88)
TERRA_BLUE = (0.20, 0.40, 0.70)
SKY_BLUE = (0.45, 0.65, 0.92)
SKY_LIGHT = (0.70, 0.83, 0.95)

# ============================================================================
# MATERIALES
# ============================================================================
def make_mat(name, color, roughness=0.4, metallic=0.0, emissive=0.0, emit_color=None):
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

def glass_mat(name, color=WINDOW_DARK, alpha=0.4, emissive=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Alpha'].default_value = alpha
    bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
    bsdf.inputs['Emission Strength'].default_value = emissive
    mat.blend_method = 'BLEND'
    return mat

# ============================================================================
# MANSIÓN PRINCIPAL
# ============================================================================
def create_mansion():
    """Mansión 2 pisos estilo neoclásico"""

    # ========================================================================
    # CUERPO PRINCIPAL DE LA MANSIÓN
    # ========================================================================

    # Planta baja - bloque principal (32m ancho x 14m fondo x 6m alto)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3))
    ground_floor = bpy.context.active_object
    ground_floor.name = "MansionGroundFloor"
    ground_floor.scale = (32, 14, 6)
    m = make_mat("GroundFloorMat", WALL_CREAM, roughness=0.6)
    ground_floor.data.materials.append(m)

    # Segundo piso (32m ancho x 14m fondo x 4m alto, encima del primero)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 8))
    second_floor = bpy.context.active_object
    second_floor.name = "MansionSecondFloor"
    second_floor.scale = (32, 14, 4)
    m = make_mat("SecondFloorMat", WALL_CREAM, roughness=0.6)
    second_floor.data.materials.append(m)

    # ========================================================================
    # ROTONDA CENTRAL (saliente semicircular al frente)
    # ========================================================================

    # Cilindro achatado (la rotonda) - sale del frente del edificio
    bpy.ops.mesh.primitive_cylinder_add(
        radius=5.5, depth=8,
        location=(0, 7, 5.5)
    )
    rotonda = bpy.context.active_object
    rotonda.name = "Rotonda"
    rotonda.rotation_euler = (math.pi/2, 0, 0)  # Acostado
    rotonda.scale = (1, 1, 0.5)  # Achatado
    # Cortar solo la mitad frontal
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    # Seleccionar caras traseras (Z+)
    bpy.ops.object.mode_set(mode='OBJECT')
    m = make_mat("RotondaMat", MARBLE_WHITE, roughness=0.4)
    rotonda.data.materials.append(m)

    # Cúpula/techo de la rotonda (esfera achatada)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=5.5,
        location=(0, 7, 11)
    )
    rotonda_roof = bpy.context.active_object
    rotonda_roof.name = "RotondaRoof"
    rotonda_roof.scale = (1, 1, 0.35)
    # Cortar mitad inferior
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, -1),
                        clear_inner=True, clear_outer=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    m = make_mat("RotondaRoofMat", ROOF_GRAY, roughness=0.7)
    rotonda_roof.data.materials.append(m)

    # Cornisa circular sobre la rotonda
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 7, 11),
        major_radius=5.5,
        minor_radius=0.3,
        major_segments=48,
        minor_segments=8
    )
    cornisa = bpy.context.active_object
    cornisa.name = "Cornisa"
    cornisa.scale = (1, 1, 0.4)
    m = make_mat("CornisaMat", MARBLE_WHITE, roughness=0.4)
    cornisa.data.materials.append(m)

    # REMATE de la cúpula: aguja decorativa con bola + punta
    # Base circular (plinto)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.5, depth=0.4,
        location=(0, 7, 13.2)
    )
    plinto = bpy.context.active_object
    plinto.name = "CupulaPlinto"
    mat_plinto = make_mat("PlintoMat", MARBLE_WHITE, roughness=0.3)
    plinto.data.materials.append(mat_plinto)

    # Bola decorativa
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.7, location=(0, 7, 14.0)
    )
    bola = bpy.context.active_object
    bola.name = "CupulaBola"
    mat_bola = make_mat("BolaMat", (0.95, 0.82, 0.45), roughness=0.2,
                        metallic=0.4, emissive=0.3, emit_color=(1.0, 0.9, 0.5))
    bola.data.materials.append(mat_bola)

    # Aguja/espiga final puntiaguda
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.2, radius2=0.0, depth=2.5,
        location=(0, 7, 15.5)
    )
    aguja = bpy.context.active_object
    aguja.name = "CupulaAguja"
    mat_aguja = make_mat("AgujaMat", (0.95, 0.82, 0.45), roughness=0.15,
                         metallic=0.5, emissive=0.5,
                         emit_color=(1.0, 0.95, 0.6))
    aguja.data.materials.append(mat_aguja)

    # Pequeña bola arriba de la aguja (remate final)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.15, location=(0, 7, 16.9)
    )
    remate = bpy.context.active_object
    remate.name = "CupulaRemate"
    mat_remate = make_mat("RemateMat", (0.95, 0.82, 0.45), roughness=0.1,
                          metallic=0.6, emissive=0.8,
                          emit_color=(1.0, 0.95, 0.7))
    remate.data.materials.append(mat_remate)

    # ========================================================================
    # 4 COLUMNAS CORINTIAS GIGANTES
    # ========================================================================
    column_positions = [
        (-2.5, 9.5), (2.5, 9.5), (-2.5, 4.5), (2.5, 4.5)
    ]
    for i, (x, y) in enumerate(column_positions):
        # Columna (cilindro alto)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.35, depth=8,
            location=(x, y, 4.5)
        )
        column = bpy.context.active_object
        column.name = f"Column_{i}"
        m = make_mat(f"ColumnMat_{i}", MARBLE_WHITE, roughness=0.35, metallic=0.05)
        column.data.materials.append(m)

        # Capitel (parte superior de la columna - cubo decorativo)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 8.7))
        capital = bpy.context.active_object
        capital.name = f"Capital_{i}"
        capital.scale = (0.9, 0.9, 0.4)
        m = make_mat(f"CapitalMat_{i}", MARBLE_WHITE, roughness=0.3)
        capital.data.materials.append(m)

        # Base de la columna
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.4))
        base = bpy.context.active_object
        base.name = f"ColumnBase_{i}"
        base.scale = (0.9, 0.9, 0.5)
        m = make_mat(f"ColumnBaseMat_{i}", MARBLE_WHITE, roughness=0.3)
        base.data.materials.append(m)

    # ========================================================================
    # TECHO DE LA MANSIÓN
    # ========================================================================
    # Techo principal (plano + pendiente)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 10.5))
    roof = bpy.context.active_object
    roof.name = "MainRoof"
    roof.scale = (33, 14.5, 0.6)
    m = make_mat("MainRoofMat", ROOF_GRAY, roughness=0.7)
    roof.data.materials.append(m)

    # Cornisa decorativa (banda blanca entre techo y pared)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 10))
    cornisa_main = bpy.context.active_object
    cornisa_main.name = "MainCornisa"
    cornisa_main.scale = (33.2, 14.7, 0.5)
    m = make_mat("MainCornisaMat", MARBLE_WHITE, roughness=0.3)
    cornisa_main.data.materials.append(m)

    # Cornisa inferior (entre piso 1 y piso 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 6))
    cornisa_low = bpy.context.active_object
    cornisa_low.name = "LowerCornisa"
    cornisa_low.scale = (32.2, 14.2, 0.3)
    m = make_mat("LowerCornisaMat", MARBLE_WHITE, roughness=0.3)
    cornisa_low.data.materials.append(m)

    # ========================================================================
    # VENTANAS PLANTA BAJA (ventanas altas con arcos)
    # ========================================================================
    window_positions_ground = [
        # Lado izquierdo
        (-12, 7.1), (-8, 7.1), (8, 7.1), (12, 7.1),
        # Lado derecho (espejo)
        (-12, -7.1), (-8, -7.1), (8, -7.1), (12, -7.1),
        # Frente (a los lados de la rotonda)
        (-6, 11), (6, 11),
    ]

    for i, (x, y) in enumerate(window_positions_ground):
        # Marco de ventana
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 3))
        window_frame = bpy.context.active_object
        window_frame.name = f"GroundWindowFrame_{i}"
        window_frame.scale = (2.0, 0.15, 4)
        m = make_mat(f"GroundWF_{i}", WINDOW_FRAME, roughness=0.4)
        window_frame.data.materials.append(m)

        # Cristal
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 0.15, 3))
        window_glass = bpy.context.active_object
        window_glass.name = f"GroundWindowGlass_{i}"
        window_glass.scale = (1.85, 0.05, 3.85)
        m = glass_mat(f"GroundWG_{i}", WINDOW_DARK, alpha=0.5, emissive=1.5)
        window_glass.data.materials.append(m)

        # Cortinas blancas (dentro)
        if i < 4 or i >= 6:  # Solo ventanas laterales
            for side in [-0.7, 0.7]:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x + side, y + 0.1, 3))
                curtain = bpy.context.active_object
                curtain.name = f"Curtain_{i}_{side}"
                curtain.scale = (0.3, 0.05, 3.8)
                m = make_mat(f"CurtainMat_{i}_{side}", CURTAIN_WHITE,
                          roughness=0.8)
                curtain.data.materials.append(m)

    # ========================================================================
    # VENTANAS SEGUNDO PISO + BALCONES
    # ========================================================================
    window_positions_second = [
        # Frente
        (-13, 7.1), (-9, 7.1), (-5, 7.1), (5, 7.1), (9, 7.1), (13, 7.1),
        # Atrás
        (-13, -7.1), (-9, -7.1), (9, -7.1), (13, -7.1),
    ]

    for i, (x, y) in enumerate(window_positions_second):
        # Marco
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 8.5))
        window_frame = bpy.context.active_object
        window_frame.name = f"SecondWindowFrame_{i}"
        window_frame.scale = (2.0, 0.15, 3)
        m = make_mat(f"SecondWF_{i}", WINDOW_FRAME, roughness=0.4)
        window_frame.data.materials.append(m)

        # Cristal
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 0.15, 8.5))
        window_glass = bpy.context.active_object
        window_glass.name = f"SecondWindowGlass_{i}"
        window_glass.scale = (1.85, 0.05, 2.85)
        m = glass_mat(f"SecondWG_{i}", WINDOW_DARK, alpha=0.5, emissive=1.0)
        window_glass.data.materials.append(m)

        # Balcón (solo para ventanas de los extremos)
        if abs(x) > 10:
            # Plataforma del balcón
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 0.7, 6.8))
            balcony = bpy.context.active_object
            balcony.name = f"Balcony_{i}"
            balcony.scale = (2.4, 0.8, 0.1)
            m = make_mat(f"BalconyMat_{i}", MARBLE_WHITE, roughness=0.4)
            balcony.data.materials.append(m)

            # Barandal de hierro forjado (simulado con barras)
            for bar_x in [-1.0, -0.5, 0.5, 1.0]:
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x + bar_x, y + 1.05, 7.3))
                bar = bpy.context.active_object
                bar.name = f"BalconyBar_{i}_{bar_x}"
                bar.scale = (0.04, 0.04, 0.5)
                m = make_mat(f"BarMat_{i}_{bar_x}", IRON_BLACK, roughness=0.5, metallic=0.7)
                bar.data.materials.append(m)

            # Barra superior del barandal
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y + 1.05, 7.55))
            rail = bpy.context.active_object
            rail.name = f"BalconyRail_{i}"
            rail.scale = (2.4, 0.05, 0.05)
            m = make_mat(f"RailMat_{i}", IRON_BLACK, roughness=0.5, metallic=0.7)
            rail.data.materials.append(m)

    # ========================================================================
    # BALCÓN DE LA ROTONDA (con barandal de hierro forjado)
    # ========================================================================
    # Plataforma semicircular
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3.5, depth=0.2,
        location=(0, 9, 8.8)
    )
    balcony_rotonda = bpy.context.active_object
    balcony_rotonda.name = "RotondaBalcony"
    balcony_rotonda.rotation_euler = (math.pi/2, 0, 0)
    m = make_mat("RotondaBalconyMat", MARBLE_WHITE, roughness=0.4)
    balcony_rotonda.data.materials.append(m)

    # Barandal curvo (semicírculo de barras)
    num_bars = 18
    for i in range(num_bars):
        angle = math.pi * 0.1 + i * (math.pi * 0.4 / (num_bars - 1))
        x = math.sin(angle) * 3.3
        y = 9 + math.cos(angle) * 3.3 * 0.5  # Solo mitad frontal
        z = 9.4

        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
        bar = bpy.context.active_object
        bar.name = f"RotondaBar_{i}"
        bar.scale = (0.04, 0.04, 0.6)
        m = make_mat(f"RotondaBarMat_{i}", IRON_BLACK, roughness=0.5, metallic=0.7)
        bar.data.materials.append(m)

    # Barra superior del barandal curvo
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 9, 9.7),
        major_radius=3.3,
        minor_radius=0.06,
        major_segments=48,
        minor_segments=8
    )
    rail_top = bpy.context.active_object
    rail_top.name = "RotondaRailTop"
    rail_top.rotation_euler = (math.pi/2, 0, 0)
    rail_top.scale = (1, 0.5, 1)
    m = make_mat("RotondaRailTopMat", IRON_BLACK, roughness=0.4, metallic=0.7)
    rail_top.data.materials.append(m)

    # ========================================================================
    # PUERTA PRINCIPAL DE ENTRADA (doble puerta blanca con cortinas)
    # ========================================================================
    # Marco de la puerta
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 10.5, 3))
    door_frame = bpy.context.active_object
    door_frame.name = "MainDoorFrame"
    door_frame.scale = (3, 0.2, 5)
    m = make_mat("MainDoorFrameMat", MARBLE_WHITE, roughness=0.3)
    door_frame.data.materials.append(m)

    # Cristal de la puerta (doble)
    for door_x in [-0.7, 0.7]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(door_x, 10.6, 3))
        door_glass = bpy.context.active_object
        door_glass.name = f"DoorGlass_{door_x}"
        door_glass.scale = (1.3, 0.05, 4.7)
        m = glass_mat(f"DoorGlassMat_{door_x}", WINDOW_DARK, alpha=0.4, emissive=1.5)
        door_glass.data.materials.append(m)

    # Cortinas blancas dentro
    for side in [-1.0, 1.0]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(side, 10.5, 3))
        curtain = bpy.context.active_object
        curtain.name = f"DoorCurtain_{side}"
        curtain.scale = (0.4, 0.05, 4.8)
        m = make_mat(f"DoorCurtainMat_{side}", CURTAIN_WHITE, roughness=0.8)
        curtain.data.materials.append(m)

    # Escalones de entrada
    for step_i, (step_z, step_w) in enumerate([(0.3, 1.0), (0.15, 0.8)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 11.2, step_z))
        step = bpy.context.active_object
        step.name = f"Step_{step_i}"
        step.scale = (4, step_w, 0.15)
        m = make_mat(f"StepMat_{step_i}", MARBLE_WHITE, roughness=0.4)
        step.data.materials.append(m)

    # ========================================================================
    # CHIMENEAS EN EL TECHO
    # ========================================================================
    for i, (x, y) in enumerate([(-8, -3), (-4, -5), (8, -5), (4, -3)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 12))
        chimney = bpy.context.active_object
        chimney.name = f"Chimney_{i}"
        chimney.scale = (1.2, 1.2, 3)
        m = make_mat(f"ChimneyMat_{i}", MARBLE_WHITE, roughness=0.5)
        chimney.data.materials.append(m)

        # Capuchón
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 13.7))
        cap = bpy.context.active_object
        cap.name = f"ChimneyCap_{i}"
        cap.scale = (1.4, 1.4, 0.3)
        m = make_mat(f"ChimneyCapMat_{i}", ROOF_DARK, roughness=0.6)
        cap.data.materials.append(m)


# ============================================================================
# ALBERCA
# ============================================================================
def create_pool():
    """Alberca rectangular con agua azul cristalina"""

    # ========================================================================
    # ESTRUCTURA DE LA ALBERCA
    # ========================================================================

    # Borde exterior (piedra blanca) - piso que rodea la alberca
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 18, 0.05))
    pool_deck = bpy.context.active_object
    pool_deck.name = "PoolDeck"
    pool_deck.scale = (28, 8, 0.1)
    m = make_mat("PoolDeckMat", MARBLE_WHITE, roughness=0.4)
    pool_deck.data.materials.append(m)

    # ========================================================================
    # ALBERCA (rectángulo azul con profundidad)
    # ========================================================================

    # Fondo de la alberca (azul oscuro)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 18, 0.05))
    pool_bottom = bpy.context.active_object
    pool_bottom.name = "PoolBottom"
    pool_bottom.scale = (22, 5, 0.1)
    m = make_mat("PoolBottomMat", POOL_DEEP, roughness=0.1, metallic=0.0,
              emissive=0.5, emit_color=POOL_WATER)
    pool_bottom.data.materials.append(m)

    # Paredes interiores de la alberca (azul claro - mosaico)
    # Pared izquierda
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-11, 18, 0.0))
    pool_wall_l = bpy.context.active_object
    pool_wall_l.name = "PoolWallLeft"
    pool_wall_l.scale = (0.2, 5, 1.8)
    m = make_mat("PoolWallMat", POOL_TILE, roughness=0.15, metallic=0.0)
    pool_wall_l.data.materials.append(m)

    # Pared derecha
    bpy.ops.mesh.primitive_cube_add(size=1, location=(11, 18, 0.0))
    pool_wall_r = bpy.context.active_object
    pool_wall_r.name = "PoolWallRight"
    pool_wall_r.scale = (0.2, 5, 1.8)
    pool_wall_r.data.materials.append(m)

    # Pared trasera
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 20.5, 0.0))
    pool_wall_b = bpy.context.active_object
    pool_wall_b.name = "PoolWallBack"
    pool_wall_b.scale = (22, 0.2, 1.8)
    pool_wall_b.data.materials.append(m)

    # Pared frontal (más baja, con vista al agua)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15.5, 0.0))
    pool_wall_f = bpy.context.active_object
    pool_wall_f.name = "PoolWallFront"
    pool_wall_f.scale = (22, 0.2, 1.4)
    pool_wall_f.data.materials.append(m)

    # ========================================================================
    # AGUA (superficie azul cristalina con reflejos)
    # ========================================================================
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 18, 0.5))
    water = bpy.context.active_object
    water.name = "PoolWater"
    water.scale = (22, 5, 1)
    m = make_mat("PoolWaterMat", POOL_WATER, roughness=0.05, metallic=0.0,
              emissive=1.0, emit_color=POOL_WATER)
    water.data.materials.append(m)

    # Hacerlo brillar más con un plano encima semitransparente
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 18, 0.51))
    water_shine = bpy.context.active_object
    water_shine.name = "PoolWaterShine"
    water_shine.scale = (22, 5, 1)
    m = glass_mat("PoolShineMat", (0.7, 0.85, 0.95), alpha=0.3, emissive=0.7)
    water_shine.data.materials.append(m)


# ============================================================================
# JARDÍN Y MUEBLES EXTERIORES
# ============================================================================
def create_garden():
    """Pasto, árboles, arbustos, cama balinesa, egg chair"""

    # ========================================================================
    # PASTO (césped verde)
    # ========================================================================
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 5, 0))
    grass = bpy.context.active_object
    grass.name = "Grass"
    grass.scale = (80, 60, 1)
    m = make_mat("GrassMat", GRASS_GREEN, roughness=0.85)
    grass.data.materials.append(m)

    # Pasto en los lados de la alberca
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-18, 18, 0))
    grass_left = bpy.context.active_object
    grass_left.scale = (15, 8, 1)
    m = make_mat("GrassLeftMat", GRASS_GREEN, roughness=0.85)
    grass_left.data.materials.append(m)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(18, 18, 0))
    grass_right = bpy.context.active_object
    grass_right.scale = (15, 8, 1)
    grass_right.data.materials.append(m)

    # ========================================================================
    # ÁRBOLES
    # ========================================================================
    tree_positions = [
        (-22, 0), (-24, -8), (-20, -12),
        (22, 0), (24, -8), (20, -12),
        (-25, 15), (25, 15),
        (-20, 25), (20, 25),
    ]
    for i, (x, y) in enumerate(tree_positions):
        # Tronco
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.25, depth=4,
            location=(x, y, 2)
        )
        trunk = bpy.context.active_object
        trunk.name = f"TreeTrunk_{i}"
        m = make_mat(f"TrunkMat_{i}", WOOD_BROWN, roughness=0.9)
        trunk.data.materials.append(m)

        # Follaje (múltiples esferas verdes)
        for j in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=1.5 + random.uniform(-0.3, 0.5),
                location=(x + random.uniform(-0.4, 0.4),
                          y + random.uniform(-0.4, 0.4),
                          5 + j * 1.0)
            )
            foliage = bpy.context.active_object
            foliage.name = f"Foliage_{i}_{j}"
            color = random.choice([TREE_GREEN, TREE_DARK, TREE_GREEN])
            m = make_mat(f"FoliageMat_{i}_{j}", color, roughness=0.85)
            foliage.data.materials.append(m)

    # ========================================================================
    # ARBUSTOS DECORATIVOS (alrededor de la mansión)
    # ========================================================================
    bush_positions = [
        (-16, 0), (-16, -5), (-16, 5),
        (16, 0), (16, -5), (16, 5),
        (-13, 12), (13, 12), (-13, -12), (13, -12),
    ]
    for i, (x, y) in enumerate(bush_positions):
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.8 + random.uniform(-0.2, 0.3),
            location=(x, y, 0.8)
        )
        bush = bpy.context.active_object
        bush.name = f"Bush_{i}"
        bush.scale = (1, 1, 0.7)
        m = make_mat(f"BushMat_{i}", TREE_GREEN, roughness=0.9)
        bush.data.materials.append(m)

    # ========================================================================
    # CAMA BALINESA (izquierda del jardín)
    # ========================================================================
    # Estructura de madera
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-14, 20, 0.6))
    balinese_base = bpy.context.active_object
    balinese_base.name = "BalineseBase"
    balinese_base.scale = (3.5, 2.2, 0.3)
    m = make_mat("BalineseBaseMat", WOOD_BROWN, roughness=0.7)
    balinese_base.data.materials.append(m)

    # Patas
    for px, py in [(-1.5, 1), (1.5, 1), (-1.5, -1), (1.5, -1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-14 + px, 20 + py, 0.4))
        leg = bpy.context.active_object
        leg.name = f"BalineseLeg_{px}_{py}"
        leg.scale = (0.15, 0.15, 0.8)
        m = make_mat(f"BalineseLegMat_{px}_{py}", WOOD_BROWN, roughness=0.7)
        leg.data.materials.append(m)

    # Colchón con rayas
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-14, 20, 1.0))
    mattress = bpy.context.active_object
    mattress.name = "Mattress"
    mattress.scale = (3.3, 2.0, 0.3)
    m = make_mat("MattressMat", CUSHION_STRIPE, roughness=0.7)
    mattress.data.materials.append(m)

    # Cojines
    for cx in [-0.8, 0, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-14 + cx, 21, 1.3))
        cushion = bpy.context.active_object
        cushion.name = f"Cushion_{cx}"
        cushion.scale = (0.5, 0.2, 0.4)
        m = make_mat(f"CushionMat_{cx}", (0.2, 0.2, 0.25), roughness=0.7)
        cushion.data.materials.append(m)

    # Techo de paja (palapa) - 4 postes + techo cónico
    for px in [-1.8, 1.8]:
        for py in [-1.2, 1.2]:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.08, depth=3.5,
                location=(-14 + px, 20 + py, 2.0)
            )
            pole = bpy.context.active_object
            pole.name = f"PalapaPole_{px}_{py}"
            m = make_mat(f"PalapaMat_{px}_{py}", WOOD_BROWN, roughness=0.7)
            pole.data.materials.append(m)

    # Techo de palma (cono invertido)
    bpy.ops.mesh.primitive_cone_add(
        radius1=2.5, radius2=0.5, depth=1.2,
        location=(-14, 20, 3.7)
    )
    palapa_roof = bpy.context.active_object
    palapa_roof.name = "PalapaRoof"
    m = make_mat("PalapaRoofMat", (0.45, 0.30, 0.18), roughness=0.95)
    palapa_roof.data.materials.append(m)

    # ========================================================================
    # EGG CHAIR BLANCA (derecha)
    # ========================================================================
    # Base redonda
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.2, depth=0.15,
        location=(14, 20, 0.1)
    )
    egg_base = bpy.context.active_object
    egg_base.name = "EggBase"
    m = make_mat("EggBaseMat", (0.9, 0.88, 0.85), roughness=0.4)
    egg_base.data.materials.append(m)

    # Caparazón (esfera cortada)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1.6, location=(14, 20, 1.5)
    )
    egg_shell = bpy.context.active_object
    egg_shell.name = "EggShell"
    # Cortar mitad frontal para abrirla
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    # Simplificado: solo bajar la posición
    egg_shell.scale = (1.0, 0.9, 1.4)
    m = make_mat("EggShellMat", (0.95, 0.93, 0.90), roughness=0.35)
    egg_shell.data.materials.append(m)

    # Cojín dentro
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1.0, location=(14, 19.7, 0.7)
    )
    egg_cushion = bpy.context.active_object
    egg_cushion.name = "EggCushion"
    egg_cushion.scale = (1.1, 0.9, 0.6)
    m = make_mat("EggCushionMat", CUSHION_STRIPE, roughness=0.7)
    egg_cushion.data.materials.append(m)

    # ========================================================================
    # SOMBRILLAS / DETALLES DE PISCINA
    # ========================================================================
    for i, (x, y) in enumerate([(-8, 17), (8, 17)]):
        # Asta
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.05, depth=3,
            location=(x, y, 1.5)
        )
        pole = bpy.context.active_object
        pole.name = f"UmbrellaPole_{i}"
        m = make_mat(f"UmbrellaPoleMat_{i}", WOOD_LIGHT, roughness=0.6)
        pole.data.materials.append(m)

        # Sombrilla (cono invertido)
        bpy.ops.mesh.primitive_cone_add(
            radius1=1.5, radius2=0.3, depth=0.8,
            location=(x, y, 3.0)
        )
        umbrella = bpy.context.active_object
        umbrella.name = f"Umbrella_{i}"
        m = make_mat(f"UmbrellaMat_{i}", CURTAIN_WHITE, roughness=0.6)
        umbrella.data.materials.append(m)


# ============================================================================
# ILUMINACIÓN (mediodía cálido)
# ============================================================================
def create_lighting():
    """Sol + cielo + ambiente cálido de mediodía"""

    # Sol (Directional light) - más bajo para no saturar
    bpy.ops.object.light_add(type='SUN', location=(15, -10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 1.5  # Bajado de 4.0 para evitar saturación
    sun.data.color = (1.0, 0.95, 0.85)  # Cálido
    sun.data.angle = math.radians(15)
    # Apuntar al centro
    direction = Vector((0, 0, 0)) - sun.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    sun.rotation_euler = rot_quat.to_euler()

    # Cielo hemisférico (luz suave azul)
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 25))
    sky = bpy.context.active_object
    sky.data.energy = 60  # Bajado de 200
    sky.data.color = (0.6, 0.75, 1.0)
    sky.data.size = 40

    # Luz de relleno (rellena sombras)
    bpy.ops.object.light_add(type='AREA', location=(0, 10, 8))
    fill = bpy.context.active_object
    fill.data.energy = 30  # Bajado de 100
    fill.data.color = (1.0, 0.95, 0.9)
    fill.data.size = 12

    # Luz desde abajo para iluminar la alberca
    bpy.ops.object.light_add(type='AREA', location=(0, 18, 0))
    pool_light = bpy.context.active_object
    pool_light.data.energy = 20  # Bajado de 60
    pool_light.data.color = (0.8, 0.9, 1.0)
    pool_light.data.size = 22


# ============================================================================
# CIELO AZUL CLARO
# ============================================================================
def create_sky():
    """Fondo de cielo azul claro de mediodía"""
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    bg_node = nodes.new('ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = (0.45, 0.65, 0.92, 1.0)

    # Gradient vertical (cielo más claro cerca del horizonte)
    tex = nodes.new('ShaderNodeTexGradient')
    tex.gradient_type = 'LINEAR'

    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Rotation'].default_value = (math.radians(180), 0, 0)
    coord = nodes.new('ShaderNodeTexCoord')

    color_ramp = nodes.new('ShaderNodeValToRGB')
    # Cielo arriba (azul profundo)
    color_ramp.color_ramp.elements[0].color = (0.30, 0.50, 0.85, 1.0)
    color_ramp.color_ramp.elements[0].position = 0.0
    # Medio
    color_ramp.color_ramp.elements.new(0.5)
    color_ramp.color_ramp.elements[1].color = (0.50, 0.70, 0.95, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.5
    # Horizonte (muy claro)
    color_ramp.color_ramp.elements.new(1.0)
    color_ramp.color_ramp.elements[2].color = (0.80, 0.90, 1.0, 1.0)
    color_ramp.color_ramp.elements[2].position = 1.0

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
    """Cámara frontal (como la referencia) + render"""
    # Cámara al FRENTE (y positivo grande) mirando al edificio
    bpy.ops.object.camera_add(location=(0, 30, 7))
    cam = bpy.context.active_object
    cam.name = "MainCamera"
    cam.data.lens = 28

    # Apuntar al centro de la mansión (rotonda)
    direction = Vector((0, 5, 6)) - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

    bpy.context.scene.camera = cam

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 128
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'

    return scene


# ============================================================================
# EJECUCIÓN
# ============================================================================
print("="*70)
print("ESTRUCTURA 7 — MANSIÓN NEOCLÁSICA PREMIUM")
print("="*70)

create_sky()
print("✓ Cielo azul claro")

create_mansion()
print("✓ Mansión 2 pisos + rotonda + 4 columnas + ventanas + balcones")

create_pool()
print("✓ Alberca rectangular con agua cristalina")

create_garden()
print("✓ Jardín: pasto, árboles, arbustos, palapa, egg chair, sombrillas")

create_lighting()
print("✓ Iluminación de mediodía cálido")

scene = setup_camera_and_render()
print("✓ Cámara + render configurado")

total_objs = len([o for o in bpy.data.objects if o.type == 'MESH'])
total_lights = len([o for o in bpy.data.objects if o.type == 'LIGHT'])
print(f"\n📊 {total_objs} objetos, {total_lights} luces")

# Render
output_path = '/Users/hectoraguilar/.hermes/image_cache/estructura7_mansion.png'
scene.render.filepath = output_path
print(f"\n🎬 Renderizando → {output_path}")
bpy.ops.render.render(write_still=True)
print(f"✅ Render guardado")

# Guardar .blend
blend_path = '/Users/hectoraguilar/Projects/edificio/edificios/estructura7/estructura7_mansion.blend'
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"✅ .blend guardado en {blend_path}")
