---
inclusion: auto
name: item-design
description: Design and create item and pickup pixel art. Use when creating weapons, potions, keys, gems, collectibles, or other game items.
---

# Item Design

## Constraints
- DO NOT create characters, tiles, backgrounds, or VFX
- DO NOT make items too large — 16×16 or 24×24 is standard
- DO NOT forget readability
- ONLY create items, pickups, weapons, and collectibles

## Approach
1. CONCEPT: Item type, size (16×16 or 24×24), palette (3-6 colors)
2. LAYERS: outline → base_color → shading → shine
3. DRAW: Outline → base fill → shading → shine highlight using _at variants
4. ANIMATE: Float with oscillate_cel_positions(amplitude_y=1)
5. PALETTE SWAPS: copy_sprite → remap_colors_in_cel_range
6. RULES: Readability at 1x, distinct silhouette, color coding

Common shapes: Potion (rectangle+circle), Sword (rectangle+crossguard), Shield (circle), Gem (polygon), Coin (circle)
