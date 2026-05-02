---
inclusion: manual
---

# Asset Export

Export, package, and validate pixel art assets for game engines.

## Approach
1. VALIDATE: validate_scene() + get_sprite_info() before export
2. EXPORT: export_sprite(format="png"|"gif") or spritesheet_export()
3. ORGANIZE: Follow directory convention (hero/, monsters/, environment/, effects/, cutscene/)
4. VERIFY: All exports exist and are non-empty
5. PREVIEW: start_preview_server(directory="generated_assets", port=8000)

## Export Format Guide
| Asset Type | Primary | Secondary |
|-----------|---------|-----------|
| Static sprite | PNG | — |
| Animated character | PNG spritesheet | GIF |
| Tileset | PNG spritesheet | — |
| VFX | GIF | PNG spritesheet |
| Background | PNG | — |
