# Background Workflow

## Design Process

### 1. Concept
- Define the scene (forest, dungeon, castle, sky, underwater)
- Choose canvas size (match game viewport or wider for parallax)
- Pick depth layers (2-5 parallax planes)
- Pick palette per layer (far = desaturated, near = saturated)
- Decide animation (cloud drift, water ripple, torch flicker)

### 2. Canvas Setup

**Static background:**
```python
create_canvas(width=320, height=180, filename="forest_bg.aseprite")
```

**Parallax background** (wider for scrolling):
```python
create_canvas(width=640, height=180, filename="forest_bg.aseprite")
```

**Palette** — use depth-based desaturation:
```python
set_palette(filename="forest_bg.aseprite", colors=[
    # Sky (far)
    "#1a1c2c", "#333c57", "#41a6f6", "#73eff7",
    # Mountains (mid-far)
    "#3b4e6e", "#5a6e8a", "#7a8ea6",
    # Trees (mid)
    "#257179", "#38b764", "#1e6e3e",
    # Foreground (near)
    "#1a1c2c", "#2e1e3e", "#5d275d", "#38b764",
])
```

### 3. Layer Architecture (Parallax)

```python
# Bottom to top (far to near)
add_layer(filename="forest_bg.aseprite", layer_name="sky")
add_layer(filename="forest_bg.aseprite", layer_name="mountains")
add_layer(filename="forest_bg.aseprite", layer_name="midground_trees")
add_layer(filename="forest_bg.aseprite", layer_name="foreground_trees")
add_layer(filename="forest_bg.aseprite", layer_name="foreground_detail")
```

### 4. Drawing

**Sky** — gradient:
```python
apply_gradient_rect(
    filename="forest_bg.aseprite", layer_name="sky", frame_index=1,
    x=0, y=0, width=640, height=180,
    color_start="#1a1c2c", color_end="#41a6f6",
    direction="vertical"
)
```

**Mountains** — silhouette shapes:
```python
# Far mountains (desaturated, low contrast)
draw_polygon(
    filename="forest_bg.aseprite", layer_name="mountains", frame_index=1,
    points=[{"x": 0, "y": 120}, {"x": 80, "y": 60}, {"x": 160, "y": 100},
            {"x": 240, "y": 50}, {"x": 320, "y": 90}, {"x": 400, "y": 55},
            {"x": 480, "y": 80}, {"x": 560, "y": 45}, {"x": 640, "y": 110},
            {"x": 640, "y": 180}, {"x": 0, "y": 180}],
    color="#3b4e6e", fill=True
)
```

**Midground trees** — tree shapes:
```python
# Tree silhouettes
draw_circle_at(
    filename="forest_bg.aseprite", layer_name="midground_trees", frame_index=1,
    center_x=50, center_y=100, radius=20,
    color="#257179", fill=True
)
# Add more trees...
```

**Foreground** — detailed elements:
```python
# Close trees with detail
draw_pixels_at(filename="forest_bg.aseprite", layer_name="foreground_detail", frame_index=1, pixels=[
    # Detailed grass, rocks, leaves
])
```

### 5. Parallax Animation

Each layer scrolls at a different speed. Use `tween_cel_positions` with linear easing:

```python
add_frames(filename="forest_bg.aseprite", count=7, duration=100)

# Sky: very slow (barely moves)
tween_cel_positions(
    filename="forest_bg.aseprite", layer_name="sky",
    start_frame=1, end_frame=8,
    start_x=0, start_y=0,
    end_x=-10, end_y=0
)

# Mountains: slow
tween_cel_positions(
    filename="forest_bg.aseprite", layer_name="mountains",
    start_frame=1, end_frame=8,
    start_x=0, start_y=0,
    end_x=-30, end_y=0
)

# Midground: medium
tween_cel_positions(
    filename="forest_bg.aseprite", layer_name="midground_trees",
    start_frame=1, end_frame=8,
    start_x=0, start_y=0,
    end_x=-60, end_y=0
)

# Foreground: fast
tween_cel_positions(
    filename="forest_bg.aseprite", layer_name="foreground_detail",
    start_frame=1, end_frame=8,
    start_x=0, start_y=0,
    end_x=-120, end_y=0
)
```

### 6. Environmental Animation

**Cloud drift:**
```python
oscillate_cel_positions(
    filename="forest_bg.aseprite", layer_name="sky",
    start_frame=1, end_frame=8,
    center_x=0, center_y=0,
    amplitude_x=5, amplitude_y=0,
    frequency=0.5
)
```

**Torch flicker** (opacity variation):
```python
tween_cel_opacity_eased(
    filename="forest_bg.aseprite", layer_name="torch_glow",
    start_frame=1, end_frame=4,
    start_opacity=200, end_opacity=255,
    easing="ease_in_out"
)
```

### 7. Cross-Sprite Composition

Combine separate sprites into a scene:
```python
# Copy a character sprite's layers into the background
copy_layers_between_sprites(
    source_filename="hero.aseprite",
    target_filename="forest_bg.aseprite",
    layer_names=["body", "arm_front", "head"]
)
```

### 8. Export

```python
# Animated GIF for preview
export_sprite(filename="forest_bg.aseprite", output_filename="forest_bg.gif", format="gif")

# PNG for game engine (static frame)
export_sprite(filename="forest_bg.aseprite", output_filename="forest_bg.png", format="png")
```

## Background Design Tips

- **Atmospheric perspective**: Far objects are lighter, bluer, less detailed
- **Layer separation**: Each depth plane should be visually distinct
- **Canvas width**: Make parallax layers wider than viewport to avoid visible edges
- **Color temperature**: Cool colors recede, warm colors advance
- **Detail gradient**: Far = simple shapes, near = detailed pixels
- **Seamless wrapping**: For looping parallax, ensure left and right edges connect