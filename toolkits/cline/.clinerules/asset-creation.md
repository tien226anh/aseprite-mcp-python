# Aseprite Asset Creation

## Pipeline
```
CONCEPT → CANVAS → PALETTE → LAYERS → DRAW → VERIFY → ANIMATE → TAG → VALIDATE → EXPORT
```

## Naming Conventions
- Filenames: `snake_case.aseprite`
- Character sprites: `{character}_{action}.aseprite`
- Layer names: PascalCase for body parts, Tags: snake_case

## Directory Organization
```
generated_assets/{project_name}/
├── hero/           # Player characters
├── monsters/       # Enemies and NPCs
├── environment/    # Tiles, backgrounds, structures
├── effects/        # VFX, spells, impacts
└── cutscene/       # Story scenes, portraits
```

## Canvas Sizes
| Asset Type | Typical Size | Frames |
|-----------|-------------|--------|
| Items/pickups | 16×16 to 24×24 | 1-4 |
| Small enemies | 16×16 to 24×24 | 4 |
| Player characters | 32×32 to 48×48 | 4-8 |
| Tiles | 16×16 or 32×32 | 1 |
| Backgrounds | 240×135 to 960×540 | 1-8 |
| VFX | 16×16 to 64×64 | 4-8 |

## Layer Architecture
- **Characters**: shadow → outline → base_color → shading → details → highlights
- **Items**: outline → base_color → shading → shine
- **Tiles**: base → surface → details (no outline)
- **Backgrounds**: sky → mountains → midground → foreground → foreground_detail
- **VFX**: flash → core → glow → particles (transparent background)

## Animation Timing
| Animation | Duration | Frames | Easing |
|-----------|----------|--------|--------|
| Idle | 100-150ms | 4 | ease_in_out |
| Walk | 80-120ms | 8 | linear |
| Attack | 50-80ms | 4-6 | ease_in → ease_out |
| Float | 100-150ms | 4-8 | sine |
| VFX expand | 40-80ms | 4-8 | ease_out |

## Always Use `_at` Variants & Read Back After Drawing
