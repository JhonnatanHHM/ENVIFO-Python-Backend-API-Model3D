import bpy
import sys
import os
from pathlib import Path

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

# Validar que la imagen exista
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

# -------------------------
# Limpiar escena
# -------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------
# Crear plano con dimensiones width x height
# -------------------------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
plane = bpy.context.active_object
plane.scale.x = width / 2
plane.scale.y = height / 2

# -------------------------
# Crear material y aplicar la textura
# -------------------------
mat = bpy.data.materials.new(name="ImageMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Nodos principales
output_node = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image_node = nodes.new(type='ShaderNodeTexImage')
tex_image_node.image = bpy.data.images.load(image_path)

# Conectar nodos
links.new(bsdf_node.inputs['Base Color'], tex_image_node.outputs['Color'])
links.new(output_node.inputs['Surface'], bsdf_node.outputs['BSDF'])

# Asignar material al objeto
plane.data.materials.append(mat)

# -------------------------
# Aplicar profundidad con Solidify si depth > 0
# -------------------------
if depth > 0:
    solidify = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = depth
    bpy.ops.object.select_all(action='DESELECT')
    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    bpy.ops.object.modifier_apply(modifier=solidify.name)

# -------------------------
# Asegurar que la carpeta de salida exista
# -------------------------
Path(glb_path).parent.mkdir(parents=True, exist_ok=True)

# -------------------------
# Seleccionar objeto antes de exportar
# -------------------------
bpy.ops.object.select_all(action='DESELECT')
plane.select_set(True)
bpy.context.view_layer.objects.active = plane
bpy.context.view_layer.update()

# -------------------------
# Exportar GLB
# -------------------------
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True
)
