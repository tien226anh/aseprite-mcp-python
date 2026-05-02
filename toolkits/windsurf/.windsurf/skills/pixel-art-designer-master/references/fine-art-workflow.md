# Fine Art Workflow

## Design Process

Fine art pixel art prioritizes **aesthetic quality** over game-readability. Think of it as digital painting at very low resolution — portraits, landscapes, still lifes, and abstract pieces.

### 1. Concept
- Define the subject (portrait, landscape, still life, abstract)
- Choose canvas size (larger than game assets: 64×64 to 320×180)
- Pick a rich palette (16-32 colors minimum)
- Decide on animation (subtle: breathing, blinking, light shift — or none)

### 2. Canvas Setup
```python
create_canvas(width=128, height=128, filename="portrait.aseprite")
set_palette(filename="portrait.aseprite", colors=[
    # Skin tones
    "#fce4c0", "#e8b88a", "#c4885e", "#8a5a3a", "#4a2a1a",
    # Hair
    "#2a1a0a", "#4a3020", "#6a4830", "#8a6848",
    # Eyes
    "#1a1c2c", "#41a6f6", "#73eff7",
    # Clothing
    "#5d275d", "#b13e53", "#ef7d57",
    # Background
    "#1a1c2c", "#333c57", "#5a6e8a",
    # Highlights
    "#ffffff", "#ffe8c8",
])
```

### 3. Layer Architecture (Painter's Approach)

```python
# Background to foreground (painter's order)
add_layer(filename="portrait.aseprite", layer_name="background")
add_layer(filename="portrait.aseprite", layer_name="hair_back")      # hair behind head
add_layer(filename="portrait.aseprite", layer_name="neck")
add_layer(filename="portrait.aseprite", layer_name="face_base")
add_layer(filename="portrait.aseprite", layer_name="face_shade")
add_layer(filename="portrait.aseprite", layer_name="face_highlight")
add_layer(filename="portrait.aseprite", layer_name="eyes")
add_layer(filename="portrait.aseprite", layer_name="mouth")
add_layer(filename="portrait.aseprite", layer_name="hair_front")     # hair in front of face
add_layer(filename="portrait.aseprite", layer_name="clothing")
add_layer(filename="portrait.aseprite", layer_name="accessories")
```

### 4. Drawing — Iterative Detail Process

Fine art uses an **iterative refinement** approach:

**Pass 1: Block in major shapes**
```python
# Background gradient
apply_gradient_rect(
    filename="portrait.aseprite", layer_name="background", frame_index=1,
    x=0, y=0, width=128, height=128,
    color_start="#333c57", color_end="#1a1c2c",
    direction="vertical"
)

# Face base shape
draw_circle_at(
    filename="portrait.aseprite", layer_name="face_base", frame_index=1,
    center_x=64, center_y=56, radius=24,
    color="#e8b88a", fill=True
)

# Hair base
draw_polygon(
    filename="portrait.aseprite", layer_name="hair_back", frame_index=1,
    points=[...],
    color="#4a3020", fill=True
)
```

**Pass 2: Add shading**
```python
# Face shadows
draw_pixels_at(filename="portrait.aseprite", layer_name="face_shade", frame_index=1, pixels=[
    # Shadow pixels along jaw, nose, eye sockets
])
```

**Pass 3: Add highlights**
```python
# Face highlights
draw_pixels_at(filename="portrait.aseprite", layer_name="face_highlight", frame_index=1, pixels=[
    # Highlight pixels on nose bridge, cheekbones, forehead
])
```

**Pass 4: Details**
```python
# Eyes
draw_pixels_at(filename="portrait.aseprite", layer_name="eyes", frame_index=1, pixels=[
    {"x": 56, "y": 52, "color": "#ffffff"},  # eye white
    {"x": 57, "y": 52, "color": "#41a6f6"},  # iris
    {"x": 58, "y": 52, "color": "#1a1c2c"},  # pupil
    # ... more eye pixels
])
```

**Pass 5: Read back and refine**
```python
# Read back to verify
get_pixels_rect(filename="portrait.aseprite", x=48, y=44, width=32, height=24,
    layer_name="face_base", frame_index=1)

# Adjust pixels that don't look right
draw_pixels_at(filename="portrait.aseprite", layer_name="face_base", frame_index=1, pixels=[
    # Corrected pixels
])
```

### 5. Subtle Animation (Optional)

Fine art animations should be **barely perceptible**:

**Breathing:**
```python
add_frames(filename="portrait.aseprite", count=3, duration=200)
tween_cel_positions_eased(
    filename="portrait.aseprite", layer_name="clothing",
    start_frame=1, end_frame=4,
    start_x=0, start_y=0,
    end_x=0, end_y=1,
    easing="ease_in_out"
)
set_tag(filename="portrait.aseprite", name="breathe", from_frame=1, to_frame=4, direction="pingpong")
```

**Blinking:**
```python
# Hide eyes on blink frame
set_layer_opacity(filename="portrait.aseprite", layer_name="eyes", opacity=0)
# Note: this affects all frames. For per-frame control, draw closed eyes on specific frames.
```

**Light shift:**
```python
# Subtle hue shift across frames
tween_cel_opacity_eased(
    filename="portrait.aseprite", layer_name="face_highlight",
    start_frame=1, end_frame=4,
    start_opacity=200, end_opacity=255,
    easing="ease_in_out"
)
```

### 6. Export
```python
# High-quality PNG
export_sprite(filename="portrait.aseprite", output_filename="portrait.png", format="png")

# Animated GIF (if animated)
export_sprite(filename="portrait.aseprite", output_filename="portrait.gif", format="gif")
```

## Fine Art Design Tips

- **Work large, display small**: Use a larger canvas than needed, then crop
- **Many colors**: Fine art uses more colors than game assets (16-32+)
- **Hue shifting**: Essential for depth — shadows go cool, highlights go warm
- **Dithering**: Use for smooth gradients (sky, skin, metal)
- **Sub-pixel detail**: Place pixels at exact positions for subtle effects
- **Iterative refinement**: Draw → read → adjust → verify, repeat until satisfied
- **Reference images**: Study real art for color, composition, and lighting
- **Less animation**: Fine art often needs no animation, or very subtle movement
- **Layer separation**: Keep elements on separate layers for easy editing and optional animation