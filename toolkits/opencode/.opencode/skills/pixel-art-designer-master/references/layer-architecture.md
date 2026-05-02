# Layer Architecture

## Why Layers Matter

Layers are the structural backbone of pixel art. They enable:
- **Independent animation** per element (arm swings, cape flows, eyes blink)
- **Selective editing** without affecting other parts
- **Compositing** from multiple sprites
- **Opacity control** for transparency effects
- **Read-back verification** per layer

## Standard Layer Stacks by Asset Type

### Character Sprite

```
Top
 ├── highlights       (specular, rim light)
 ├── details           (eyes, mouth, accessories)
 ├── shading           (shadow areas)
 ├── base_color        (flat fill per body part)
 ├── outline           (dark border)
 └── shadow            (ground shadow, optional)
Bottom
```

**Animation layers** (separate from the static stack):
```
 ├── arm_back          (behind body)
 ├── body              (torso, legs)
 └── arm_front         (in front of body)
```

### Item / Pickup

```
Top
 ├── shine             (specular highlight)
 ├── details           (engraving, gem, strap)
 ├── base_color        (flat fill)
 ├── outline           (border)
 └── glow              (soft glow behind item, optional)
Bottom
```

### Tile

```
Top
 ├── details           (cracks, moss, debris)
 ├── surface           (main tile pattern)
 └── base              (solid fill)
Bottom
```

### Background (Parallax)

```
Top
 ├── foreground_detail  (closest: grass, rocks)
 ├── midground          (trees, structures)
 ├── background         (mountains, clouds)
 └── sky                (gradient, stars)
Bottom
```

### VFX / Effect

```
Top
 ├── particles          (sparks, debris)
 ├── glow              (soft outer glow)
 ├── core              (bright center)
 └── flash             (full-screen flash, optional)
Bottom
```

### Portrait / Fine Art

```
Top
 ├── hair_highlight     (specular on hair)
 ├── hair_shade         (hair shadow)
 ├── hair_base          (hair flat color)
 ├── skin_highlight     (face highlights)
 ├── skin_shade         (face shadows)
 ├── skin_base          (skin flat color)
 ├── eyes              (iris, pupil, white)
 ├── outline            (border)
 └── background         (solid or gradient)
Bottom
```

## Layer Creation Pattern

```python
# Create layers in bottom-up order (first created = bottom)
add_layer(filename="hero.aseprite", layer_name="shadow")
add_layer(filename="hero.aseprite", layer_name="outline")
add_layer(filename="hero.aseprite", layer_name="base_color")
add_layer(filename="hero.aseprite", layer_name="shading")
add_layer(filename="hero.aseprite", layer_name="details")
add_layer(filename="hero.aseprite", layer_name="highlights")
```

## Layer Naming Conventions

- Use **snake_case**: `arm_front`, `base_color`, `skin_shade`
- Be **specific**: `skin_shade` not just `shade`
- Include **position**: `arm_back` vs `arm_front`
- Use **purpose**: `glow`, `shine`, `particles`

## Layer Opacity Guide

| Layer | Typical Opacity | Notes |
|-------|----------------|-------|
| Shadow | 128 (50%) | Semi-transparent ground shadow |
| Glow | 64-128 (25-50%) | Soft light effect |
| Shine | 192-255 (75-100%) | Specular highlight |
| Outline | 255 (100%) | Always fully opaque |
| Base color | 255 (100%) | Always fully opaque |
| Shading | 255 (100%) | Full opacity, use darker colors |
| Details | 255 (100%) | Full opacity |
| Highlights | 192-255 (75-100%) | Can be slightly transparent |

## Layer Visibility for Animation

Toggle layer visibility per frame to create animation effects:
- Blink: hide `eyes` layer on blink frames
- Flash: show `flash` layer on impact frames
- Glow pulse: toggle `glow` layer on/off