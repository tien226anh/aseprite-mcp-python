# Drawing Reference

## Drawing Order

**Always draw bottom-up** within a layer stack:
1. Outline first (defines the shape)
2. Base color fill (flood fill inside outline)
3. Shading (add depth)
4. Details (small features)
5. Highlights (specular, rim light)

## Tool Selection by Task

### Single Pixels
Use `draw_pixels_at` for precise 1-pixel placement:
```python
draw_pixels_at(
    filename="hero.aseprite",
    layer_name="outline",
    frame_index=1,
    pixels=[{"x": 5, "y": 3, "color": "#1a1c2c"}]
)
```

### Lines
Use `draw_line_at` for straight edges:
```python
draw_line_at(
    filename="hero.aseprite",
    layer_name="outline",
    frame_index=1,
    x1=5, y1=3, x2=15, y2=3,
    color="#1a1c2c", thickness=1
)
```

### Rectangles
Use `draw_rectangle_at` for boxes, borders, UI elements:
```python
# Filled rectangle (base color fill)
draw_rectangle_at(
    filename="hero.aseprite",
    layer_name="base_color",
    frame_index=1,
    x=6, y=4, width=9, height=12,
    color="#5d275d", fill=True
)

# Outline rectangle (border only)
draw_rectangle_at(
    filename="hero.aseprite",
    layer_name="outline",
    frame_index=1,
    x=5, y=3, width=11, height=14,
    color="#1a1c2c", fill=False
)
```

### Circles
Use `draw_circle_at` for round shapes:
```python
# Filled circle (head, shield)
draw_circle_at(
    filename="hero.aseprite",
    layer_name="base_color",
    frame_index=1,
    center_x=10, center_y=6, radius=4,
    color="#fac4a0", fill=True
)

# Circle outline (ring, wheel)
draw_circle_at(
    filename="hero.aseprite",
    layer_name="outline",
    frame_index=1,
    center_x=10, center_y=6, radius=4,
    color="#1a1c2c", fill=False
)
```

### Polygons
Use `draw_polygon` for irregular shapes:
```python
draw_polygon(
    filename="hero.aseprite",
    layer_name="base_color",
    frame_index=1,
    points=[{"x": 8, "y": 2}, {"x": 14, "y": 6}, {"x": 12, "y": 12}, {"x": 4, "y": 10}],
    color="#38b764", fill=True
)
```

### Paths (Polylines)
Use `draw_path` for curves and complex outlines:
```python
draw_path(
    filename="hero.aseprite",
    layer_name="outline",
    frame_index=1,
    points=[{"x": 5, "y": 3}, {"x": 8, "y": 2}, {"x": 12, "y": 2}, {"x": 15, "y": 5}],
    color="#1a1c2c"
)
```

### Flood Fill
Use `fill_area_at` to fill enclosed regions:
```python
fill_area_at(
    filename="hero.aseprite",
    layer_name="base_color",
    frame_index=1,
    x=10, y=6,
    color="#5d275d"
)
```

### Gradients
Use `apply_gradient_rect` for sky, atmosphere, glow:
```python
apply_gradient_rect(
    filename="bg.aseprite",
    layer_name="sky",
    frame_index=1,
    x=0, y=0, width=320, height=180,
    color_start="#1a1c2c", color_end="#41a6f6",
    direction="vertical"
)
```

## Drawing Techniques

### Symmetry Shortcut
Draw one half, then mirror:
```python
# Draw left half on "base_color" layer
draw_pixels_at(filename="hero.aseprite", layer_name="base_color", frame_index=1, pixels=[...])

# Flip to create right half
flip_layer(filename="hero.aseprite", layer_name="base_color", direction="horizontal")
```

### Outline-First Method
1. Draw the outline shape with `draw_pixels_at` or `draw_line_at`
2. Fill interior with `fill_area_at`
3. Add shading pixels on top

### Block-In Method
1. Draw a rough filled shape with `draw_rectangle_at` or `draw_polygon` (fill=True)
2. Refine edges by adding/removing pixels
3. Add detail layers on top

### Gradient Shading
For smooth shading on large areas:
```python
apply_gradient_rect(
    filename="hero.aseprite",
    layer_name="shading",
    frame_index=1,
    x=6, y=4, width=9, height=12,
    color_start="#00000000",  # transparent
    color_end="#333c5780",    # semi-transparent shadow
    direction="vertical"
)
```

## Read-Back Verification

After drawing, always verify:
```python
# Read a single pixel
get_pixel_color(filename="hero.aseprite", x=10, y=6, layer_name="outline", frame_index=1)

# Read a region
get_pixels_rect(filename="hero.aseprite", x=0, y=0, width=32, height=32,
    layer_name="base_color", frame_index=1)
```

## Common Pixel Patterns

### Dithering (Gradient Between Two Colors)
Alternate pixels in a checkerboard pattern:
```
A B A B
B A B A
A B A B
```

### Anti-Aliasing on Curves
Place intermediate-color pixels at curve edges:
```
  ##
 #  #
#    #
 #  #
  ##
```

### Selective Outline
Only outline edges that face the background (skip edges between body parts):
```
Outline: top, left, right of head
No outline: where neck meets body
```