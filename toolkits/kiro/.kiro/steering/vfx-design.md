---
inclusion: auto
name: vfx-design
description: Design and create VFX and spell effect pixel art. Use when creating explosions, fire, magic bolts, slashes, healing effects, or other visual effects.
---

# VFX Design

## Constraints
- DO NOT create characters, tiles, or backgrounds
- DO NOT make VFX too long — keep to 4-8 frames at 40-80ms each
- DO NOT use outlines on VFX
- ONLY create VFX, spells, impacts, and visual effects

## Approach
1. CONCEPT: Effect type, size (16-64px), palette (3-6 colors), frame count (4-8)
2. CANVAS: Center the effect on canvas
3. LAYERS: flash (optional) → core → glow → particles
4. DRAW: Frame 1 = small bright core + glow using draw_circle_at
5. ANIMATE: Expand + fade. Core expands then fades, glow fades out.
6. TAG: set_tag(name="effect", direction="forward")

## VFX Pattern Reference
| Effect | Core Color | Glow Color | Frames | Duration |
|--------|-----------|-----------|--------|----------|
| Explosion | #ffffff → #ffcc00 | #ef7d57 → #b13e53 | 6-8 | 40-60ms |
| Fire | #ffffff → #ffcc00 | #ef7d57 | 4-8 | 60-100ms |
| Magic bolt | #41a6f6 → #73eff7 | #257179 | 4-6 | 50-80ms |
| Heal | #a7f070 → #38b764 | #257179 | 6-8 | 80-120ms |
| Slash | #ffffff | #ef7d57 | 3-4 | 30-50ms |
