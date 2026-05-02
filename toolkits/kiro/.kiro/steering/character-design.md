---
inclusion: auto
name: character-design
description: Design and create character pixel art sprites. Use when creating hero characters, enemies, NPCs, or bosses with idle, walk, attack, or other animations.
---

# Character Design

## Constraints
- DO NOT create tiles, backgrounds, VFX, or items — use the appropriate steering file
- DO NOT skip the verify step — always read back pixels after drawing
- DO NOT use legacy tools — use the `_at` variants
- ONLY create character sprites

## Approach
1. CONCEPT: Define role, silhouette, palette (12-16 colors), animation needs
2. CANVAS + PALETTE: create_canvas(width=32, height=32) then set_palette()
3. LAYERS (bottom-up): shadow → outline → base_color → shading → details → highlights. For animated: arm_back → body → arm_front → head
4. DRAW layer by layer using _at variants. Read back after each layer.
5. ANIMATE: Use #animation steering for idle breathing, walk cycles, attack swings
6. TAG: set_tag(name="idle", from_frame=1, to_frame=4, direction="pingpong")
7. VALIDATE: validate_scene(required_layers=["outline", "base_color"])
8. REVIEW: Use #review steering

Sizes: 16×16 (small enemies), 24×24 (medium), 32×32 (player), 48×48 (boss).
Symmetry: draw half → flip_layer(direction="horizontal")
