# VFX & Effects (Fireballs, Explosions, Magic)

## Canvas

```
create_canvas(width=32, height=32, filename="fireball.aseprite")
```

VFX sprites are often centered on a transparent background. Size depends on effect scale:
| Size | Use Case |
|------|----------|
| 16×16 | Small sparks, hits |
| 32×32 | Projectiles, medium effects |
| 48×48 | Explosions, large spells |
| 64×64 | Boss effects, screen-filling |

## Layer Stack

| Layer | Purpose |
|-------|---------|
| `core` | Bright center |
| `glow` | Outer glow |
| `particles` | Trailing sparks |

```
add_layer(filename="fireball.aseprite", layer_name="core")
add_layer(filename="fireball.aseprite", layer_name="glow")
add_layer(filename="fireball.aseprite", layer_name="particles")
```

## Drawing Strategy

1. **Core** — `draw_circle_at` filled, bright color:
```
draw_circle_at(filename="fireball.aseprite", layer_name="core", frame_index=1,
  center_x=16, center_y=16, radius=4, color="#ffcd75", fill=True)
```
2. **Glow** — `draw_circle_at` outline + `apply_gradient_rect`:
```
draw_circle_at(filename="fireball.aseprite", layer_name="glow", frame_index=1,
  center_x=16, center_y=16, radius=8, color="#ef7d57", fill=False)
apply_gradient_rect(
  filename="fireball.aseprite", layer_name="glow", frame_index=1,
  x=8, y=8, width=16, height=16,
  color_start="#ffcd75", color_end="#b13e53", horizontal=True
)
```
3. **Particles** — `draw_pixels_at` for scattered spark pixels

## Animation (Expansion + Fade)

```
add_frames(filename="fireball.aseprite", count=6, duration_ms=50)

# Core shrinks and fades
tween_cel_opacity_eased(
  filename="fireball.aseprite", layer_name="core",
  start_frame=1, end_frame=6,
  start_opacity=255, end_opacity=0, easing="ease_in"
)

# Glow fades out
tween_cel_opacity_eased(
  filename="fireball.aseprite", layer_name="glow",
  start_frame=1, end_frame=6,
  start_opacity=200, end_opacity=0, easing="ease_out"
)

# Particles scatter outward
oscillate_cel_positions(
  filename="fireball.aseprite", layer_name="particles",
  start_frame=1, end_frame=6, amplitude_x=3, amplitude_y=3, cycles=2.0
)

set_tag(filename="fireball.aseprite", name="explode", from_frame=1, to_frame=6, direction="forward")
```

## Common VFX Patterns

| Effect | Core Technique |
|--------|---------------|
| Explosion | Expanding circle + opacity fade |
| Fireball | Moving core + oscillating glow |
| Heal/Power-up | Oscillating position + opacity pulse |
| Slash/Swing | `draw_line_at` with varying thickness + opacity tween |
| Shield | `draw_circle_at` outline + opacity oscillation |
| Smoke | Multiple small circles + upward tween + fade |
| Lightning | `draw_path` with random offsets + flash opacity |
| Dust cloud | `draw_circle_at` small + expand + fade |
| Sparkle | `draw_pixels_at` scattered + oscillate + fade |
| Aura | `draw_circle_at` outline + `tween_cel_opacity_eased` pulse |

## VFX Animation Timing

| Effect Type | Frame Count | Duration per Frame |
|-------------|-------------|-------------------|
| Quick hit | 3-4 | 40-60ms |
| Projectile | 4-6 | 50-80ms |
| Explosion | 6-8 | 50-80ms |
| Sustained aura | 4-6 | 100-150ms |
| Smoke/dissipate | 6-10 | 80-120ms |