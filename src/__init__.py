import gradio as gr
import subprocess
import uuid
import os
import zipfile

CACHE_ROOT = os.environ.get("CACHE_ROOT", "/a_square/.cache")
os.makedirs(CACHE_ROOT, exist_ok=True)

def mesh_convert(file_obj, output_format, mesh_type):
    format_mapping = {
        "FBX": ".fbx",
        "OBJ": ".obj",
        "STL": ".stl",
        "GLB": ".glb",
        "USD": ".usdz",
    }
    extension = format_mapping.get(output_format, ".fbx")
    valid_exts = {".usd", ".usda", ".usdc", ".usdz", ".fbx", ".obj", ".stl", ".gltf", ".glb", ".ply"}

    def write_to_temp(file_obj, suffix):
        temp_path = os.path.join(CACHE_ROOT, f"{uuid.uuid4()}{suffix}")
        if hasattr(file_obj, "read"):
            content = file_obj.read()
        elif isinstance(file_obj, dict) and "data" in file_obj:
            content = file_obj["data"]
        else:
            raise ValueError("Invalid file input")
        with open(temp_path, "wb") as f:
            f.write(content)
        return temp_path

    def extract_from_zip(zip_path):
        extract_folder = os.path.join(CACHE_ROOT, f"{uuid.uuid4()}")
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        for root, _, files in os.walk(extract_folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in valid_exts:
                    return os.path.join(root, file)
        return None

    if isinstance(file_obj, str):
        orig_name = file_obj
    elif hasattr(file_obj, "name") and file_obj.name:
        orig_name = file_obj.name
    elif isinstance(file_obj, dict) and "name" in file_obj:
        orig_name = file_obj["name"]
    else:
        orig_name = ""

    if orig_name.lower().endswith(".zip"):
        zip_path = file_obj if isinstance(file_obj, str) else write_to_temp(file_obj, ".zip")
        temp_input = extract_from_zip(zip_path)
        if not temp_input:
            return "Error: No valid 3D file found in ZIP."
        print("Found 3D file in ZIP:", temp_input)
    else:
        if isinstance(file_obj, str):
            temp_input = file_obj
        else:
            suffix = os.path.splitext(orig_name)[1] if orig_name else ".obj"
            temp_input = write_to_temp(file_obj, suffix)

    temp_output = os.path.join(CACHE_ROOT, f"{uuid.uuid4()}{extension}")

    mesh_arg = "tri" if mesh_type == "Tri Mesh" else "quad"
    command = [
        "xvfb-run",
        "--auto-servernum",
        "blender",
        "--background",
        "--python",
        "/a_square/app/src/blender_convert.py",
        "--",
        temp_input,
        temp_output,
        mesh_arg
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return f"Conversion failed: {e}"

    if temp_output.endswith(".obj"):
        temp_output = os.path.splitext(temp_output)[0] + ".zip"
    if not os.path.exists(temp_output):
        return f"Error: Converted file not found at {temp_output}"
    return temp_output

iface = gr.Interface(
    fn=mesh_convert,
    inputs=[
        gr.File(label="Upload 3D Mesh File (ZIP allowed)"),
        gr.Dropdown(
            label="Select Output Format",
            choices=["FBX", "OBJ", "STL", "GLB", "USD"],
            value="FBX"
        ),
        gr.Dropdown(
            label="Mesh Type",
            choices=["Quad Mesh", "Tri Mesh"],
            value="Quad Mesh"
        )
    ],
    outputs=gr.File(label="Download Converted File"),
    title="Mesh Converter",
    description="Upload a 3D mesh file or a ZIP (containing a 3D file and its resources) and convert it to your desired format using Blender in headless mode.",
)

if __name__ == "__main__":
    iface.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        allowed_paths=[CACHE_ROOT]
    )
