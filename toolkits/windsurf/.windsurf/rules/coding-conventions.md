---
trigger: always_on
---

# Aseprite MCP Coding Conventions

## Error Handling
- New tools return error strings, never raise exceptions
- Validate inputs early, return `"Error: ..."` for invalid inputs

## Lua Script Rules
- Use `table.unpack`, NOT `unpack` (Lua 5.3+)
- Wrap mutations in `app.transaction(function() ... end)`
- Always save after mutations: `spr:saveAs("path")`
- Account for cel position offset

## Indexing
- Frame indices: **1-based**, Pixel coordinates: **0-based**

## String Escaping
- Normalize Windows backslashes: `filename.replace("\\", "/")`
- Escape all user-provided strings with `_lua_escape()`

## Path Traversal
- Reject filenames containing `..`

## Color Validation
- Two systems, don't mix: `validate_hex_color` (new) vs `parse_hex_color` (legacy)

## Layer Targeting
- Layers found by **name string**, not index. Case-sensitive.

## Drawing
- Always use `_at` variants: `draw_pixels_at`, `draw_line_at`, `draw_circle_at`, etc.
- Read back after drawing: `get_pixel_color()` / `get_pixels_rect()`

## Naming Conventions
- Filenames: `snake_case.aseprite`
- Character sprites: `{character}_{action}.aseprite`
- Layer names: PascalCase for body parts, Tags: snake_case

## Directory Organization
```
generated_assets/{project_name}/
├── hero/           # Player characters
├── monsters/       # Enemies and NPCs
├── environment/    # Tiles, backgrounds, structures
├── effects/        # VFX, spells, impacts
└── cutscene/       # Story scenes, portraits
```
