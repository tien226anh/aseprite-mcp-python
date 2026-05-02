# Animation Patterns & Techniques

## Frame Management

### Add frames with timing
```
add_frames(filename="sprite.aseprite", count=4, duration_ms=120)
```

### Copy a base pose to all frames
```
propagate_frame_to_range(filename="sprite.aseprite", source_frame=1, start_frame=2, end_frame=4)
```

### Copy a specific frame
```
copy_frame(filename="sprite.aseprite", source_frame=1, target_frame=3)
```

### Set all frame durations
```
set_frame_duration_all(filename="sprite.aseprite", duration_ms=100)
```

### Duplicate a frame range
```
duplicate_frame_range(filename="sprite.aseprite", start_frame=1, end_frame=4, times=1)
```

## Tweening

### Linear position tween
```
tween_cel_positions(
  filename="sprite.aseprite", layer_name="arm",
  start_frame=1, end_frame=4,
  start_x=10, start_y=20, end_x=30, end_y=20,
  create_missing_cels=True
)
```

### Eased position tween
```
tween_cel_positions_eased(
  filename="sprite.aseprite", layer_name="arm",
  start_frame=1, end_frame=6,
  start_x=0, start_y=0, end_x=20, end_y=-10,
  easing="smoothstep", create_missing_cels=True
)
```

**Easing options**: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `smoothstep`

| Easing | Curve | Best For |
|--------|-------|----------|
| `linear` | Constant speed | Parallax, mechanical motion |
| `ease_in` | Slow start, fast end | Falling, launching |
| `ease_out` | Fast start, slow end | Landing, stopping |
| `ease_in_out` | Slow start & end | Smooth transitions |
| `smoothstep` | Smooth S-curve | Natural organic motion |

### Oscillation (sine wave)
```
oscillate_cel_positions(
  filename="sprite.aseprite", layer_name="body",
  start_frame=1, end_frame=8,
  amplitude_x=0, amplitude_y=3, cycles=1.0
)
```

**Parameters**:
- `amplitude_x/y`: Pixel distance of oscillation
- `cycles`: Number of complete sine waves (0.5 = half wave, 1.0 = full wave)
- `phase_deg`: Phase offset in degrees (0° = start at center, 90° = start at peak)

### Opacity tween (fade in/out)
```
tween_cel_opacity_eased(
  filename="sprite.aseprite", layer_name="glow",
  start_frame=1, end_frame=6,
  start_opacity=255, end_opacity=0, easing="ease_out"
)
```

## Animation Tags

```
set_tag(filename="sprite.aseprite", name="idle", from_frame=1, to_frame=4, direction="pingpong")
set_tag(filename="sprite.aseprite", name="walk", from_frame=5, to_frame=12, direction="forward")
set_tag(filename="sprite.aseprite", name="attack", from_frame=13, to_frame=18, direction="forward")
```

**Directions**: `forward`, `reverse`, `pingpong`

| Direction | Behavior |
|-----------|----------|
| `forward` | Play 1→N, then restart |
| `reverse` | Play N→1, then restart |
| `pingpong` | Play 1→N→1→N (bounce) |

## Common Animation Patterns

| Pattern | Technique | Parameters |
|---------|-----------|------------|
| Idle bob | `oscillate_cel_positions` | amplitude_y=1-2, cycles=1 |
| Walk cycle | Keyframes + `propagate_cels` for static parts | 6-8 frames, 80-100ms |
| Attack swing | `tween_cel_positions_eased` ease_out | 4-6 frames, 60-80ms |
| Bounce | `oscillate_cel_positions` | amplitude_y=3-5, cycles=0.5 |
| Fade in | `tween_cel_opacity_eased` 0→255 | ease_in |
| Fade out | `tween_cel_opacity_eased` 255→0 | ease_out |
| Pulse glow | `tween_cel_opacity_eased` 255→180→255 | ease_in_out, pingpong tag |
| Parallax | `tween_cel_positions` linear | Different speeds per layer |
| Float | `oscillate_cel_positions` | amplitude_y=2, cycles=1 |
| Spin | `rotate_layer` 90° per frame | 4 frames |
| Shake | `oscillate_cel_positions` | amplitude_x=2, cycles=4-8, short duration |

## Propagating Cels Across Layers

Copy specific layers from one frame to a range:
```
propagate_cels(
  filename="sprite.aseprite",
  layer_names=["outline", "base_colors"],
  source_frame=1, start_frame=2, end_frame=4
)
```

## Cel Position Offsets

Shift a layer across frames without tweening:
```
offset_cel_positions(
  filename="sprite.aseprite", layer_name="arm",
  start_frame=3, end_frame=6, dx=2, dy=-1
)
```

## Cel Management

### Create an empty cel
```
create_cel(filename="sprite.aseprite", layer_name="arm", frame_index=3, x=0, y=0)
```

### Delete a cel
```
clear_cel(filename="sprite.aseprite", layer_name="arm", frame_index=3)
```

### Copy a cel between frames
```
copy_cel(filename="sprite.aseprite", layer_name="arm", source_frame=1, target_frame=3)
```

### Set cel position
```
set_cel_position(filename="sprite.aseprite", layer_name="arm",
  frame_index=1, x=10, y=20, create_if_missing=True)
```