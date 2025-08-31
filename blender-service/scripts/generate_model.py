import bpy
import sys
from pathlib import Path

# Argumentos después de "--"
argv_index = sys.argv.index("--")
argv = sys.argv[argv_index + 1:]

image_path = argv[0]
width = float(argv[1])
height = float(argv[2])
depth = float(argv[3])
glb_path = argv[4]

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Crear cubo sólido escalado según width, height, depth
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,depth/2))
obj = bpy.context.active_object
obj.scale.x = width / 2
obj.scale.y = height / 2
obj.scale.z = depth / 2

# Crear material con la imagen
mat = bpy.data.materials.new(name="ImageMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output_node = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image_node = nodes.new(type='ShaderNodeTexImage')
tex_image_node.image = bpy.data.images.load(image_path)

links.new(bsdf_node.inputs['Base Color'], tex_image_node.outputs['Color'])
links.new(output_node.inputs['Surface'], bsdf_node.outputs['BSDF'])
obj.data.materials.append(mat)

# Seleccionar el objeto antes de exportar
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Asegurar que el directorio de salida exista
glb_dir = Path(glb_path).parent
glb_dir.mkdir(parents=True, exist_ok=True)

# Exportar GLB
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True
)
