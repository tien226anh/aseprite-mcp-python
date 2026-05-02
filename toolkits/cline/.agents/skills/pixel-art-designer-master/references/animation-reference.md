# Animation Reference

## Frame Management

### Adding Frames
```python
# Add single frame (default 100ms)
add_frame(filename="hero.aseprite")

# Add multiple frames with duration
add_frames(filename="hero.aseprite", count=4, duration=120)

# Set duration for all frames
set_frame_duration_all(filename="hero.aseprite", duration_ms=100)
```

### Copying Frames
```python
# Copy all cels from one frame to another
copy_frame(filename="hero.aseprite", from_frame=1, to_frame=3)

# Copy a specific cel
copy_cel(filename="hero.aseprite", layer_name="arm_front", from_frame=1, to_frame=3)

# Propagate a frame across a range
propagate_frame_to_range(filename="hero.aseprite", source_frame=1, start_frame=2, end_frame=4)
```

### Duplicating Frame Ranges
```python
# Duplicate frames 1-4 once (creates frames 5-8)
duplicate_frame_range(filename="hero.aseprite", start_frame=1, end_frame=4, times=1)
```

## Animation Types

### 1. Keyframe Animation
Draw each frame manually:
```python
# Frame 1: idle pose
draw_pixels_at(filename="hero.aseprite", layer_name="body", frame_index=1, pixels=[...])

# Frame 2: slight movement
draw_pixels_at(filename="hero.aseprite", layer_name="body", frame_index=2, pixels=[...])

# Frame 3: extreme pose
draw_pixels_at(filename="hero.aseprite", layer_name="body", frame_index=3, pixels=[...])
```

### 2. Cel Position Tweening
Move elements smoothly between positions:
```python
# Linear tween
tween_cel_positions(
    filename="hero.aseprite",
    layer_name="arm_front",
    start_frame=1, end_frame=4,
    start_x=10, start_y=8,
    end_x=14, end_y=6
)

# Eased tween (smooth acceleration/deceleration)
tween_cel_positions_eased(
    filename="hero.aseprite",
    layer_name="arm_front",
    start_frame=1, end_frame=4,
    start_x=10, start_y=8,
    end_x=14, end_y=6,
    easing="ease_in_out"
)
```

### 3. Oscillating Motion
Sine-wave back-and-forth:
```python
oscillate_cel_positions(
    filename="hero.aseprite",
    layer_name="item",
    start_frame=1, end_frame=8,
    center_x=16, center_y=10,
    amplitude_x=2, amplitude_y=4,
    frequency=1.0
)
```

### 4. Opacity Animation
Fade in/out effects:
```python
tween_cel_opacity_eased(
    filename="hero.aseprite",
    layer_name="glow",
    start_frame=1, end_frame=6,
    start_opacity=0, end_opacity=200,
    easing="ease_in"
)
```

### 5. Layer Visibility Toggle
Show/hide layers per frame:
```python
# Blink animation: hide eyes on frame 3
set_layer_visibility(filename="hero.aseprite", layer_name="eyes", visible=False)
# Note: visibility is per-layer, not per-frame in Aseprite
# For per-frame visibility, use opacity instead:
set_layer_opacity(filename="hero.aseprite", layer_name="eyes", opacity=0)
```

## Easing Functions

| Easing | Effect | Use For |
|--------|--------|---------|
| `linear` | Constant speed | Scrolling, mechanical motion |
| `ease_in` | Slow start, fast end | Throwing, launching |
| `ease_out` | Fast start, slow end | Landing, settling |
| `ease_in_out` | Slow start and end | Natural movement, breathing |
| `smoothstep` | Very smooth | Organic motion, floating |

## Animation Tags

Tags mark frame ranges for game engines:
```python
set_tag(filename="hero.aseprite", name="idle", from_frame=1, to_frame=4, direction="forward")
set_tag(filename="hero.aseprite", name="walk", from_frame=5, to_frame=12, direction="forward")
set_tag(filename="hero.aseprite", name="attack", from_frame=13, to_frame=18, direction="forward")
set_tag(filename="hero.aseprite", name="blink", from_frame=19, to_frame=22, direction="pingpong")
```

## Common Animation Patterns

### Idle Breathing (4 frames)
```
Frame 1: Base pose (100ms)
Frame 2: Slight up (120ms)
Frame 3: Base pose (100ms)
Frame 4: Slight down (80ms)
```
Use `tween_cel_positions_eased` with `ease_in_out` for the body layer.

### Walk Cycle (8 frames)
```
Frame 1: Contact (right foot forward)
Frame 2: Down (body lowest)
Frame 3: Passing (right foot under)
Frame 4: Up (body highest)
Frame 5: Contact (left foot forward)
Frame 6: Down
Frame 7: Passing
Frame 8: Up
```

### Attack Swing (6 frames)
```
Frame 1: Idle → anticipation (arm back)
Frame 2: Wind-up
Frame 3: Swing start
Frame 4: Impact (arm fully extended)
Frame 5: Follow-through
Frame 6: Return to idle
```
Use `ease_in` for anticipation, `ease_out` for follow-through.

### Float / Hover (oscillate)
```python
oscillate_cel_positions(
    filename="item.aseprite",
    layer_name="item",
    start_frame=1, end_frame=8,
    center_x=8, center_y=8,
    amplitude_x=0, amplitude_y=2,
    frequency=1.0
)
```

### Fade In/Out
```python
# Fade in
tween_cel_opacity_eased(
    filename="vfx.aseprite", layer_name="core",
    start_frame=1, end_frame=4,
    start_opacity=0, end_opacity=255,
    easing="ease_in"
)

# Fade out
tween_cel_opacity_eased(
    filename="vfx.aseprite", layer_name="core",
    start_frame=5, end_frame=8,
    start_opacity=255, end_opacity=0,
    easing="ease_out"
)
```

## Frame Duration Guide

| Animation Type | Frame Duration | Notes |
|---------------|---------------|-------|
| Idle | 100-150ms | Subtle, slow |
| Walk | 80-120ms | Medium pace |
| Run | 60-80ms | Fast |
| Attack | 50-80ms | Quick, snappy |
| Impact | 30-50ms | Very fast |
| Float | 100-150ms | Slow, gentle |
| VFX expand | 40-80ms | Fast expansion |
| VFX fade | 80-150ms | Slow dissipation |
| Blink | 50-80ms | Quick |