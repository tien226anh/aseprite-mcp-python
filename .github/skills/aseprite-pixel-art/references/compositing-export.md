# Compositing & Export

## Cross-Sprite Composition

Build a complete scene from individual assets:
```
copy_layers_between_sprites(
  source_filename="castle_bg.aseprite",
  target_filename="level_01.aseprite",
  layer_names=["sky", "far_mountains", "mid_castle", "near_trees", "ground"],
  create_missing_frames=True
)

copy_layers_between_sprites(
  source_filename="hero.aseprite",
  target_filename="level_01.aseprite",
  layer_names=["outline", "base_colors", "shading", "highlights", "details"],
  create_missing_frames=True
)

copy_layers_between_sprites(
  source_filename="torch.aseprite",
  target_filename="level_01.aseprite",
  layer_names=["flame", "base"],
  create_missing_frames=True
)
```

## Positioning Elements

```
set_cel_position(filename="level_01.aseprite", layer_name="outline",
  frame_index=1, x=200, y=180, create_if_missing=True)

set_cel_position(filename="level_01.aseprite", layer_name="flame",
  frame_index=1, x=100, y=120, create_if_missing=True)
```

## Scene Validation

### Ensure all layers have cels across frames
```
ensure_layers_present(
  filename="level_01.aseprite",
  layer_names=["sky", "far_mountains", "mid_castle", "near_trees", "ground",
               "outline", "base_colors", "shading", "highlights", "details"],
  start_frame=1, end_frame=8
)
```

### Validate required layers exist
```
validate_scene(filename="level_01.aseprite",
  required_layers=["sky", "far_mountains", "mid_castle", "near_trees", "ground",
                   "outline", "base_colors", "shading", "highlights", "details"])
```

### Audit for overlaps and out-of-range activity
```
audit_animation(filename="level_01.aseprite",
  overlap_pairs=["outline,ground", "flame,mid_castle"],
  layer_frame_ranges=["sky:1-8", "outline:1-8", "flame:1-8"],
  report_bounds=True
)
```

## Export Options

### Quick GIF preview
```
export_sprite(filename="hero.aseprite", output_filename="hero_idle.gif", format="gif")
```

### Game engine spritesheet with atlas
```
spritesheet_export(filename="hero.aseprite", output_filename="hero_sheet.png")
```
Generates PNG + JSON with frame coordinates for game engines.

### PNG for tilesets
```
export_sprite(filename="dungeon_tiles.aseprite", output_filename="dungeon_tiles.png", format="png")
```

### Copy as new .aseprite (preserve source)
```
copy_sprite(filename="hero.aseprite", output_filename="hero_backup.aseprite")
```

### Supported export formats
`png`, `gif`, `jpg`, `jpeg`, `bmp`, `webp`, `aseprite`, `ase`

## Browser Preview

```
start_preview_server(directory="generated_assets", port=8000)
# Open http://localhost:8000/hero_idle.gif

# When done:
stop_preview_server(port=8000)
```

## Transform Operations

| Operation | Tool |
|-----------|------|
| Flip horizontal | `flip_layer(filename, layer_name, frame_index, "horizontal")` |
| Flip vertical | `flip_layer(filename, layer_name, frame_index, "vertical")` |
| Rotate 90°/180°/270° | `rotate_layer(filename, layer_name, frame_index, angle)` |
| Resize (scales content) | `resize_canvas(filename, width, height)` |
| Crop to region | `crop_canvas(filename, x, y, width, height)` |

## Color Remapping

Swap colors across a range of cels (useful for palette swaps, damage flash, rarity variants):
```
remap_colors_in_cel_range(
  filename="hero.aseprite", layer_name="base_colors",
  start_frame=1, end_frame=4,
  mappings=[{"from": "#3b5dc9", "to": "#b13e53"}]  # blue armor → red armor
)
```

## Palette Management

### Get current palette
```
get_palette(filename="hero.aseprite")
```

### Set new palette
```
set_palette(filename="hero.aseprite", colors=[
  "#1a1c2c", "#5d275d", "#b13e53", "#ef7d57", "#ffcd75",
  "#a7f070", "#38b764", "#257179", "#29366f", "#3b5dc9",
  "#41a6f6", "#73eff7", "#f4f4f4", "#94b0c2", "#566c86", "#333c57"
])
```

## Pixel Reading (for verification)

### Read a single pixel
```
get_pixel_color(filename="hero.aseprite", x=15, y=8,
  layer_name="details", frame_index=1)
```

### Read a rectangular region
```
get_pixels_rect(filename="hero.aseprite", x=14, y=7, width=4, height=4,
  layer_name="details", frame_index=1)
```

### Get full sprite info
```
get_sprite_info(filename="hero.aseprite")
```