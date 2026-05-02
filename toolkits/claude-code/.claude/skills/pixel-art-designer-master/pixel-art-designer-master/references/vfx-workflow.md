# VFX / Effects Workflow

## Design Process

### 1. Concept
- Define the effect type (explosion, fire, magic, slash, heal, lightning, smoke)
- Choose canvas size (centered, with room for expansion)
- Pick palette (3-6 colors: core bright → outer dim)
- Decide animation length (4-12 frames typical)

### 2. Canvas Setup
```python
create_canvas(width=32, height=32, filename="explosion.aseprite")
set_palette(filename="explosion.aseprite", colors=[
    "#ffffff",  # core (white-hot)
    "#ffcc00",  # inner (yellow)
    "#ef7d57",  # mid (orange)
    "#b13e53",  # outer (red)
    "#5d275d",  # smoke (dark purple)
    "#1a1c2c",  # smoke (dark)
])
```

### 3. Layer Architecture
```python
add_layer(filename="explosion.aseprite", layer_name="flash")     # full-screen flash
add_layer(filename="explosion.aseprite", layer_name="core")      # bright center
add_layer(filename="explosion.aseprite", layer_name="glow")      # soft outer glow
add_layer(filename="explosion.aseprite", layer_name="particles") # sparks, debris
```

### 4. Drawing

**Core layer** — bright center:
```python
# Frame 1: small bright core
draw_circle_at(
    filename="explosion.aseprite", layer_name="core", frame_index=1,
    center_x=16, center_y=16, radius=2,
    color="#ffffff", fill=True
)
```

**Glow layer** — soft outer light:
```python
# Frame 1: small glow
draw_circle_at(
    filename="explosion.aseprite", layer_name="glow", frame_index=1,
    center_x=16, center_y=16, radius=4,
    color="#ffcc00", fill=True
)
```

**Particles layer** — sparks and debris:
```python
# Frame 1: initial sparks
draw_pixels_at(filename="explosion.aseprite", layer_name="particles", frame_index=1, pixels=[
    {"x": 14, "y": 14, "color": "#ffcc00"},
    {"x": 18, "y": 14, "color": "#ffcc00"},
    {"x": 14, "y": 18, "color": "#ffcc00"},
    {"x": 18, "y": 18, "color": "#ffcc00"},
])
```

### 5. Animation — Expansion + Fade

VFX typically follow an **expand then fade** pattern:

```python
add_frames(filename="explosion.aseprite", count=5, duration=60)

# Core: expand then fade
# Frame 1: small bright (already drawn)
# Frame 2-3: expanding
# Frame 4-6: fading

# Use cel position and opacity tweening
tween_cel_positions_eased(
    filename="explosion.aseprite", layer_name="core",
    start_frame=1, end_frame=3,
    start_x=14, start_y=14,
    end_x=10, end_y=10,
    easing="ease_out"
)

tween_cel_opacity_eased(
    filename="explosion.aseprite", layer_name="core",
    start_frame=3, end_frame=6,
    start_opacity=255, end_opacity=0,
    easing="ease_out"
)

# Glow: expand and fade
tween_cel_opacity_eased(
    filename="explosion.aseprite", layer_name="glow",
    start_frame=1, end_frame=6,
    start_opacity=200, end_opacity=0,
    easing="ease_out"
)

# Particles: fly outward
tween_cel_positions_eased(
    filename="explosion.aseprite", layer_name="particles",
    start_frame=1, end_frame=6,
    start_x=12, start_y=12,
    end_x=4, end_y=4,
    easing="ease_out"
)
```

### 6. Flash Effect
```python
# Full-screen flash on frame 1 only
set_layer_opacity(filename="explosion.aseprite", layer_name="flash", opacity=255)
# Then hide on subsequent frames by setting opacity to 0 on those cels
```

### 7. Tag and Export
```python
set_tag(filename="explosion.aseprite", name="explode", from_frame=1, to_frame=6, direction="forward")
export_sprite(filename="explosion.aseprite", output_filename="explosion.gif", format="gif")
```

## VFX Pattern Reference

| Effect | Core Color | Glow Color | Particle Color | Frames | Duration |
|--------|-----------|-----------|---------------|--------|----------|
| Explosion | #ffffff → #ffcc00 | #ef7d57 → #b13e53 | #ffcc00 sparks | 6-8 | 40-60ms |
| Fire | #ffffff → #ffcc00 | #ef7d57 | #5d275d smoke | 4-8 | 60-100ms |
| Magic bolt | #41a6f6 → #73eff7 | #257179 | #41a6f6 sparks | 4-6 | 50-80ms |
| Heal | #a7f070 → #38b764 | #257179 | #a7f070 sparkles | 6-8 | 80-120ms |
| Slash | #ffffff | #ef7d57 | none | 3-4 | 30-50ms |
| Lightning | #ffffff → #73eff7 | #41a6f6 | none | 2-3 | 20-40ms |
| Smoke | #5d275d | none | #3b4e6e wisps | 6-10 | 80-150ms |
| Shield | #41a6f6 | #73eff7 | #41a6f6 hexagons | 4-6 | 60-100ms |

## VFX Design Tips

- **Center the effect**: VFX sprites should be centered on the canvas
- **Transparent background**: VFX must have transparent backgrounds
- **Short and punchy**: VFX should be fast (4-8 frames, 30-80ms each)
- **Bright core, dim edges**: Always have a bright center fading outward
- **Expand then fade**: The universal VFX animation pattern
- **Flash frame**: Add a 1-frame full-brightness flash for impact
- **Particle trails**: Small dots flying outward add energy
- **Reuse and recolor**: Use `remap_colors_in_cel_range` for palette swaps (fire → ice)