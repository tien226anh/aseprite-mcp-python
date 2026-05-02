---
inclusion: manual
---

# Asset Review

Review pixel art assets for quality issues AND apply fixes when found.

## Review Checklist
1. STRUCTURAL: validate_scene() — all layers exist, all frames have cels
2. PIXEL: get_pixels_rect() — compare against intent
3. ANIMATION: audit_animation() — overlaps, out-of-range, missing cels
4. NAMING: snake_case filenames, PascalCase layers, snake_case tags

## Fix Workflow
- Missing pixels → draw_pixels_at
- Wrong colors → remap_colors_in_cel_range
- Missing cels → ensure_layers_present
- Misaligned → set_cel_position
- Timing → set_frame_duration

## Report Format
1. Status: PASS or NEEDS_FIXES
2. Issues Found with severity
3. Fixes Applied
4. Re-verification

Self-review cycle: Review → Fix → Re-verify → Repeat until PASS
