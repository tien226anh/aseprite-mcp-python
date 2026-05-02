# Game Objects & Items

## Canvas

Items are typically smaller: 8×8 to 24×24.
```
create_canvas(width=16, height=16, filename="health_potion.aseprite")
```

## Layer Stack

| Layer | Purpose |
|-------|---------|
| `shape` | Bottle/weapon outline |
| `fill` | Interior color, liquid |
| `shine` | Specular highlight |
| `shadow` | Drop shadow |

```
add_layer(filename="health_potion.aseprite", layer_name="shape")
add_layer(filename="health_potion.aseprite", layer_name="fill")
add_layer(filename="health_potion.aseprite", layer_name="shine")
add_layer(filename="health_potion.aseprite", layer_name="shadow")
```

## Drawing Strategy

1. **Shape** — `draw_polygon` for irregular outlines (bottles, shields):
```
draw_polygon(filename="health_potion.aseprite", layer_name="shape", frame_index=1,
  points=[{x:4,y:2},{x:6,y:2},{x:7,y:4},{x:7,y:12},{x:4,y:12},{x:3,y:4}],
  color="#1a1c2c", fill=True)
```
2. **Fill** — `fill_area_at` for interior, then `apply_gradient_rect` for liquid:
```
fill_area_at(filename="health_potion.aseprite", layer_name="fill", frame_index=1,
  x=4, y=5, color="#b13e53")
apply_gradient_rect(filename="health_potion.aseprite", layer_name="fill", frame_index=1,
  x=4, y=5, width=3, height=7,
  color_start="#b13e53", color_end="#ef7d57", horizontal=False)
```
3. **Shine** — 1-2 pixel specular line with `draw_pixels_at`
4. **Shadow** — Subtle drop shadow below the object with `draw_pixels_at`

## Common Item Shapes

| Item | Best Tool | Approach |
|------|-----------|----------|
| Potion/Bottle | `draw_polygon` | Outline vertices → fill → gradient liquid |
| Sword/Weapon | `draw_line_at` + `draw_pixels_at` | Blade line → crossguard pixels → handle |
| Shield | `draw_circle_at` | Circle outline → fill → emblem detail |
| Coin/Gem | `draw_circle_at` | Filled circle → highlight pixel |
| Chest/Box | `draw_rectangle_at` | Filled rect → line details → lock pixel |
| Key | `draw_path` | Path for shaft + circle for bow |

## Animation (Pickup Sparkle, Float, Spin)

```
add_frames(filename="health_potion.aseprite", count=6, duration_ms=80)

# Floating bob
oscillate_cel_positions(
  filename="health_potion.aseprite", layer_name="shape",
  start_frame=1, end_frame=6, amplitude_y=2, cycles=1.0
)

# Glow pulse
tween_cel_opacity_eased(
  filename="health_potion.aseprite", layer_name="shine",
  start_frame=1, end_frame=6,
  start_opacity=255, end_opacity=120, easing="ease_in_out"
)

set_tag(filename="health_potion.aseprite", name="float", from_frame=1, to_frame=6, direction="pingpong")
```

## Palette Swaps (Damage, Rarity)

```
remap_colors_in_cel_range(
  filename="health_potion.aseprite", layer_name="fill",
  start_frame=1, end_frame=6,
  mappings=[{"from": "#b13e53", "to": "#3b5dc9"}]  # red → blue (mana potion)
)
```