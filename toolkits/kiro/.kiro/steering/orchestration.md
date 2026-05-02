---
inclusion: auto
name: orchestration
description: Orchestrate a full pixel art asset design session. Use when creating multiple game assets in sequence or parallel.
---

# Asset Design Orchestration

## Workflow
```
PLAN → DELEGATE → REVIEW → FIX → EXPORT
```

### 1. PLAN
Parse request into asset list with type/size/animation/dependencies.

### 2. DELEGATE
| Asset Type | Steering File |
|-----------|---------------|
| Characters | #character-design |
| Tiles | #tile-design |
| VFX | #vfx-design |
| Backgrounds | #background-design |
| Items | #item-design |
| Animation | #animation |

### 3. REVIEW
Each asset goes through #review.

### 4. FIX
Send fixes back to specialist or to #review.

### 5. EXPORT
All assets go through #export.

## Parallel vs Sequential
- Parallel: Independent assets (character + tileset, VFX + backgrounds)
- Sequential: Animation after base sprite, compositing after both assets, palette swaps after original reviewed
