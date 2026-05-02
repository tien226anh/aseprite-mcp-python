# Canvas Size Guide

## By Asset Type

| Asset Type | Typical Size | Notes |
|-----------|-------------|-------|
| UI Icons | 8×8 to 16×16 | Minimal detail, high readability |
| Items/Pickups | 16×16 to 24×24 | Enough for shape + color + shine |
| Small enemies | 16×16 to 24×24 | Readable at game scale |
| Player characters | 32×32 to 48×48 | Room for detail and animation |
| Bosses | 48×48 to 128×128 | Large, detailed, imposing |
| Portraits | 64×64 to 128×128 | Face detail, expression |
| Tiles | 16×16 or 32×32 | Must tile seamlessly |
| Tileset strips | 128×16, 256×16 | Multiple tiles in a row |
| Backgrounds | 240×135 to 960×540 | Match game resolution |
| VFX | 16×16 to 64×64 | Centered on transparent bg |
| Cutscene art | 128×128 to 320×180 | Cinematic, detailed |

## Choosing the Right Size

**Smaller is better** for pixel art. Constraints breed creativity:
- Start with the **smallest size** that can convey the design
- You can always `resize_canvas` later, but shrinking loses detail
- Consider the **game's display scale**: a 16×16 sprite displayed at 4x = 64px on screen

## Resolution Reference

| Game Style | Internal Resolution | Canvas Size |
|-----------|-------------------|-------------|
| Game Boy | 160×144 | 160×144 |
| NES | 256×240 | 256×240 |
| SNES | 256×224 | 256×224 |
| Indie standard | 320×180 | 320×180 |
| HD indie | 480×270 | 480×270 |
| Full HD | 960×540 | 960×540 |

## Background Canvas Sizing

For parallax backgrounds, make the canvas **wider than the viewport** to allow scrolling:
- 2x viewport width for gentle parallax
- 3x viewport width for deep parallax with multiple layers