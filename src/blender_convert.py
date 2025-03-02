import uuid, zipfile, shutil, os, sys, bpy, re

CACHE_ROOT = os.environ.get("CACHE_ROOT", "/vizcom/.cache")

def pack_obj_with_textures(temp_export_dir, output_path):
    image_name_mapping = {}
    textures_dir = temp_export_dir
    
    for mat in bpy.data.materials:
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    img = node.image
                    if img.name not in image_name_mapping:
                        if img.packed_file:
                            dest_filename = img.name + ".png"
                            dest_path = os.path.join(textures_dir, dest_filename)
                            img.save_render(dest_path)
                            image_name_mapping[img.name] = dest_filename
                            img.filepath = dest_filename
                        elif img.filepath:
                            abs_path = bpy.path.abspath(img.filepath).strip()
                            if abs_path and os.path.exists(abs_path) and os.path.isfile(abs_path):
                                dest_filename = os.path.basename(abs_path)
                                dest_path = os.path.join(textures_dir, dest_filename)
                                shutil.copy2(abs_path, dest_path)
                                image_name_mapping[img.name] = dest_filename
                                img.filepath = dest_filename
                            else:
                                print(f"Warning: Texture file for {img.name} not found at '{abs_path}'")
        else:
            if hasattr(mat, "texture_slots"):
                for slot in mat.texture_slots:
                    if slot and slot.texture and slot.texture.type == 'IMAGE' and slot.texture.image:
                        img = slot.texture.image
                        if img.name not in image_name_mapping:
                            if img.packed_file:
                                dest_filename = img.name + ".png"
                                dest_path = os.path.join(textures_dir, dest_filename)
                                img.save_render(dest_path)
                                image_name_mapping[img.name] = dest_filename
                                img.filepath = dest_filename
                            elif img.filepath:
                                abs_path = bpy.path.abspath(img.filepath).strip()
                                if abs_path and os.path.exists(abs_path) and os.path.isfile(abs_path):
                                    dest_filename = os.path.basename(abs_path)
                                    dest_path = os.path.join(textures_dir, dest_filename)
                                    shutil.copy2(abs_path, dest_path)
                                    image_name_mapping[img.name] = dest_filename
                                    img.filepath = dest_filename
                                else:
                                    print(f"Warning: Texture file for {img.name} not found at '{abs_path}'")
    
    mtl_path = os.path.join(temp_export_dir, "model.mtl")
    if os.path.exists(mtl_path):
        with open(mtl_path, 'r') as f:
            mtl_contents = f.read()
        def update_map_line(match):
            prefix = match.group(1)
            tex_ref = match.group(2).strip()
            return prefix + os.path.basename(tex_ref)
        mtl_contents = re.sub(r'(map_\w+\s+)(.+)', update_map_line, mtl_contents)
        with open(mtl_path, 'w') as f:
            f.write(mtl_contents)
    
    zip_output_path = os.path.splitext(output_path)[0] + ".zip"
    base_folder = os.path.splitext(os.path.basename(zip_output_path))[0]
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_export_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, temp_export_dir)
                arcname = os.path.join(base_folder, rel_path)
                zipf.write(file_path, arcname=arcname)
    shutil.rmtree(temp_export_dir)
    return zip_output_path

def create_usdz_file(output_path, temp_dir):
    base_folder = os.path.splitext(os.path.basename(output_path))[0]
    main_usd_path = os.path.join(temp_dir, "model.usdc")
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_STORED) as usdz_zip:
        usdz_zip.write(main_usd_path, arcname=os.path.join(base_folder, "scene.usdc"))
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.normpath(file_path) == os.path.normpath(main_usd_path):
                    continue
                rel_path = os.path.relpath(file_path, temp_dir)
                arcname = os.path.join(base_folder, rel_path)
                usdz_zip.write(file_path, arcname=arcname)

argv = sys.argv
try:
    argv = argv[argv.index("--") + 1:]
except ValueError:
    argv = []

if len(argv) < 2:
    print("Usage: blender --background --python blender_convert.py -- <input_file> <output_file> [mesh_type]")
    sys.exit(1)

input_path = argv[0]
output_path = argv[1]
mesh_type = "quad"
if len(argv) >= 3:
    mesh_type = argv[2]

os.chdir(os.path.dirname(input_path))
bpy.ops.wm.read_factory_settings(use_empty=True)

ext = os.path.splitext(input_path)[1].lower()

if ext in [".usd", ".usda", ".usdc", ".usdz"]:
    result = bpy.ops.wm.usd_import(
        filepath=input_path,
        import_textures_mode='IMPORT_PACK',
        import_textures_dir='//textures/',
    )
    if result is None or "FINISHED" not in result:
        print("Error: USD import failed!")
        sys.exit(1)
elif ext == ".fbx":
    result = bpy.ops.import_scene.fbx(filepath=input_path, use_image_search=True)
    if result is None or "FINISHED" not in result:
        print("Error: FBX import failed!")
        sys.exit(1)
elif ext in [".gltf", ".glb"]:
    result = bpy.ops.import_scene.gltf(filepath=input_path, import_pack_images=True)
    if result is None or "FINISHED" not in result:
        print("Error: GLB import failed!")
        sys.exit(1)
elif ext == ".obj":
    directory = os.path.dirname(input_path) + os.sep
    result = bpy.ops.wm.obj_import(filepath=input_path, directory=directory)
    if result is None or "FINISHED" not in result:
        print("Error: OBJ import failed!")
        sys.exit(1)
elif ext == ".stl":
    result = bpy.ops.import_mesh.stl(filepath=input_path)
    if result is None or "FINISHED" not in result:
        print("Error: STL import failed!")
        sys.exit(1)
elif ext == ".ply":
    result = bpy.ops.import_mesh.ply(filepath=input_path)
    if result is None or "FINISHED" not in result:
        print("Error: PLY import failed!")
        sys.exit(1)
else:
    print("Unsupported file extension:", ext)
    sys.exit(1)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and (not obj.data or not len(obj.data.vertices)):
        bpy.data.objects.remove(obj, do_unlink=True)

imported_objs = [obj.name for obj in bpy.context.scene.objects
                 if obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}]
if not imported_objs:
    print("Warning: No objects were imported.")
    sys.exit(1)

if mesh_type.lower() == "tri":
    print("Triangulating mesh...")
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')

out_ext = os.path.splitext(output_path)[1].lower()

if out_ext == ".fbx":
    result = bpy.ops.export_scene.fbx(
        filepath=output_path,
        embed_textures=True,
        path_mode='COPY'
    )
    if not os.path.exists(output_path):
        print(f"Error: FBX export failed at {output_path}")
        sys.exit(1)
    final_output = output_path

elif out_ext == ".glb":
    result = bpy.ops.export_scene.gltf(filepath=output_path, export_format="GLB")
    final_output = output_path

elif out_ext == ".obj":
    temp_export_dir = os.path.join(CACHE_ROOT, str(uuid.uuid4()))
    os.makedirs(temp_export_dir, exist_ok=True)

    temp_obj_path = os.path.join(temp_export_dir, "model.obj")
    result = bpy.ops.wm.obj_export(
        filepath=temp_obj_path,
        export_uv=True,
        export_materials=True,
        path_mode='COPY'
    )
    if not os.path.exists(temp_obj_path):
        raise FileNotFoundError(f"OBJ export failed: file not found at {temp_obj_path}")
    
    zip_filename = pack_obj_with_textures(temp_export_dir, output_path)
    final_output = zip_filename

elif out_ext == ".stl":
    result = bpy.ops.export_mesh.stl(filepath=output_path)
    final_output = output_path

elif out_ext == ".usdz":
    temp_dir = os.path.join(CACHE_ROOT, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    temp_usd = os.path.join(temp_dir, "model.usdc")
    try:
        result = bpy.ops.wm.usd_export(
            filepath=temp_usd,
            selected_objects_only=False,
            export_animation=False,
            export_hair=False,
            export_uvmaps=True,
            export_normals=True,
            export_materials=True,
            export_textures=True,
            relative_paths=True
        )
        if 'FINISHED' not in result:
            raise Exception("USD export did not finish successfully.")
        create_usdz_file(output_path, temp_dir)
        final_output = output_path
    except Exception as e:
        print(f"USDZ export failed: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        sys.exit(1)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
else:
    print("Unsupported export file extension:", out_ext)
    sys.exit(1)

if not os.path.exists(final_output):
    error_msg = f"Error: Converted file not found at {final_output}"
    print(error_msg)
    sys.exit(1)

print("Conversion complete!")
