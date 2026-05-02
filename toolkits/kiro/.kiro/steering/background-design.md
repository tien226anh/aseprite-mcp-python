---
inclusion: auto
name: background-design
description: Design and create parallax background pixel art. Use when creating multi-layer parallax backgrounds, game scenes, or environment backdrops.
---

# Background Design

## Constraints
- DO NOT create characters, tiles, or VFX
- DO NOT make backgrounds too small — use at least 240×135
- DO NOT forget atmospheric perspective
- ONLY create backgrounds, scenes, and environment backdrops

## Approach
1. CONCEPT: Scene type, canvas size (wider for parallax), depth layers (2-5)
2. LAYERS (far to near): sky → mountains → midground → foreground → foreground_detail
3. DRAW (far to near): apply_gradient_rect for sky, draw_polygon for silhouettes
4. ANIMATE PARALLAX: Far layers move slowly, near layers move fast
5. RULES: Atmospheric perspective, layer separation, canvas wider than viewport
