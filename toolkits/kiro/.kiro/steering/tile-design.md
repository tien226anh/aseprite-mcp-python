---
inclusion: auto
name: tile-design
description: Design and create tile and environment pixel art. Use when creating tilesets, platform tiles, dungeon tiles, or environment structures.
---

# Tile Design

## Constraints
- DO NOT create characters, VFX, or backgrounds
- DO NOT skip the seamless tiling verification step
- DO NOT use outlines on tiles
- ONLY create tiles, platforms, and environment structures

## Approach
1. CONCEPT: Tile type, size (16×16 or 32×32), palette (4-8 colors)
2. CANVAS: Single tile or tileset strip (128×16)
3. LAYERS: base → surface → details
4. DRAW: Base fill → surface pattern → detail accents using _at variants
5. VERIFY SEAMLESS TILING: Read left/right edges, ensure no visible seams
6. RULES: No outlines, edge variation, color noise, dithering, consistent lighting
