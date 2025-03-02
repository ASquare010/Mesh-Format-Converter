# Quad Mesh Conversion Tool

## Input Requirements

### Mesh-to-Mesh Conversion:
- Supported formats: `.usd`, `.usda`, `.usdc`, `.usdz`, `.fbx`, `.obj`, `.stl`, `.gltf`, `.glb`, `.ply`
- Geometry-only conversion (no texture preservation)
- Clean topology recommended for best results

### Textured Mesh Conversion:
- Supported base formats: `USD`, `FBX`, `GLB`
- Texture requirements:
  - Common image formats: `.png`, `.jpg`, `.jpeg`
  - Textures must be either:
    1. Packed inside the file (GLB)
    2. In a ZIP package with main mesh file for (`FBX`, `GLTF`)

## FBX Handling with textures
- **Input FBX**: Can be standalone or in ZIP with textures
- **Output FBX**: Always packaged as ZIP containing:
  - Main `.fbx` file
  - All associated textures
  - Texture paths relative to ZIP root
  - Automatic texture format conversion to PNG if needed

## Output Formats
| Format | Package | Texture Handling | Notes |
|--------|---------|-------------------|-------|
| FBX    | ZIP     | Embedded + PNG    | Recommended for cross-platform |
| GLTF   | ZIP     | Embedded + .BIN   | Web-friendly format |
| GLB    | Single  | Embedded          | Web-friendly format |
| USDZ   | Single  | Relative paths    | iOS/AR compatible |
| OBJ    | Single  | MTL + textures    | Legacy format support |
| STL    | Single  | None              | 3D printing optimized |