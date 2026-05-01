"""Guide tools for Aseprite MCP — animation workflow guidance."""

from __future__ import annotations

from aseprite_mcp import mcp

_CHARACTER_GUIDE = """\
Character Animation Workflow Guide
===================================

1. **Plan the character sheet** — Decide on the character's dimensions (e.g. 16×16, 32×32, 64×64) and create a new sprite with `create_canvas`. Keep the palette limited to 4–8 colors for readability.

2. **Create a base layer** — Use `add_layer` for the character outline or silhouette. Work in a separate layer so you can iterate on the shape without losing detail work.

3. **Add a color/shading layer** — Create a second layer below the outline for flat colors and shading. Use at least three values per hue (highlight, midtone, shadow) for depth.

4. **Set up animation frames** — Use `add_frame` and `set_frame_duration` to build the animation timeline. Start with keyframes (most extreme poses), then add inbetweens.

5. **Animate on twos** — For smooth 2D character animation, hold each drawing for 2 frames (~120 ms at 60 fps). Set frame durations accordingly with `set_frame_duration`.

6. **Use onion skinning** — In Aseprite, enable onion skinning (View → Onion Skin) to see adjacent frames while editing. This helps maintain consistent volume and motion arcs.

7. **Iterate and refine** — After roughing out the full animation, go back and polish timing and spacing. Shorter holds = faster action; longer holds = weight and emphasis.

8. **Export for preview** — Use `sprite_export` to save as GIF for quick feedback, or `spritesheet_export` for a full spritesheet with JSON metadata for game engines.
"""

_ENVIRONMENT_GUIDE = """\
Environment Animation Workflow Guide
====================================

1. **Define the scene dimensions** — Create a canvas sized to your target resolution (e.g. 256×144 for a handheld, 480×270 for HD). Use `create_canvas` to set up the sprite.

2. **Build the background layer** — Paint the static portion of the scene (sky, ground, distant objects) on a locked background layer. This won't change frame-to-frame.

3. **Add parallax layers** — Create separate layers for foreground, midground, and background elements that will scroll at different speeds. Use `add_layer` for each depth plane.

4. **Mark animated elements** — Use `add_frame` for each step of the environment animation (e.g. water ripple, swaying grass, flickering torch). Keep cycle lengths short (4–8 frames) for seamless loops.

5. **Set frame durations** — Environmental animations often use varying durations. Slow drifts = 200–300 ms per frame; quick flickers = 30–60 ms. Use `set_frame_duration` per frame.

6. **Use tags for sections** — Organize your timeline with tags naming each animated element (e.g. "water_cycle", "torch_flicker"). This makes editing individual loops easier.

7. **Export as spritesheet** — Use `spritesheet_export` with sheet_type="rows" so each tagged animation gets its own row in the atlas, and include the JSON data for game-engine integration.
"""

_DEFAULT_GUIDE = """\
Animation Workflow Guide
========================

1. **Set up your sprite** — Use `create_canvas` to create a new file at your target resolution. Named layers and clear naming conventions pay off quickly.

2. **Work in layers** — Keep outlines, fills, and shading on separate layers so you can edit each independently. Use `add_layer` and `set_layer` to manage them.

3. **Build the timeline** — Use `add_frame` for each step of your animation. Set durations with `set_frame_duration` to control timing.

4. **Draft keyframes first** — Put your most important poses on keyframe positions, then fill inbetweens. This ensures strong silhouettes and readable motion.

5. **Preview and iterate** — Use Aseprite's Play button or export to GIF with `sprite_export` to review the animation. Tighten timing, fix pops, and smooth arcs.

6. **Export for your pipeline** — Use `spritesheet_export` for game engines (PNG + JSON atlas), or `sprite_export` for simple GIF/PNG outputs. Keep source `.aseprite` files for future edits.
"""


@mcp.tool()
async def animation_workflow_guide(use_case: str = "character") -> str:
    """Return a text guide for pixel-art animation workflows in Aseprite.

    This is a pure-text tool — it does not interact with Aseprite.

    Args:
        use_case: The type of animation workflow guide to return.
            Options: "character" for character animation,
            "environment" for environment/scene animation,
            or any other value for a general guide.
    """
    if use_case == "character":
        return _CHARACTER_GUIDE
    if use_case == "environment":
        return _ENVIRONMENT_GUIDE
    return _DEFAULT_GUIDE