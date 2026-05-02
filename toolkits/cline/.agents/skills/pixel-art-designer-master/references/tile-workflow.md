# Tile / Platform Workflow

## Design Process

### 1. Concept
- Define tile type (ground, wall, water, grass, stone, wood, lava)
- Choose tile size (16×16 or 32×32 are standard)
- Pick palette (4-8 colors per tile type)
- Decide if animated (water, lava) or static (stone, wood)

### 2. Canvas Setup

**Single tile:**
```python
create_canvas(width=16, height=16, filename="grass_tile.aseprite")
```

**Tileset strip** (multiple tiles in a row):
```python
create_canvas(width=128, height=16, filename="dungeon_tiles.aseprite")
```

**Set palette:**
```python
set_palette(filename="grass_tile.aseprite", colors=[
    "#1a1c2c",  # outline (optional for tiles)
    "#38b764",  # grass light
    "#257179",  # grass mid
    "#1e6e3e",  # grass dark
    "#5d275d",  # dirt
    "#3b2e42",  # dirt dark
])
```

### 3. Layer Architecture

```python
add_layer(filename="grass_tile.aseprite", layer_name="base")      # solid fill
add_layer(filename="grass_tile.aseprite", layer_name="surface")    # main pattern
add_layer(filename="grass_tile.aseprite", layer_name="details")    # cracks, grass blades
```

### 4. Drawing

**Base layer** — solid fill:
```python
draw_rectangle_at(
    filename="grass_tile.aseprite", layer_name="base", frame_index=1,
    x=0, y=0, width=16, height=16,
    color="#257179", fill=True
)
```

**Surface layer** — main pattern:
```python
# Grass pattern with variation
draw_pixels_at(filename="grass_tile.aseprite", layer_name="surface", frame_index=1, pixels=[
    {"x": 2, "y": 3, "color": "#38b764"},
    {"x": 5, "y": 1, "color": "#38b764"},
    {"x": 8, "y": 4, "color": "#38b764"},
    # ... scattered grass pixels
])
```

**Details layer** — small accents:
```python
draw_pixels_at(filename="grass_tile.aseprite", layer_name="details", frame_index=1, pixels=[
    {"x": 3, "y": 7, "color": "#a7f070"},  # bright grass blade
    {"x": 11, "y": 5, "color": "#a7f070"},  # bright grass blade
])
```

### 5. Seamless Tiling Verification

**Critical**: Tiles must tile seamlessly. Verify by:
1. Drawing the tile
2. Reading back the edges
3. Checking that left edge matches right edge, top matches bottom

```python
# Read left edge
left_edge = get_pixels_rect(filename="grass_tile.aseprite", x=0, y=0, width=1, height=16,
    layer_name="surface", frame_index=1)

# Read right edge
right_edge = get_pixels_rect(filename="grass_tile.aseprite", x=15, y=0, width=1, height=16,
    layer_name="surface", frame_index=1)

# Compare — they should flow naturally (not necessarily identical)
```

**Tips for seamless tiles:**
- Avoid hard lines at edges
- Let patterns flow across boundaries
- Use `draw_path` for organic edges that wrap
- Test by placing 4 copies in a 2×2 grid

### 6. Animated Tiles

For water, lava, or other animated tiles:

```python
# Create 4 frames for water animation
add_frames(filename="water_tile.aseprite", count=3, duration=200)

# Frame 1: base water
draw_pixels_at(filename="water_tile.aseprite", layer_name="surface", frame_index=1, pixels=[...])

# Frame 2: wave shifted
draw_pixels_at(filename="water_tile.aseprite", layer_name="surface", frame_index=2, pixels=[...])

# Frame 3: wave shifted more
draw_pixels_at(filename="water_tile.aseprite", layer_name="surface", frame_index=3, pixels=[...])

# Frame 4: back to base (or close)
draw_pixels_at(filename="water_tile.aseprite", layer_name="surface", frame_index=4, pixels=[...])

set_tag(filename="water_tile.aseprite", name="flow", from_frame=1, to_frame=4, direction="forward")
```

### 7. Tileset Organization

For a tileset strip, organize tiles left-to-right:
```
| grass | grass_edge | dirt | dirt_edge | stone | stone_edge | water | water_edge |
```

Each tile occupies a fixed-width section of the strip.

### 8. Export

```python
# Single tile as PNG
export_sprite(filename="grass_tile.aseprite", output_filename="grass_tile.png", format="png")

# Tileset strip as spritesheet
spritesheet_export(filename="dungeon_tiles.aseprite", output_filename="dungeon_tiles_sheet.png")
```

## Tile Design Tips

- **No outlines** (usually): Tiles typically don't have outlines — they tile seamlessly
- **Edge variation**: Avoid identical edges that create visible grid lines
- **Color noise**: Add subtle color variation to break up flat areas
- **Dithering**: Use dithering for smooth transitions between tile types
- **Corner blending**: Design corner tiles that blend between two terrain types
- **Consistent lighting**: All tiles in a set must share the same light direction