---
name: aseprite-pixel-art
description: 'Create detailed pixel art game assets with animation using Aseprite MCP tools. Use when: drawing characters, objects, tiles, backgrounds, VFX, or fine art pixel art; animating sprites with tweening and oscillation; compositing scenes from multiple sprites; exporting spritesheets or GIFs; iterating on pixel-level detail with read-back verification; building parallax backgrounds; creating tilesets; remapping colors for palette swaps.'
argument-hint: 'asset-type [character|object|tile|background|vfx|art] and description'
user-invocable: true
---

# Aseprite Pixel Art Creation Skill

Create detailed, animated pixel art game assets using the Aseprite MCP server tools. This skill covers the full pipeline from blank canvas to exported game-ready asset, with emphasis on **iterative layered construction** and **read-back verification**.

## When to Use

- Creating any pixel art asset (character, item, tile, background, VFX, portrait)
- Adding animation to sprites (idle, walk, attack, parallax, effects)
- Compositing multiple sprites into a scene
- Exporting spritesheets or GIFs for game engines
- Iterating on pixel-level detail with verify-and-adjust loops
- Palette swaps, color remapping, or asset variants

## Universal Principles

| Rule | Why |
|------|-----|
| **Never draw in one shot** | Break into layers → draw per layer → verify → adjust |
| **Always use `_at` variants** | `draw_pixels_at`, `draw_line_at`, etc. target specific layer+frame |
| **Read back after drawing** | `get_pixel_color` / `get_pixels_rect` to verify intent matches reality |
| **Batch pixels per call** | Send all pixels for one region in a single `draw_pixels_at` call |
| **1-based frame indices** | All frame parameters start at 1 (Aseprite Lua convention) |
| **Work bottom-up** | Background → base → shading → highlights → details |

## Core Workflow (All Asset Types)

```
1. PLAN    → animation_workflow_guide() for best practices
2. CANVAS  → create_canvas() with appropriate dimensions
3. PALETTE → set_palette() with limited colors (8-16, 3 values per hue)
4. LAYERS  → add_layer() for each structural layer
5. DRAW    → draw_pixels_at / draw_line_at / draw_circle_at / draw_polygon / fill_area_at per layer
6. VERIFY  → get_pixel_color / get_pixels_rect to read back and compare
7. ADJUST  → redraw specific pixels if verification fails
8. ANIMATE → add_frames() → copy_frame() / propagate_frame_to_range() → per-frame deltas
9. TWEEN   → tween_cel_positions_eased / oscillate_cel_positions / tween_cel_opacity_eased
10. TAG    → set_tag() for animation names
11. VALIDATE → validate_scene / audit_animation / ensure_layers_present
12. EXPORT  → export_sprite (GIF/PNG) or spritesheet_export (atlas + JSON)
13. PREVIEW → start_preview_server for browser review
14. ITERATE → if changes needed, go back to step 5
```

## The Iterative Refinement Loop

This is the **most important pattern** for detail work:

```
DRAW → READ → COMPARE → ADJUST → VERIFY → NEXT LAYER/FRAME
```

1. **DRAW**: `draw_pixels_at` with intended pixel data
2. **READ**: `get_pixels_rect` to read back what was actually drawn
3. **COMPARE**: Does the read-back match your intent?
4. **ADJUST**: If not, `draw_pixels_at` again with corrected pixels
5. **VERIFY**: Read back once more to confirm
6. **NEXT**: Move to the next layer or frame

## Asset-Specific Workflows

Each asset type has a detailed reference guide:

- **Characters**: [character-assets.md](./references/character-assets.md) — heroes, NPCs, enemies
- **Objects/Items**: [object-items.md](./references/object-items.md) — swords, potions, coins, chests
- **Tiles/Platforms**: [tiles-platforms.md](./references/tiles-platforms.md) — dungeon tiles, ground, walls
- **Backgrounds/Scenes**: [backgrounds-scenes.md](./references/backgrounds-scenes.md) — parallax, environments
- **VFX/Effects**: [vfx-effects.md](./references/vfx-effects.md) — fireballs, explosions, magic
- **Fine Art**: [fine-art.md](./references/fine-art.md) — portraits, cutscenes, illustrations
- **Animation Patterns**: [animation-patterns.md](./references/animation-patterns.md) — tweening, oscillation, tags
- **Compositing & Export**: [compositing-export.md](./references/compositing-export.md) — scene assembly, spritesheets

## Tool Selection Quick Reference

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

## Canvas Size Guide

| Size | Use Case |
|------|----------|
| 8×8 | Tiny icons, particles |
| 16×16 | Items, small enemies, UI icons |
| 32×32 | Characters, items with detail |
| 48×48 | Detailed characters |
| 64×64 | Bosses, portraits |
| 128×128 | Cutscene art, large portraits |
| 256×256+ | Full scenes, fine art |
| Wide (e.g. 480×270) | Backgrounds, parallax scenes |

## Palette Strategy

- Use **8-16 colors** for small sprites (readability)
- Use **16-32 colors** for detailed work
- Include at least **3 values per hue**: highlight, midtone, shadow
- Always include a **near-black** and **near-white**
- Set palette early with `set_palette()` before drawing