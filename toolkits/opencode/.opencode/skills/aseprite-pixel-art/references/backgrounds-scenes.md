# Backgrounds & Parallax Scenes

## Canvas

Use wide format matching game resolution.
```
create_canvas(width=480, height=270, filename="castle_bg.aseprite")
```

Common background sizes:
| Resolution | Canvas Size |
|------------|-------------|
| 240×135 (handheld) | 480×270 (2x) |
| 320×180 (indie) | 640×360 (2x) |
| 480×270 (HD) | 960×540 (2x) |

## Layer Stack (Parallax Depth Planes)

| Layer | Parallax Speed | Content |
|-------|---------------|---------|
| `sky` | Static | Gradient sky |
| `far_mountains` | 0.25x | Distant silhouettes |
| `mid_castle` | 0.5x | Main structures |
| `near_trees` | 1.0x | Foreground foliage |
| `ground` | 1.0x | Walkable surface |

```
add_layer(filename="castle_bg.aseprite", layer_name="sky")
add_layer(filename="castle_bg.aseprite", layer_name="far_mountains")
add_layer(filename="castle_bg.aseprite", layer_name="mid_castle")
add_layer(filename="castle_bg.aseprite", layer_name="near_trees")
add_layer(filename="castle_bg.aseprite", layer_name="ground")
```

## Drawing Strategy (Back to Front)

1. **Sky** — `apply_gradient_rect` for full canvas:
```
apply_gradient_rect(
  filename="castle_bg.aseprite", layer_name="sky", frame_index=1,
  x=0, y=0, width=480, height=270,
  color_start="#29366f", color_end="#41a6f6", horizontal=False
)
```
2. **Far mountains** — `draw_polygon` for silhouettes, `fill_area_at` for fills:
```
draw_polygon(filename="castle_bg.aseprite", layer_name="far_mountains", frame_index=1,
  points=[{x:0,y:180},{x:60,y:100},{x:120,y:160},{x:200,y:80},{x:280,y:150},
          {x:360,y:90},{x:480,y:170},{x:480,y:270},{x:0,y:270}],
  color="#333c57", fill=True)
```
3. **Mid castle** — `draw_rectangle_at` for towers, `draw_polygon` for roofs, `draw_pixels_at` for windows
4. **Near trees** — `draw_pixels_at` for foliage clusters, `draw_line_at` for trunks
5. **Ground** — `draw_rectangle_at` filled, `draw_pixels_at` for grass tufts

## Parallax Animation

```
add_frames(filename="castle_bg.aseprite", count=8, duration_ms=100)

# Far layer moves slowly (parallax factor ~0.25)
tween_cel_positions_eased(
  filename="castle_bg.aseprite", layer_name="far_mountains",
  start_frame=1, end_frame=8,
  start_x=0, start_y=0, end_x=-30, end_y=0,
  easing="linear", create_missing_cels=True
)

# Mid layer at medium speed (parallax factor ~0.5)
tween_cel_positions_eased(
  filename="castle_bg.aseprite", layer_name="mid_castle",
  start_frame=1, end_frame=8,
  start_x=0, start_y=0, end_x=-60, end_y=0,
  easing="linear", create_missing_cels=True
)

# Near layer moves fastest (parallax factor ~1.0)
tween_cel_positions_eased(
  filename="castle_bg.aseprite", layer_name="near_trees",
  start_frame=1, end_frame=8,
  start_x=0, start_y=0, end_x=-120, end_y=0,
  easing="linear", create_missing_cels=True
)
```

## Environmental Animation

```
# Cloud drift with oscillation
oscillate_cel_positions(
  filename="castle_bg.aseprite", layer_name="sky",
  start_frame=1, end_frame=8, amplitude_x=5, amplitude_y=1, cycles=0.5
)

# Torch flicker via opacity
tween_cel_opacity_eased(
  filename="castle_bg.aseprite", layer_name="mid_castle",
  start_frame=1, end_frame=4,
  start_opacity=255, end_opacity=200, easing="ease_in_out"
)
```

## Cross-Sprite Composition

Build individual elements as separate sprites, then compose:
```
copy_layers_between_sprites(
  source_filename="torch.aseprite",
  target_filename="castle_bg.aseprite",
  layer_names=["flame", "base"],
  create_missing_frames=True
)
```

## Audit for Overlaps

```
audit_animation(
  filename="castle_bg.aseprite",
  overlap_pairs=["far_mountains,mid_castle", "near_trees,ground"],
  layer_frame_ranges=["sky:1-8", "far_mountains:1-8", "mid_castle:1-8"],
  report_bounds=True
)
```