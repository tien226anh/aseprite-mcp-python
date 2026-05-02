# Character Workflow

## Design Process

### 1. Concept
- Define the character's role (hero, enemy, NPC, boss)
- Choose silhouette shape (tall/short, thin/wide, angular/round)
- Pick a color palette (3-5 main colors + accent)
- Decide animation needs (idle, walk, attack, hurt, death)

### 2. Canvas Setup
```python
create_canvas(width=32, height=32, filename="hero.aseprite")
set_palette(filename="hero.aseprite", colors=[
    "#1a1c2c",  # outline
    "#5d275d",  # armor dark
    "#b13e53",  # armor mid
    "#ef7d57",  # armor light
    "#fac4a0",  # skin
    "#41a6f6",  # eyes
    "#38b764",  # cape
    "#257179",  # cape shadow
])
```

### 3. Layer Architecture
```python
add_layer(filename="hero.aseprite", layer_name="shadow")      # ground shadow
add_layer(filename="hero.aseprite", layer_name="outline")      # dark outline
add_layer(filename="hero.aseprite", layer_name="base_color")   # flat fills
add_layer(filename="hero.aseprite", layer_name="shading")      # shadow areas
add_layer(filename="hero.aseprite", layer_name="details")     # eyes, belt, etc.
add_layer(filename="hero.aseprite", layer_name="highlights")   # specular
```

### 4. Drawing Order

**Step 1: Outline** (on `outline` layer)
```python
# Draw the character silhouette
draw_pixels_at(filename="hero.aseprite", layer_name="outline", frame_index=1, pixels=[
    # ... outline pixels
])
```

**Step 2: Base Color** (on `base_color` layer)
```python
# Fill inside the outline
fill_area_at(filename="hero.aseprite", layer_name="base_color", frame_index=1,
    x=10, y=8, color="#b13e53")  # armor
fill_area_at(filename="hero.aseprite", layer_name="base_color", frame_index=1,
    x=10, y=14, color="#fac4a0")  # skin
```

**Step 3: Shading** (on `shading` layer)
```python
# Add shadow pixels
draw_pixels_at(filename="hero.aseprite", layer_name="shading", frame_index=1, pixels=[
    # ... shadow pixels with darker colors
])
```

**Step 4: Details** (on `details` layer)
```python
# Eyes, belt, accessories
draw_pixels_at(filename="hero.aseprite", layer_name="details", frame_index=1, pixels=[
    {"x": 13, "y": 8, "color": "#41a6f6"},  # eye
    {"x": 18, "y": 8, "color": "#41a6f6"},  # eye
])
```

**Step 5: Highlights** (on `highlights` layer)
```python
# Specular highlights
draw_pixels_at(filename="hero.aseprite", layer_name="highlights", frame_index=1, pixels=[
    # ... highlight pixels
])
```

### 5. Verify Each Layer
```python
# Read back each layer to verify
get_pixels_rect(filename="hero.aseprite", x=0, y=0, width=32, height=32,
    layer_name="outline", frame_index=1)
```

### 6. Animation

For animated characters, separate body parts into layers:
```python
# Animation-ready layers
add_layer(filename="hero.aseprite", layer_name="arm_back")
add_layer(filename="hero.aseprite", layer_name="body")
add_layer(filename="hero.aseprite", layer_name="arm_front")
add_layer(filename="hero.aseprite", layer_name="head")
```

Then animate with tweening:
```python
# Idle breathing
add_frames(filename="hero.aseprite", count=3, duration=120)
tween_cel_positions_eased(
    filename="hero.aseprite", layer_name="body",
    start_frame=1, end_frame=4,
    start_x=8, start_y=10,
    end_x=8, end_y=9,
    easing="ease_in_out"
)

# Tag the animation
set_tag(filename="hero.aseprite", name="idle", from_frame=1, to_frame=4, direction="pingpong")
```

### 7. Validate and Export
```python
validate_scene(filename="hero.aseprite",
    required_layers=["outline", "base_color", "shading", "details"])
ensure_layers_present(filename="hero.aseprite",
    layer_names=["outline", "base_color", "shading", "details"],
    start_frame=1, end_frame=4)
export_sprite(filename="hero.aseprite", output_filename="hero_idle.gif", format="gif")
```

## Character Size Reference

| Size | Best For | Detail Level |
|------|----------|-------------|
| 8×8 | Tiny enemies, projectiles | Minimal: 1-2 colors per part |
| 16×16 | Small enemies, NPCs | Basic: outline + 2 colors per part |
| 24×24 | Medium enemies | Moderate: outline + 3 colors per part |
| 32×32 | Player character, important NPCs | Full: outline + shading + details |
| 48×48 | Boss, detailed character | Rich: full layer stack + accessories |
| 64×64 | Portrait, cutscene | Maximum: full detail + expression |

## Symmetry Shortcut

For symmetric characters, draw one half and mirror:
```python
# Draw left half
draw_pixels_at(filename="hero.aseprite", layer_name="base_color", frame_index=1, pixels=[
    # left side pixels only
])

# Mirror to create right half
flip_layer(filename="hero.aseprite", layer_name="base_color", direction="horizontal")
```