---
inclusion: auto
name: animation
description: Add animation to existing pixel art sprites. Use when adding idle, walk, attack, or other animations to a completed sprite.
---

# Animation

## Constraints
- DO NOT draw new sprites — only add animation to existing sprites
- DO NOT modify the base sprite's pixel art
- DO NOT forget to validate after animating
- ONLY animate existing sprites

## Approach
1. ANALYZE: get_sprite_info() to understand current structure
2. ADD FRAMES: add_frames(count=N, duration=120)
3. CHOOSE TECHNIQUE:
   - Idle breathing: tween_cel_positions_eased with ease_in_out
   - Walk cycle: copy_frame + per-frame deltas
   - Attack swing: tween_cel_positions_eased with ease_in→ease_out
   - Float/hover: oscillate_cel_positions (sine)
   - Fade in/out: tween_cel_opacity_eased
   - Parallax scroll: tween_cel_positions (linear)
4. ENSURE CELS: ensure_layers_present() for all layers across all frames
5. TAG: set_tag() with appropriate direction
6. VALIDATE: audit_animation()

Timing: Idle 100-150ms/4f, Walk 80-120ms/8f, Run 60-80ms/6f, Attack 50-80ms/4-6f, Float 100-150ms/4-8f
