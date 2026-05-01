---
description: "Use when: creating pixel art game assets with Aseprite MCP tools; defining sprites, tilesets, backgrounds, VFX, or character animations; organizing asset directories; setting up canvas sizes, palettes, and layer stacks for game art. Covers the full asset creation workflow and project naming/sizing/organization conventions."
name: "Aseprite Asset Creation"
applyTo: "generated_assets/**"
---

# Aseprite Asset Creation Workflow & Conventions

## Asset Creation Pipeline

```
CONCEPT → CANVAS → PALETTE → LAYERS → DRAW → VERIFY → ANIMATE → TAG → VALIDATE → EXPORT
```

### 1. CONCEPT — Define the Asset
Decide: type (character, item, tile, background, VFX), size, palette, animation needs, style.

### 2. CANVAS — Create and Configure
```python
create_canvas(width=32, height=32, filename="hero_idle.aseprite")
set_palette(filename="hero_idle.aseprite", colors=["#1a1c2c", "#5d275d", ...])
```

### 3. LAYERS — Set Up the Stack
Create layers bottom-up (first created = bottom):
```python
add_layer(filename="hero_idle.aseprite", layer_name="shadow")
add_layer(filename="hero_idle.aseprite", layer_name="outline")
add_layer(filename="hero_idle.aseprite", layer_name="base_color")
add_layer(filename="hero_idle.aseprite", layer_name="shading")
add_layer(filename="hero_idle.aseprite", layer_name="details")
add_layer(filename="hero_idle.aseprite", layer_name="highlights")
```

### 4. DRAW — Layer by Layer
**Always use `_at` variants** to target specific layer+frame:
```python
draw_pixels_at(filename="hero_idle.aseprite", layer_name="outline", frame_index=1, pixels=[...])
fill_area_at(filename="hero_idle.aseprite", layer_name="base_color", frame_index=1, x=10, y=8, color="#5d275d")
```

### 5. VERIFY — Read Back and Compare
```python
get_pixels_rect(filename="hero_idle.aseprite", x=0, y=0, width=32, height=32,
    layer_name="outline", frame_index=1)
```

### 6. ANIMATE — Add Motion
```python
add_frames(filename="hero_idle.aseprite", count=3, duration=120)
tween_cel_positions_eased(filename="hero_idle.aseprite", layer_name="body",
    start_frame=1, end_frame=4, start_x=8, start_y=10, end_x=8, end_y=9,
    easing="ease_in_out")
```

### 7. TAG — Mark Animation Ranges
```python
set_tag(filename="hero_idle.aseprite", name="idle", from_frame=1, to_frame=4, direction="pingpong")
```

### 8. VALIDATE — Check Structure
```python
validate_scene(filename="hero_idle.aseprite", required_layers=["outline", "base_color"])
ensure_layers_present(filename="hero_idle.aseprite", layer_names=["outline", "base_color"],
    start_frame=1, end_frame=4)
```

### 9. EXPORT — Game-Ready Output
```python
export_sprite(filename="hero_idle.aseprite", output_filename="hero_idle.png", format="png")
```

## Naming Conventions

| Pattern | Example |
|---------|---------|
| Filenames | `snake_case.aseprite` — `knight_idle.aseprite`, `dungeon_tiles.aseprite` |
| Character sprites | `{character}_{action}.aseprite` — `knight_walk.aseprite`, `goblin_idle.aseprite` |
| Environment | `{descriptive_name}.aseprite` — `dungeon_tiles.aseprite`, `castle_tower.aseprite` |
| Effects | `{effect_type}.aseprite` — `melee_slash.aseprite`, `fireball_spell.aseprite` |
| Animation tags | `{action_state}` — `idle`, `walk`, `melee_attack`, `fire_breath` |
| Layer names | `PascalCase` for body parts — `Body`, `Armor`, `Sword`, `Cape`, `Eyes` |

## Directory Organization

```
generated_assets/{project_name}/
├── hero/           # Player characters
├── monsters/       # Enemies and NPCs
├── environment/    # Tiles, backgrounds, structures
├── effects/        # VFX, spells, impacts
└── cutscene/       # Story scenes, portraits
```

Each `.aseprite` file has a corresponding `.png` export. Animated effects also export `.gif`.

## Canvas Size Reference

| Asset Type | Typical Size | Frames |
|-----------|-------------|--------|
| UI icons | 8×8 to 16×16 | 1 |
| Items/pickups | 16×16 to 24×24 | 1-4 (float) |
| Small enemies | 16×16 to 24×24 | 4 |
| Player characters | 32×32 to 48×48 | 4-8 |
| Bosses | 48×48 to 128×128 | 4-8 |
| Tiles | 16×16 or 32×32 | 1 (or 4 for animated) |
| Tileset strips | 128×16 or 256×16 | 1 |
| Backgrounds | 240×135 to 960×540 | 1-8 (parallax) |
| VFX | 16×16 to 64×64 | 4-8 |
| Cutscene art | 64×64 to 320×180 | 1 |

## Layer Architecture by Asset Type

### Characters
```
highlights → details → shading → base_color → outline → shadow
```
Animation-ready: separate `arm_back`, `body`, `arm_front`, `head` layers.

### Items/Pickups
```
shine → details → base_color → outline → glow (optional)
```

### Tiles
```
details → surface → base
```
No outline. Must tile seamlessly.

### Backgrounds (Parallax)
```
foreground_detail → midground → background → sky
```
Each layer scrolls at different speed.

### VFX
```
particles → glow → core → flash (optional)
```
Expand then fade pattern.

## Palette Strategy

- **Small sprites (≤16px)**: 6-10 colors
- **Medium sprites (32px)**: 12-16 colors
- **Large sprites (64px+)**: 16-32 colors
- Always include: near-black, near-white, and 3 values per hue (highlight, midtone, shadow)
- Hue-shift shadows cool (blue/purple), highlights warm (yellow/orange)

## Animation Timing

| Animation | Frame Duration | Frames |
|-----------|---------------|--------|
| Idle | 100-150ms | 4 |
| Walk | 80-120ms | 8 |
| Run | 60-80ms | 6 |
| Attack | 50-80ms | 4-6 |
| Float | 100-150ms | 4-8 |
| VFX expand | 40-80ms | 4-8 |
| VFX fade | 80-150ms | 4-6 |

## Easing Functions

| Easing | Use For |
|--------|---------|
| `linear` | Scrolling, mechanical motion |
| `ease_in` | Throwing, launching |
| `ease_out` | Landing, settling |
| `ease_in_out` | Natural movement, breathing |
| `smoothstep` | Organic motion, floating |

## Tool Selection Quick Reference

| Task | Tool |
|------|------|
| Large flat area | `fill_area_at`, `draw_rectangle_at` (fill=True) |
| Sky / atmosphere | `apply_gradient_rect` |
| Character outline | `draw_pixels_at` + `draw_line_at` |
| Rounded shapes | `draw_circle_at`, `draw_polygon` |
| Irregular shapes | `draw_polygon` (fill=True) |
| Curves / paths | `draw_path` |
| Single-pixel details | `draw_pixels_at` |
| Symmetry | Draw half → `flip_layer` |
| Smooth motion | `tween_cel_positions_eased` |
| Oscillating motion | `oscillate_cel_positions` |
| Fade in/out | `tween_cel_opacity_eased` |
| Color swaps | `remap_colors_in_cel_range` |
| Verify pixels | `get_pixel_color`, `get_pixels_rect` |
| Verify structure | `validate_scene`, `audit_animation` |