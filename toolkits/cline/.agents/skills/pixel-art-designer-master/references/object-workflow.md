# Object / Item Workflow

## Design Process

### 1. Concept
- Define the item type (weapon, potion, key, gem, food, scroll)
- Choose a distinctive silhouette (readable at small sizes)
- Pick 3-6 colors (item color, highlight, shadow, outline)
- Decide animation (float, spin, pulse, none)

### 2. Canvas Setup
```python
create_canvas(width=16, height=16, filename="potion.aseprite")
set_palette(filename="potion.aseprite", colors=[
    "#1a1c2c",  # outline
    "#b13e53",  # liquid
    "#ef7d57",  # liquid highlight
    "#5d275d",  # liquid shadow
    "#41a6f6",  # glass
    "#94b0c2",  # glass highlight
    "#257179",  # cork
])
```

### 3. Layer Architecture
```python
add_layer(filename="potion.aseprite", layer_name="outline")
add_layer(filename="potion.aseprite", layer_name="base_color")
add_layer(filename="potion.aseprite", layer_name="shading")
add_layer(filename="potion.aseprite", layer_name="shine")
```

### 4. Drawing

**Common item shapes:**

| Item | Shape | Tool |
|------|-------|------|
| Potion | Bottle (rectangle + circle top) | `draw_rectangle_at` + `draw_circle_at` |
| Sword | Long thin rectangle + crossguard | `draw_rectangle_at` + `draw_line_at` |
| Shield | Circle or rounded rectangle | `draw_circle_at` or `draw_rectangle_at` |
| Gem | Diamond (rotated square) | `draw_polygon` |
| Key | Thin rectangle + circle | `draw_rectangle_at` + `draw_circle_at` |
| Scroll | Rounded rectangle | `draw_rectangle_at` |
| Coin | Circle | `draw_circle_at` |
| Heart | Two circles + triangle | `draw_circle_at` + `draw_polygon` |

**Example: Potion**
```python
# Outline
draw_pixels_at(filename="potion.aseprite", layer_name="outline", frame_index=1, pixels=[
    # Bottle outline pixels
])

# Base color fill
fill_area_at(filename="potion.aseprite", layer_name="base_color", frame_index=1,
    x=6, y=5, color="#b13e53")  # red liquid

# Shading
draw_pixels_at(filename="potion.aseprite", layer_name="shading", frame_index=1, pixels=[
    {"x": 5, "y": 8, "color": "#5d275d"},  # shadow on left
])

# Shine (specular highlight)
draw_pixels_at(filename="potion.aseprite", layer_name="shine", frame_index=1, pixels=[
    {"x": 7, "y": 6, "color": "#ffffff"},  # bright highlight
])
```

### 5. Animation

**Float animation** (gentle up-down):
```python
add_frames(filename="potion.aseprite", count=3, duration=120)
oscillate_cel_positions(
    filename="potion.aseprite", layer_name="base_color",
    start_frame=1, end_frame=4,
    center_x=4, center_y=4,
    amplitude_x=0, amplitude_y=1,
    frequency=1.0
)
set_tag(filename="potion.aseprite", name="float", from_frame=1, to_frame=4, direction="pingpong")
```

**Spin animation** (rotate through angles):
```python
# Draw 4 rotation frames manually, or use rotate_layer for 90° increments
```

**Pulse animation** (scale/brightness):
```python
# Use opacity tweening for glow pulse
tween_cel_opacity_eased(
    filename="potion.aseprite", layer_name="shine",
    start_frame=1, end_frame=4,
    start_opacity=128, end_opacity=255,
    easing="ease_in_out"
)
```

### 6. Palette Swaps

Create color variants without redrawing:
```python
# Create a copy
copy_sprite(filename="potion.aseprite", output_filename="potion_blue.aseprite")

# Remap colors
remap_colors_in_cel_range(
    filename="potion_blue.aseprite",
    source_colors=["#b13e53", "#ef7d57", "#5d275d"],  # red
    target_colors=["#41a6f6", "#73eff7", "#257179"],    # blue
    layer_name="base_color",
    start_frame=1, end_frame=4
)
```

### 7. Export
```python
export_sprite(filename="potion.aseprite", output_filename="potion.png", format="png")
```

## Item Design Tips

- **Readability**: Items must be recognizable at 1x scale in-game
- **Distinct silhouette**: Each item type should have a unique shape
- **Color coding**: Use color to indicate item type (red = health, blue = mana, green = poison)
- **Size consistency**: All items in the same game should use the same canvas size
- **Animation subtlety**: Items need gentle animation — too much is distracting