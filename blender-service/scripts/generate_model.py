import bpy
import sys

# Argumentos después de "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:]

image_path = argv[0]
glb_path = argv[1]

# Leer dimensiones si se pasaron
width = float(argv[2]) if len(argv) > 2 else 2
height = float(argv[3]) if len(argv) > 3 else 2
depth = float(argv[4]) if len(argv) > 4 else 0.1

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Crear plano y escalar según width, height
bpy.ops.mesh.primitive_plane_add(size=1)  # plano de 1x1
plane = bpy.context.active_object
plane.scale.x = width / 2   # Blender escala desde el centro
plane.scale.y = height / 2

# Crear material con la imagen
mat = bpy.data.materials.new(name="ImageMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Limpiar nodos por defecto
nodes.clear()

# Nodos principales
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')
tex_image.image = bpy.data.images.load(image_path)

# Conectar nodos
links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
links.new(output.inputs['Surface'], bsdf.outputs['BSDF'])
plane.data.materials.append(mat)

# Ajustar profundidad con Solidify si depth > 0
if depth > 0:
    solidify = plane.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = depth
    bpy.ops.object.modifier_apply(modifier=solidify.name)

# Asegurar selección antes de exportar
bpy.ops.object.select_all(action='DESELECT')
plane.select_set(True)
bpy.context.view_layer.objects.active = plane

# Exportar GLB
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=True
)
