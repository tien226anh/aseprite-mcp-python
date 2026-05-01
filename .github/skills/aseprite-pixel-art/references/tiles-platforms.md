# Platform Tiles & Tilesets

## Canvas

Create tilesets as strips (e.g., 8 tiles of 16×16 = 128×16).
```
create_canvas(width=128, height=16, filename="dungeon_tiles.aseprite")
```

For individual tiles:
```
create_canvas(width=16, height=16, filename="stone_floor.aseprite")
```

## Layer Stack

| Layer | Purpose |
|-------|---------|
| `base` | Solid fill per tile |
| `texture` | Cracks, moss, variation |
| `edge_blend` | Soft transitions between tiles |

```
add_layer(filename="dungeon_tiles.aseprite", layer_name="base")
add_layer(filename="dungeon_tiles.aseprite", layer_name="texture")
add_layer(filename="dungeon_tiles.aseprite", layer_name="edge_blend")
```

## Drawing Strategy

1. **Base** — `draw_rectangle_at` filled for each tile block:
```
draw_rectangle_at(filename="dungeon_tiles.aseprite", layer_name="base", frame_index=1,
  x=0, y=0, width=16, height=16, color="#566c86", fill=True)
draw_rectangle_at(filename="dungeon_tiles.aseprite", layer_name="base", frame_index=1,
  x=16, y=0, width=16, height=16, color="#566c86", fill=True)
```
2. **Texture** — `draw_pixels_at` for cracks, moss, per-tile variation
3. **Edge blend** — `draw_pixels_at` for pixels that soften tile boundaries

## Seamless Tiling Verification (Critical!)

Read left/right and top/bottom edges — they must match for seamless tiling:
```
# Read left edge
get_pixels_rect(filename="dungeon_tiles.aseprite", x=0, y=0, width=1, height=16,
  layer_name="base", frame_index=1)

# Read right edge
get_pixels_rect(filename="dungeon_tiles.aseprite", x=15, y=0, width=1, height=16,
  layer_name="base", frame_index=1)

# Read top edge
get_pixels_rect(filename="dungeon_tiles.aseprite", x=0, y=0, width=16, height=1,
  layer_name="base", frame_index=1)

# Read bottom edge
get_pixels_rect(filename="dungeon_tiles.aseprite", x=0, y=15, width=16, height=1,
  layer_name="base", frame_index=1)
```
If edges don't match, adjust with `draw_pixels_at`.

## Animated Tiles (Water, Lava)

```
add_frames(filename="dungeon_tiles.aseprite", count=4, duration_ms=150)

# Draw each water frame with slight pixel shifts
draw_pixels_at(filename="dungeon_tiles.aseprite", layer_name="texture", frame_index=1, pixels=[...])
draw_pixels_at(filename="dungeon_tiles.aseprite", layer_name="texture", frame_index=2, pixels=[...])
draw_pixels_at(filename="dungeon_tiles.aseprite", layer_name="texture", frame_index=3, pixels=[...])
draw_pixels_at(filename="dungeon_tiles.aseprite", layer_name="texture", frame_index=4, pixels=[...])

set_tag(filename="dungeon_tiles.aseprite", name="water_flow", from_frame=1, to_frame=4, direction="forward")
```

## Tile Types & Techniques

| Tile Type | Approach |
|-----------|----------|
| Solid floor | `draw_rectangle_at` fill → `draw_pixels_at` texture |
| Cracked wall | `draw_rectangle_at` fill → `draw_line_at` cracks → `draw_pixels_at` moss |
| Water | `apply_gradient_rect` base → per-frame `draw_pixels_at` ripple |
| Lava | `apply_gradient_rect` hot colors → `oscillate_cel_positions` for flow |
| Grass | `draw_rectangle_at` fill → `draw_pixels_at` grass tufts on top edge |
| Platform edge | `draw_rectangle_at` fill → `draw_pixels_at` edge highlight on top row |

## Export as Spritesheet

```
spritesheet_export(filename="dungeon_tiles.aseprite", output_filename="dungeon_tiles_sheet.png")
```
This generates PNG + JSON atlas metadata for game engines.