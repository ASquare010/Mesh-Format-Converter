# Mesh Conversion Tool

Run application

```bash
docker compose up --build
```

## Input Requirements+

### Mesh-to-Mesh Conversion:

- Supported formats: `.usd`, `.usda`, `.usdc`, `.usdz`, `.fbx`, `.obj`, `.stl`, `.gltf`, `.glb`, `.ply`
- Clean topology recommended for best results
- Tri or quad mesh supported

### Textured Mesh Conversion:

- Supported base formats: `USDZ`, `FBX`, `GLB`, `OBJ`
- Texture requirements:
  - Common image formats: `.png`, `.jpg`, `.jpeg`
  - Textures must be either:
    1. Packed inside (embedded) the file (GLB, FBX)
    2. In a ZIP package with main mesh file for (`OBJ`, `GLTF`) in the root of the ZIP for obj and for gltf, in the textures folder

## Output Formats

| Format | Package       | Texture Handling | Notes                          |
| ------ | ------------- | ---------------- | ------------------------------ |
| FBX    | ZIP or Single | Embedded + PNG   | Recommended for cross-platform |
| GLTF   | ZIP           | Embedded + .BIN  | Web-friendly format            |
| GLB    | Single        | Embedded         | Web-friendly format            |
| USDZ   | Single        | Relative paths   | iOS/AR compatible              |
| OBJ    | ZIP           | MTL + textures   | Legacy format support          |
| STL    | Single        | None             | 3D printing optimized          |
