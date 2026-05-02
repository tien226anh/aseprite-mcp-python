# Agent Workflows

## When Designing a Character
1. CONCEPT: Define role, silhouette, palette (12-16 colors), animation needs
2. CANVAS + PALETTE: create_canvas(width=32, height=32) then set_palette()
3. LAYERS (bottom-up): shadow → outline → base_color → shading → details → highlights. For animated: arm_back → body → arm_front → head
4. DRAW layer by layer using _at variants. Read back after each layer.
5. ANIMATE: Use idle breathing, walk cycles, attack swings
6. TAG: set_tag(name="idle", from_frame=1, to_frame=4, direction="pingpong")
7. VALIDATE: validate_scene(required_layers=["outline", "base_color"])
8. REVIEW: Check pixel accuracy, structure, naming

Sizes: 16×16 (small enemies), 24×24 (medium), 32×32 (player), 48×48 (boss).
Symmetry: draw half → flip_layer(direction="horizontal")

## When Designing Tiles
1. CONCEPT: Tile type, size (16×16 or 32×32), palette (4-8 colors)
2. CANVAS: Single tile or tileset strip (128×16)
3. LAYERS: base → surface → details
4. DRAW: Base fill → surface pattern → detail accents
5. VERIFY SEAMLESS TILING: Read left/right edges, ensure no visible seams
6. RULES: No outlines, edge variation, color noise, dithering, consistent lighting

## When Designing VFX
1. CONCEPT: Effect type, size (16-64px), palette (3-6 colors), frame count (4-8)
2. CANVAS: Center the effect on canvas
3. LAYERS: flash (optional) → core → glow → particles
4. DRAW: Frame 1 = small bright core + glow
5. ANIMATE: Expand + fade. Core expands then fades, glow fades out.
6. TAG: set_tag(name="effect", direction="forward")
7. RULES: Transparent background, 40-80ms/frame, bright core/dim edges

VFX reference: Explosion (#ffffff→#ffcc00, 6-8f, 40-60ms), Fire (4-8f, 60-100ms), Magic (#41a6f6→#73eff7, 4-6f, 50-80ms), Heal (#a7f070→#38b764, 6-8f, 80-120ms), Slash (#ffffff, 3-4f, 30-50ms)

## When Designing Backgrounds
1. CONCEPT: Scene type, canvas size (≥240×135, wider for parallax), depth layers (2-5)
2. LAYERS (far to near): sky → mountains → midground → foreground → foreground_detail
3. DRAW (far to near): apply_gradient_rect for sky, draw_polygon for silhouettes
4. ANIMATE PARALLAX: Far layers move slowly, near layers move fast
5. RULES: Atmospheric perspective, layer separation, canvas wider than viewport

## When Designing Items
1. CONCEPT: Item type, size (16×16 or 24×24), palette (3-6 colors)
2. LAYERS: outline → base_color → shading → shine
3. DRAW: Outline → base fill → shading → shine highlight
4. ANIMATE: Float with oscillate_cel_positions(amplitude_y=1)
5. PALETTE SWAPS: copy_sprite → remap_colors_in_cel_range
6. RULES: Readability at 1x, distinct silhouette, color coding

Common shapes: Potion (rectangle+circle), Sword (rectangle+crossguard), Shield (circle), Gem (polygon), Coin (circle)

## When Adding Animation
1. ANALYZE: get_sprite_info() to understand current structure
2. ADD FRAMES: add_frames(count=N, duration=120)
3. CHOOSE TECHNIQUE: Idle breathing (tween_cel_positions_eased, ease_in_out), Walk (copy_frame + deltas), Attack (tween_cel_positions_eased, ease_in→ease_out), Float (oscillate_cel_positions, sine), Fade (tween_cel_opacity_eased), Parallax (tween_cel_positions, linear)
4. ENSURE CELS: ensure_layers_present() for all layers across all frames
5. TAG: set_tag() with appropriate direction
6. VALIDATE: audit_animation()

Timing: Idle 100-150ms/4f, Walk 80-120ms/8f, Run 60-80ms/6f, Attack 50-80ms/4-6f, Float 100-150ms/4-8f

## When Reviewing Assets
1. STRUCTURAL: validate_scene() — all layers exist, all frames have cels
2. PIXEL: get_pixels_rect() — compare against intent
3. ANIMATION: audit_animation() — overlaps, out-of-range, missing cels
4. NAMING: snake_case filenames, PascalCase layers, snake_case tags
5. FIX: Missing pixels→draw_pixels_at, Wrong colors→remap_colors_in_cel_range, Missing cels→ensure_layers_present, Misaligned→set_cel_position, Timing→set_frame_duration
6. REPORT: Status (PASS/NEEDS_FIXES), issues, fixes, re-verification

## When Exporting Assets
1. VALIDATE: validate_scene() + get_sprite_info() before export
2. EXPORT: export_sprite(format="png"|"gif") or spritesheet_export()
3. ORGANIZE: Follow directory convention
4. VERIFY: All exports exist and are non-empty
5. PREVIEW: start_preview_server(directory="generated_assets", port=8000)

Formats: Static→PNG, Animated character→PNG spritesheet+GIF, Tileset→PNG spritesheet, VFX→GIF+PNG spritesheet, Background→PNG

## When Orchestrating a Full Session
1. PLAN: Parse request into asset list with type/size/animation/dependencies
2. DELEGATE: Characters→Character workflow, Tiles→Tile workflow, VFX→VFX workflow, Backgrounds→Background workflow, Items→Item workflow, Animation→Animation workflow
3. PARALLEL: Independent assets simultaneously
4. SEQUENTIAL: Animation after base sprite, compositing after both assets, palette swaps after original reviewed
5. REVIEW: Each asset goes through Review workflow
6. FIX: Send fixes back to specialist or Review workflow
7. EXPORT: All assets go through Export workflow
