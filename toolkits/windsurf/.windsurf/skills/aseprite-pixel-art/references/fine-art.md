# Fine Art Pixel Pieces (Portraits, Cutscenes, Illustrations)

## Canvas

Larger format for detail work.
```
create_canvas(width=128, height=128, filename="princess_portrait.aseprite")
```

Common fine art sizes:
| Size | Use Case |
|------|----------|
| 64×64 | Small portraits, icons |
| 128×128 | Detailed portraits, cutscene close-ups |
| 256×256 | Full scenes, landscape art |
| 320×180 | Cinematic widescreen cutscene |

## Layer Stack (Painter's Approach)

| Layer | Purpose |
|-------|---------|
| `bg` | Background wash / gradient |
| `sketch` | Rough composition lines |
| `flat_color` | Color blocks for major regions |
| `volume` | Shading to create 3D form |
| `light` | Lighting, rim light, specular |
| `atmosphere` | Fog, glow, depth haze |
| `fine_detail` | Final pixel-level polish |

```
add_layer(filename="princess_portrait.aseprite", layer_name="bg")
add_layer(filename="princess_portrait.aseprite", layer_name="sketch")
add_layer(filename="princess_portrait.aseprite", layer_name="flat_color")
add_layer(filename="princess_portrait.aseprite", layer_name="volume")
add_layer(filename="princess_portrait.aseprite", layer_name="light")
add_layer(filename="princess_portrait.aseprite", layer_name="atmosphere")
add_layer(filename="princess_portrait.aseprite", layer_name="fine_detail")
```

## Drawing Strategy (Painterly Pipeline)

1. **BG** — `apply_gradient_rect` for atmospheric background:
```
apply_gradient_rect(
  filename="princess_portrait.aseprite", layer_name="bg", frame_index=1,
  x=0, y=0, width=128, height=128,
  color_start="#29366f", color_end="#5d275d", horizontal=False
)
```
2. **Sketch** — `draw_path` for composition lines:
```
draw_path(filename="princess_portrait.aseprite", layer_name="sketch", frame_index=1,
  points=[{x:64,y:20},{x:60,y:40},{x:55,y:60},{x:64,y:80}],
  color="#94b0c2", thickness=1)
```
3. **Flat color** — `fill_area_at` for major regions (skin, hair, dress)
4. **Volume** — `draw_pixels_at` for shadow gradients following form
5. **Light** — `draw_pixels_at` for rim lighting, specular highlights
6. **Atmosphere** — `set_layer_opacity` for fog/glow, `apply_gradient_rect` for depth
7. **Fine detail** — `draw_pixels_at` for eyelashes, jewelry, fabric texture

## Layer Opacity for Atmosphere

```
set_layer_opacity(filename="princess_portrait.aseprite", layer_name="atmosphere", opacity=128)
set_layer_opacity(filename="princess_portrait.aseprite", layer_name="sketch", opacity=64)
```

## Subtle Animation (Breathing, Hair Sway, Candle Flicker)

```
add_frames(filename="princess_portrait.aseprite", count=4, duration_ms=200)

# Subtle breathing motion
oscillate_cel_positions(
  filename="princess_portrait.aseprite", layer_name="flat_color",
  start_frame=1, end_frame=4, amplitude_y=1, cycles=1.0
)

# Candle flicker
tween_cel_opacity_eased(
  filename="princess_portrait.aseprite", layer_name="light",
  start_frame=1, end_frame=4,
  start_opacity=255, end_opacity=220, easing="ease_in_out"
)
```

## Fine Art Palette Strategy

- Use **24-32 colors** for detailed work
- Include **5+ values per hue** for smooth gradients (deep shadow → shadow → midtone → highlight → specular)
- Use **hue shifting**: shadows shift toward cool (blue/purple), highlights shift toward warm (yellow/orange)
- Atmospheric perspective: distant objects use desaturated, lighter colors

## Iterative Detail Process

For fine art, the iteration loop is especially important:

1. Block in major shapes on `flat_color`
2. Read back with `get_pixels_rect` to verify proportions
3. Add volume on `volume` layer
4. Read back again to check form
5. Add highlights on `light` layer
6. Read back to check lighting consistency
7. Add atmosphere and fine details
8. Final read-back of the full composition