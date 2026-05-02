# Character Asset Creation

## Canvas & Palette

```
create_canvas(width=32, height=32, filename="hero.aseprite")
set_palette(filename="hero.aseprite", colors=[
  "#1a1c2c", "#5d275d", "#b13e53", "#ef7d57", "#ffcd75",
  "#a7f070", "#38b764", "#257179", "#29366f", "#3b5dc9",
  "#41a6f6", "#73eff7", "#f4f4f4", "#94b0c2", "#566c86", "#333c57"
])
```

## Layer Stack (bottom to top)

| Layer | Purpose | Drawing Tools |
|-------|---------|---------------|
| `base_colors` | Flat color fills | `fill_area_at`, `draw_pixels_at` |
| `shading` | Shadow volumes | `draw_pixels_at` |
| `highlights` | Specular, rim light | `draw_pixels_at` |
| `outline` | Edge definition | `draw_pixels_at`, `draw_line_at` |
| `details` | Eyes, emblems, fine detail | `draw_pixels_at` |

```
add_layer(filename="hero.aseprite", layer_name="base_colors")
add_layer(filename="hero.aseprite", layer_name="shading")
add_layer(filename="hero.aseprite", layer_name="highlights")
add_layer(filename="hero.aseprite", layer_name="outline")
add_layer(filename="hero.aseprite", layer_name="details")
```

## Drawing Order

1. **Outline** — silhouette edges with `draw_pixels_at` and `draw_line_at`
2. **Base colors** — `fill_area_at` for large regions, `draw_pixels_at` for borders between color zones
3. **Shading** — `draw_pixels_at` for shadow pixels (consistent light source!)
4. **Highlights** — `draw_pixels_at` for specular hits (armor glint, hair shine)
5. **Details** — `draw_pixels_at` for eyes, belt buckle, emblem

## Symmetry Shortcut

Draw the left half, then:
```
flip_layer(filename="hero.aseprite", layer_name="outline", frame_index=1, direction="horizontal")
```
Read back center column with `get_pixels_rect`, then clean up the center line with `draw_pixels_at`.

## Animation

```
# Add frames
add_frames(filename="hero.aseprite", count=4, duration_ms=120)

# Copy base pose to all frames first
propagate_frame_to_range(filename="hero.aseprite", source_frame=1, start_frame=2, end_frame=4)

# Then modify each frame with small deltas
draw_pixels_at(filename="hero.aseprite", layer_name="outline", frame_index=2, pixels=[...])
draw_pixels_at(filename="hero.aseprite", layer_name="base_colors", frame_index=2, pixels=[...])

# Tween for smooth motion (e.g., bobbing)
tween_cel_positions_eased(
  filename="hero.aseprite", layer_name="details",
  start_frame=1, end_frame=4,
  start_x=0, start_y=0, end_x=0, end_y=-2,
  easing="smoothstep", create_missing_cels=True
)

# Tag the animation
set_tag(filename="hero.aseprite", name="idle", from_frame=1, to_frame=4, direction="pingpong")
```

## Common Character Animations

| Animation | Frames | Duration | Technique |
|-----------|--------|----------|-----------|
| Idle | 4 | 120ms | Oscillate Y ±1-2px, pingpong |
| Walk | 6-8 | 80-100ms | Keyframe legs, tween arms |
| Attack | 4-6 | 60-80ms | Tween weapon position ease_out |
| Hurt | 2-3 | 100ms | Flash opacity, offset position |
| Death | 4-6 | 150ms | Fade opacity, fall tween |

## Verification

```
get_sprite_info(filename="hero.aseprite")
validate_scene(filename="hero.aseprite",
  required_layers=["outline", "base_colors", "shading", "highlights", "details"])
```