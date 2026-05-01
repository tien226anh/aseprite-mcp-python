---
name: pixel-art-designer-master
description: 'Design and create detailed pixel art game assets from concept to export using Aseprite MCP tools. Use when: designing a new game asset from scratch with full creative control; planning asset dimensions, palette, and layer architecture before drawing; creating character sprites with animation; building tilesets with seamless tiling; composing parallax backgrounds; crafting VFX effects; making fine art pixel illustrations; iterating on pixel-level detail with read-back verification; exporting game-ready spritesheets. This is the master design skill that covers the full creative pipeline.'
argument-hint: 'asset description, e.g. "32x32 knight with idle animation" or "parallax forest background"'
user-invocable: true
---

# Pixel Art Designer Master

Design and create detailed pixel art game assets from concept to final export. This skill covers the **full creative pipeline** — from planning dimensions and palette through layered construction, animation, validation, and game-ready export.

## When to Use

- Designing a new game asset from scratch (not just executing known steps)
- Planning asset architecture before drawing (dimensions, palette, layers)
- Creating any pixel art with full creative control
- Iterating on designs with read-back verification
- Building animated sprites, tilesets, backgrounds, VFX, or fine art
- Exporting game-ready assets

## Design Pipeline

```
CONCEPT → PLAN → CONSTRUCT → VERIFY → ANIMATE → VALIDATE → EXPORT → REVIEW
```

### 1. CONCEPT — Define the Asset

Before touching any tools, decide:
- **What** is this asset? (character, item, tile, background, VFX, portrait)
- **What size?** See [canvas-sizes.md](./references/canvas-sizes.md)
- **What palette?** Limited (8-16 colors) or detailed (16-32)?
- **What animation?** Idle, walk, attack, float, parallax, none?
- **What style?** Read [design-principles.md](./references/design-principles.md)

### 2. PLAN — Set Up the Canvas

```
create_canvas(width=32, height=32, filename="hero.aseprite")
set_palette(filename="hero.aseprite", colors=[...])
```

Choose layers based on asset type. See [layer-architecture.md](./references/layer-architecture.md).

### 3. CONSTRUCT — Draw Layer by Layer

**Always use `_at` variants** (`draw_pixels_at`, `draw_line_at`, etc.) to target specific layer+frame.

Work bottom-up: background → base → shading → highlights → details.

After each layer, **read back** to verify:
```
get_pixels_rect(filename="hero.aseprite", x=0, y=0, width=32, height=32,
  layer_name="outline", frame_index=1)
```

See the full drawing reference in [drawing-reference.md](./references/drawing-reference.md).

### 4. VERIFY — Read Back and Compare

The **iterative refinement loop** is the core of quality pixel art:

```
DRAW → READ → COMPARE → ADJUST → VERIFY → NEXT
```

1. `draw_pixels_at` with intended pixels
2. `get_pixels_rect` to read back what was drawn
3. Compare against intent — does it match?
4. If not, `draw_pixels_at` with corrections
5. Read back again to confirm

### 5. ANIMATE — Add Motion

See [animation-reference.md](./references/animation-reference.md) for all animation patterns.

### 6. VALIDATE — Check Structure

```
validate_scene(filename="hero.aseprite", required_layers=[...])
ensure_layers_present(filename="hero.aseprite", layer_names=[...], start_frame=1, end_frame=4)
audit_animation(filename="hero.aseprite", ...)
```

### 7. EXPORT — Game-Ready Output

```
export_sprite(filename="hero.aseprite", output_filename="hero_idle.gif", format="gif")
spritesheet_export(filename="hero.aseprite", output_filename="hero_sheet.png")
```

### 8. REVIEW — Preview and Iterate

```
start_preview_server(directory="generated_assets", port=8000)
```

If changes needed, go back to step 3.

## Asset Type Quick Links

| Asset Type | Reference |
|-----------|-----------|
| Characters | [character-workflow.md](./references/character-workflow.md) |
| Objects/Items | [object-workflow.md](./references/object-workflow.md) |
| Tiles/Platforms | [tile-workflow.md](./references/tile-workflow.md) |
| Backgrounds | [background-workflow.md](./references/background-workflow.md) |
| VFX/Effects | [vfx-workflow.md](./references/vfx-workflow.md) |
| Fine Art | [fine-art-workflow.md](./references/fine-art-workflow.md) |

## Tool Selection Matrix

| Task | Best Tool(s) |
|------|-------------|
| Large flat area | `fill_area_at`, `draw_rectangle_at` (fill=True) |
| Sky / atmosphere | `apply_gradient_rect` |
| Character outline | `draw_pixels_at` + `draw_line_at` |
| Rounded shapes | `draw_circle_at`, `draw_polygon` |
| Irregular shapes | `draw_polygon` (fill=True) |
| Curves / paths | `draw_path` |
| Single-pixel details | `draw_pixels_at` |
| Symmetry | Draw half → `flip_layer` |
| Repetitive frames | `copy_frame` → `draw_pixels_at` for deltas |
| Smooth motion | `tween_cel_positions_eased` |
| Oscillating motion | `oscillate_cel_positions` |
| Fade in/out | `tween_cel_opacity_eased` |
| Parallax scroll | `tween_cel_positions` (linear) per depth layer |
| Compositing assets | `copy_layers_between_sprites` |
| Positioning elements | `set_cel_position` |
| Verify pixels | `get_pixel_color`, `get_pixels_rect` |
| Verify structure | `validate_scene`, `audit_animation` |
| Fix missing cels | `ensure_layers_present` |
| Color swaps | `remap_colors_in_cel_range` |
| Resize / Crop | `resize_canvas`, `crop_canvas` |
| Rotate / Flip | `rotate_layer`, `flip_layer` |