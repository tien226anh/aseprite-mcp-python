# Tool Reference Matrix

| Task | Best Tool(s) |
|------|-------------|
| Large flat area | `fill_area_at`, `draw_rectangle_at` (fill=True) |
| Sky / atmosphere | `apply_gradient_rect` |
| Character outline | `draw_pixels_at` + `draw_line_at` |
| Rounded shapes | `draw_circle_at`, `draw_polygon` |
| Irregular shapes | `draw_polygon` (fill=True) |
| Curves / paths | `draw_path` |
| Single-pixel details | `draw_pixels_at` |
| Symmetry | Draw half → `flip_layer` |
| Smooth motion | `tween_cel_positions_eased` |
| Oscillating motion | `oscillate_cel_positions` |
| Fade in/out | `tween_cel_opacity_eased` |
| Parallax scroll | `tween_cel_positions` (linear) per depth layer |
| Compositing assets | `copy_layers_between_sprites` |
| Positioning elements | `set_cel_position` |
| Verify pixels | `get_pixel_color`, `get_pixels_rect` |
| Verify structure | `validate_scene`, `audit_animation` |
| Fix missing cels | `ensure_layers_present` |
| Color swaps | `remap_colors_in_cel_range` |
| Resize / Crop | `resize_canvas`, `crop_canvas` |
| Rotate / Flip | `rotate_layer`, `flip_layer` |
