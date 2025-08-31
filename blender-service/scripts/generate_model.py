import bpy
import sys
from pathlib import Path

# Argumentos después de "--"
argv = sys.argv
argv = argv.index("--")
argv = sys.argv[argv + 1:]

# Rutas y dimensiones según app.py
image_path = argv[0]
width = float(argv[1])
height = float(argv[2])
depth = float(argv[3])
glb_path = argv[4]

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Crear plano y escalar según width, height
bpy.ops.mesh.primitive_plane_add(size=1)
plane = bpy.context.active_object
plane.scale.x = width / 2
plane.scale.y = height / 2

# Crear material con la imagen
mat = bpy.data.materials.new(name="ImageMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')
tex_image.image = bpy.data.images.load(image_path)

links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])
plane.data.materials.append(mat)

# Ajustar profundidad con Solidify
if depth > 0:
    solidify = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = depth
    bpy.ops.object.modifier_apply(modifier=solidify.name)

# Seleccionar objeto antes de exportar
bpy.ops.object.select_all(action='DESELECT')
plane.select_set(True)
bpy.context.view_layer.objects.active = plane

# Asegurar que el directorio de salida exista
glb_dir = Path(glb_path).parent
glb_dir.mkdir(parents=True, exist_ok=True)

# Exportar GLB
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True
)
