import bpy
import sys
from pathlib import Path
import os
import traceback

def log(msg):
    print(f"[generate_model.py] {msg}")

try:
    # -------------------------
    # Argumentos desde Python API
    # -------------------------
    argv_index = sys.argv.index("--")
    argv = sys.argv[argv_index + 1:]

    image_path = argv[0]
    width = float(argv[1])
    height = float(argv[2])
    depth = float(argv[3])
    glb_path = argv[4]

    log(f"Argumentos recibidos: image_path={image_path}, width={width}, height={height}, depth={depth}, glb_path={glb_path}")

    # Validar que la imagen exista
    if not os.path.exists(image_path):
        log(f"ERROR: Imagen no encontrada: {image_path}")
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
    log("Imagen encontrada correctamente.")

    # -------------------------
    # Limpiar escena
    # -------------------------
    bpy.ops.wm.read_factory_settings(use_empty=True)
    log("Escena limpiada.")

    # -------------------------
    # Crear plano y escalar según width y height
    # -------------------------
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.scale.x = width / 2
    plane.scale.y = height / 2
    log("Plano creado y escalado.")

    # -------------------------
    # Aplicar profundidad con Solidify si depth > 0
    # -------------------------
    if depth > 0:
        solidify = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = depth
        bpy.ops.object.modifier_apply(modifier=solidify.name)
        log(f"Solidify aplicado con thickness={depth}.")
    else:
        log("Sin profundidad (depth <= 0).")

    # -------------------------
    # Crear material simple para headless
    # -------------------------
    mat = bpy.data.materials.new(name="ImageMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Limpiar nodos existentes
    for node in nodes:
        nodes.remove(node)
    log("Nodos del material limpiados.")

    # Crear nodos básicos
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    emission_node = nodes.new(type='ShaderNodeEmission')
    tex_image_node = nodes.new(type='ShaderNodeTexImage')
    try:
        tex_image_node.image = bpy.data.images.load(image_path)
        log("Imagen cargada en nodo de textura.")
    except Exception as e:
        log(f"ERROR al cargar la imagen en el nodo de textura: {e}")
        raise

    # Conectar nodos: textura → emisión → salida
    links.new(emission_node.inputs['Color'], tex_image_node.outputs['Color'])
    links.new(output_node.inputs['Surface'], emission_node.outputs['Emission'])
    log("Nodos conectados.")

    # Asignar material al objeto
    plane.data.materials.append(mat)
    log("Material asignado al plano.")

    # -------------------------
    # Seleccionar objeto antes de exportar
    # -------------------------
    bpy.ops.object.select_all(action='DESELECT')
    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    log("Plano seleccionado para exportación.")

    # -------------------------
    # Asegurar que la carpeta de salida exista
    # -------------------------
    Path(glb_path).parent.mkdir(parents=True, exist_ok=True)
    log(f"Directorio de salida verificado: {Path(glb_path).parent}")

    # -------------------------
    # Exportar GLB
    # -------------------------
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        use_selection=True
    )
    log(f"Exportación exitosa: {glb_path}")

except Exception as e:
    log("¡ERROR durante la generación del modelo!")
    log(traceback.format_exc())
    sys.exit(1)