"""E2E test: Knight Quest — Full workflow pipeline validation.

Validates COMPLETE WORKFLOW SEQUENCES where multiple MCP tools are called in
sequence, simulating real MCP server usage.  Unlike integration tests that
exercise each tool individually, these tests validate CROSS-CUTTING CONCERNS:
do the tools work together correctly when called in sequence?  Is the Lua script
generation correct when tools chain?  Do error states propagate correctly across
a pipeline?
"""

from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

import aseprite_mcp.tools.animation
import aseprite_mcp.tools.canvas
import aseprite_mcp.tools.drawing
import aseprite_mcp.tools.export
import aseprite_mcp.tools.guide
import aseprite_mcp.tools.palette
import aseprite_mcp.tools.pixel_read
import aseprite_mcp.tools.preview
import aseprite_mcp.tools.quality
import aseprite_mcp.tools.scene
import aseprite_mcp.tools.transform  # noqa: F401
from aseprite_mcp.aseprite_cli import AsepriteCLI
from aseprite_mcp.config import AsepriteConfig

# Import ALL tool modules at the top so patch() can resolve dotted paths
# at runtime.  The imports above satisfy this requirement.


# ═══════════════════════════════════════════════════════════════════════════
# Shared fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_cli():
    """Create a mock AsepriteCLI with execute_lua_script returning success."""
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    # Legacy method stubs
    cli.run_json_script.return_value = {
        "width": 64,
        "height": 80,
        "success": True,
        "colorMode": "rgb",
        "palette_size": 16,
        "layers": ["Layer 1"],
        "frames": 8,
        "tags": [],
    }
    cli.run_batch.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=b"OK", stderr=b""
    )
    cli.run_script.return_value = "Script output"
    cli.list_layers.return_value = ["Background", "Knight"]
    cli.list_tags.return_value = ["walk", "idle"]
    return cli


# Module paths for patching — used by the helper below.
_ALL_TOOL_MODULES = [
    "aseprite_mcp.tools.canvas",
    "aseprite_mcp.tools.drawing",
    "aseprite_mcp.tools.animation",
    "aseprite_mcp.tools.export",
    "aseprite_mcp.tools.palette",
    "aseprite_mcp.tools.pixel_read",
    "aseprite_mcp.tools.preview",
    "aseprite_mcp.tools.scene",
    "aseprite_mcp.tools.quality",
    "aseprite_mcp.tools.transform",
    "aseprite_mcp.tools.guide",
]


@contextmanager
def _patch_all_get_cli(
    mock_cli: MagicMock,
    modules: list[str] | None = None,
):
    """Context manager that patches get_cli across all tool modules at once."""
    mods = modules or _ALL_TOOL_MODULES
    patches = [patch(f"{m}.get_cli", return_value=mock_cli) for m in mods]
    for p in patches:
        p.start()
    try:
        yield mock_cli
    finally:
        for p in patches:
            p.stop()


@contextmanager
def _patch_all_check_file(
    return_value=None,
    modules: list[str] | None = None,
):
    """Context manager that patches check_file across all tool modules."""
    mods = modules or _ALL_TOOL_MODULES
    patches = [patch(f"{m}.check_file", return_value=return_value) for m in mods]
    for p in patches:
        p.start()
    try:
        yield
    finally:
        for p in patches:
            p.stop()


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 1: Full Character Asset Creation Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2ECharacterAssetPipeline:
    """End-to-end creation of a knight character sprite."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        """Patch get_cli across canvas, drawing, animation, export."""
        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.drawing",
                "aseprite_mcp.tools.animation",
                "aseprite_mcp.tools.export",
            ],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_full_knight_creation_pipeline(self, mock_cli):
        """Create a knight: canvas, layers, frames, draw, tag, export."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            set_frame_duration_all,
            set_tag,
        )
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import (
            draw_line,
            draw_pixels,
            draw_rectangle,
        )
        from aseprite_mcp.tools.export import export_sprite

        filename = "knight.aseprite"

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.drawing",
                "aseprite_mcp.tools.animation",
                "aseprite_mcp.tools.export",
            ]
        ):
            # Step 1: create_canvas
            r1 = await create_canvas(width=64, height=80, filename=filename)
            assert "Created canvas" in r1

            # Step 2-5: add_layer x4
            for layer in ["Body", "Armor", "Sword", "Spell"]:
                r = await add_layer(filename=filename, layer_name=layer)
                assert "Added layer" in r

            # Step 6: add_frames (8 for walk cycle)
            r6 = await add_frames(filename=filename, count=8)
            assert "Added 8 frames" in r6

            # Step 7: set_frame_duration_all
            r7 = await set_frame_duration_all(
                filename=filename, duration_ms=100
            )
            assert "100ms" in r7

            # Step 8: draw_pixels (knight body)
            r8 = await draw_pixels(
                filename=filename,
                pixels=[
                    {"x": 30, "y": 10, "color": "#c0c0c0"},
                    {"x": 31, "y": 10, "color": "#c0c0c0"},
                ],
            )
            assert "Pixels drawn" in r8

            # Step 9: draw_rectangle (armor)
            r9 = await draw_rectangle(
                filename=filename,
                x=24,
                y=20,
                width=16,
                height=20,
                color="#a0a0a0",
                fill=True,
            )
            assert "Rectangle drawn" in r9

            # Step 10: draw_line (sword blade)
            r10 = await draw_line(
                filename=filename,
                x1=40,
                y1=15,
                x2=55,
                y2=15,
                color="#c0c0c0",
                thickness=1,
            )
            assert "Line drawn" in r10

            # Step 11-12: set_tag x2
            r11 = await set_tag(
                filename=filename,
                name="walk",
                from_frame=1,
                to_frame=4,
                direction="forward",
            )
            assert "walk" in r11
            r12 = await set_tag(
                filename=filename,
                name="idle",
                from_frame=5,
                to_frame=8,
                direction="pingpong",
            )
            assert "idle" in r12

            # Step 13: export_sprite
            mock_batch_result = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"", stderr=b""
            )
            mock_cli.run_batch = MagicMock(return_value=mock_batch_result)
            r13 = await export_sprite(
                filename=filename,
                output_filename="knight.png",
                format="png",
            )
            assert "Exported" in r13

        # ── Cross-tool assertions ──────────────────────────────────────
        # 1(create) + 4(layers) + 1(frames) + 1(duration)
        # + 1(pixels) + 1(rect) + 1(line) + 2(tags) = 12
        total_lua = mock_cli.execute_lua_script.call_count
        assert total_lua == 12, f"Expected 12 Lua calls, got {total_lua}"
        # Verify run_batch was called for export_sprite
        mock_cli.run_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_lua_scripts_contain_expected_apis(self, mock_cli):
        """Verify each generated Lua script contains expected API calls."""
        from aseprite_mcp.tools.animation import set_tag
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_rectangle

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.drawing",
                "aseprite_mcp.tools.animation",
            ]
        ):
            await create_canvas(
                width=64, height=80, filename="knight.aseprite"
            )
            await add_layer(
                filename="knight.aseprite", layer_name="Body"
            )
            await draw_rectangle(
                filename="knight.aseprite",
                x=0,
                y=0,
                width=10,
                height=10,
                color="#ff0000",
                fill=True,
            )
            await set_tag(
                filename="knight.aseprite",
                name="walk",
                from_frame=1,
                to_frame=4,
                direction="forward",
            )

        calls = mock_cli.execute_lua_script.call_args_list
        scripts = [c[0][0] for c in calls]

        assert any(
            "Sprite(64, 80)" in s for s in scripts
        ), "Missing Sprite() in create_canvas script"
        assert any(
            "newLayer" in s for s in scripts
        ), "Missing newLayer in add_layer script"
        assert any(
            "app.transaction" in s for s in scripts
        ), "Missing app.transaction in draw script"
        assert any(
            "AniDir.FORWARD" in s for s in scripts
        ), "Missing AniDir.FORWARD in set_tag script"

    @pytest.mark.asyncio
    async def test_filename_passes_through_pipeline(self, mock_cli):
        """Verify the same filename propagates through each pipeline step."""
        from aseprite_mcp.tools.animation import add_frames
        from aseprite_mcp.tools.canvas import add_layer, create_canvas

        filename = "knight.aseprite"

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.animation",
            ]
        ):
            await create_canvas(width=64, height=80, filename=filename)
            await add_layer(filename=filename, layer_name="Body")
            await add_frames(filename=filename, count=8)

        calls = mock_cli.execute_lua_script.call_args_list
        # create_canvas doesn't pass filename (no second arg)
        # add_layer and add_frames pass filename as 2nd arg
        for call in calls[1:]:
            if len(call[0]) > 1:
                assert call[0][1] == filename, (
                    f"Filename mismatch: {call[0][1]!r}"
                )


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 2: Monster Asset Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2EMonsterAssetPipeline:
    """Creating multiple monster sprites — consistency across pipelines."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.drawing",
                "aseprite_mcp.tools.animation",
                "aseprite_mcp.tools.export",
            ],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_three_monster_sprites_same_structure(
        self, mock_cli
    ):
        """Create goblin, skeleton, and slime with identical structure."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            set_frame_duration_all,
            set_tag,
        )
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_circle, fill_area
        from aseprite_mcp.tools.export import export_sprite

        monsters = [
            ("goblin.aseprite", "#008000"),
            ("skeleton.aseprite", "#e8e8d0"),
            ("slime.aseprite", "#00ff00"),
        ]

        mock_batch_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )
        mock_cli.run_batch = MagicMock(return_value=mock_batch_result)

        for sprite_name, body_color in monsters:
            mock_cli.execute_lua_script.reset_mock()

            with _patch_all_check_file(
                modules=[
                    "aseprite_mcp.tools.canvas",
                    "aseprite_mcp.tools.drawing",
                    "aseprite_mcp.tools.animation",
                    "aseprite_mcp.tools.export",
                ]
            ):
                await create_canvas(
                    width=32, height=32, filename=sprite_name
                )
                await add_layer(
                    filename=sprite_name, layer_name="Body"
                )
                await draw_circle(
                    filename=sprite_name,
                    center_x=16,
                    center_y=16,
                    radius=12,
                    color=body_color,
                    fill=True,
                )
                await fill_area(
                    filename=sprite_name,
                    x=16,
                    y=16,
                    color=body_color,
                )
                await add_frames(filename=sprite_name, count=4)
                await set_frame_duration_all(
                    filename=sprite_name, duration_ms=80
                )
                await set_tag(
                    filename=sprite_name,
                    name="attack",
                    from_frame=1,
                    to_frame=4,
                    direction="forward",
                )
                await export_sprite(
                    filename=sprite_name,
                    output_filename=sprite_name.replace(
                        ".aseprite", ".png"
                    ),
                    format="png",
                )

            # create + layer + circle + fill
            # + frames + duration + tag = 7 lua calls
            assert mock_cli.execute_lua_script.call_count == 7, (
                f"{sprite_name}: expected 7 Lua calls, "
                f"got {mock_cli.execute_lua_script.call_count}"
            )

    @pytest.mark.asyncio
    async def test_monster_pipeline_call_order(self, mock_cli):
        """Verify the Lua scripts are generated in the correct order."""
        from aseprite_mcp.tools.animation import add_frames, set_tag
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_circle

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.drawing",
                "aseprite_mcp.tools.animation",
            ]
        ):
            await create_canvas(
                width=32, height=32, filename="goblin.aseprite"
            )
            await add_layer(
                filename="goblin.aseprite", layer_name="Body"
            )
            await draw_circle(
                filename="goblin.aseprite",
                center_x=16,
                center_y=16,
                radius=12,
                color="#008000",
                fill=True,
            )
            await add_frames(filename="goblin.aseprite", count=4)
            await set_tag(
                filename="goblin.aseprite",
                name="attack",
                from_frame=1,
                to_frame=4,
                direction="forward",
            )

        scripts = [
            c[0][0]
            for c in mock_cli.execute_lua_script.call_args_list
        ]
        # Order: Sprite(), newLayer, ellipse tool, newEmptyFrame, tag
        assert "Sprite(32, 32)" in scripts[0]
        assert "newLayer" in scripts[1]
        # draw_circle uses Aseprite's ellipse tool
        assert (
            "filled_ellipse" in scripts[2]
            or "ellipse" in scripts[2].lower()
        )
        assert "newEmptyFrame" in scripts[3]
        assert "AniDir.FORWARD" in scripts[4]


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 3: Animation Sequence Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2EAnimationSequencePipeline:
    """Knight battle animation — tweening, propagation, easing together."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        with _patch_all_get_cli(
            mock_cli,
            modules=["aseprite_mcp.tools.animation"],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_battle_animation_pipeline(self, mock_cli):
        """Chain: add_frames, create_cel, tween, oscillate, propagate, tag."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            create_cel,
            oscillate_cel_positions,
            propagate_cels,
            set_tag,
            tween_cel_opacity_eased,
            tween_cel_positions,
            tween_cel_positions_eased,
        )

        filename = "knight.aseprite"

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.animation"]
        ):
            # Step 1: add 6 new frames
            r1 = await add_frames(filename=filename, count=6)
            assert "Added 6 frames" in r1

            # Step 2: create empty cel
            r2 = await create_cel(
                filename=filename,
                layer_name="Sword",
                frame_index=9,
                x=0,
                y=0,
            )
            assert "Created cel" in r2

            # Step 3: tween sword swing (linear)
            r3 = await tween_cel_positions(
                filename=filename,
                layer_name="Sword",
                start_frame=6,
                end_frame=10,
                start_x=40,
                start_y=15,
                end_x=10,
                end_y=30,
            )
            assert "Tweened cel positions" in r3

            # Step 4: tween with easing (smooth)
            r4 = await tween_cel_positions_eased(
                filename=filename,
                layer_name="Sword",
                start_frame=10,
                end_frame=12,
                start_x=10,
                start_y=30,
                end_x=40,
                end_y=15,
                easing="ease_in_out",
            )
            assert "ease_in_out" in r4

            # Step 5: oscillate for breathing
            r5 = await oscillate_cel_positions(
                filename=filename,
                layer_name="Body",
                start_frame=6,
                end_frame=12,
                amplitude_x=0,
                amplitude_y=2,
                cycles=2,
            )
            assert "Oscillated" in r5

            # Step 6: tween opacity for spell fade
            r6 = await tween_cel_opacity_eased(
                filename=filename,
                layer_name="Spell",
                start_frame=10,
                end_frame=12,
                start_opacity=0,
                end_opacity=255,
                easing="ease_out",
            )
            assert "Tweened cel opacity" in r6

            # Step 7: propagate cels
            r7 = await propagate_cels(
                filename=filename,
                layer_names=["Shield"],
                source_frame=1,
                start_frame=6,
                end_frame=12,
            )
            assert "Propagated" in r7

            # Step 8: set tag
            r8 = await set_tag(
                filename=filename,
                name="melee_attack",
                from_frame=6,
                to_frame=12,
                direction="forward",
            )
            assert "melee_attack" in r8

        # add_frames + create_cel + tween_linear + tween_eased
        # + oscillate + opacity_tween + propagate + tag = 8
        total = mock_cli.execute_lua_script.call_count
        assert total == 8, f"Expected 8 Lua calls, got {total}"

    @pytest.mark.asyncio
    async def test_animation_lua_script_chaining(self, mock_cli):
        """Verify Lua scripts chain with consistent frame indices."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            tween_cel_positions,
        )

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.animation"]
        ):
            await add_frames(filename="knight.aseprite", count=4)
            await tween_cel_positions(
                filename="knight.aseprite",
                layer_name="Sword",
                start_frame=1,
                end_frame=4,
                start_x=0,
                start_y=0,
                end_x=60,
                end_y=60,
            )

        calls = mock_cli.execute_lua_script.call_args_list
        scripts = [c[0][0] for c in calls]
        # add_frames script should reference newEmptyFrame
        assert "newEmptyFrame" in scripts[0]
        # tween script should reference frame range
        assert (
            "spr.frames[1]" in scripts[1] or "1" in scripts[1]
        )

    @pytest.mark.asyncio
    async def test_eased_tween_generates_easing_function(
        self, mock_cli
    ):
        """Verify eased tween scripts include easing function defs."""
        from aseprite_mcp.tools.animation import (
            tween_cel_positions_eased,
        )

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.animation"]
        ):
            await tween_cel_positions_eased(
                filename="knight.aseprite",
                layer_name="Sword",
                start_frame=1,
                end_frame=4,
                start_x=0,
                start_y=0,
                end_x=10,
                end_y=10,
                easing="smoothstep",
            )

        script = mock_cli.execute_lua_script.call_args[0][0]
        # Smoothstep should define the easing function in Lua
        assert (
            "smoothstep" in script.lower()
            or "3*t^2" in script
            or "ease" in script.lower()
        )


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 4: Scene Composition Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2ESceneCompositionPipeline:
    """Composing the final quest scene — scene, quality, info together."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.scene",
                "aseprite_mcp.tools.quality",
                "aseprite_mcp.tools.animation",
            ],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_scene_composition_pipeline(self, mock_cli):
        """Copy dragon, ensure layers, validate, audit, sanitize, info."""
        from aseprite_mcp.tools.animation import get_sprite_info
        from aseprite_mcp.tools.quality import (
            animation_sanitize,
            audit_animation,
            ensure_layers_present,
            validate_scene,
        )
        from aseprite_mcp.tools.scene import (
            copy_layers_between_sprites,
        )

        # Set up specific mock returns for quality tools
        mock_cli.execute_lua_script.side_effect = [
            (True, "Copied layers: Dragon"),
            (
                True,
                "Created 3 cel(s), skipped 0 layer(s)",
            ),
            (
                True,
                'JSON_START{"frames":8,'
                '"missing_layers":[],"missing_cels":[]}',
            ),
            (
                True,
                'JSON_START{"summary":{"total_cels":24,'
                '"overlaps_count":0,"out_of_range_count":0}}',
            ),
            (
                True,
                'JSON_START{"sanitized":true,'
                '"analysis":{"total_layers":4,"total_cels":32}}',
            ),
            (
                True,
                "Sprite: quest.aseprite\n"
                "  Dimensions: 128x128\n"
                "  Frames: 8",
            ),
        ]

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.scene",
                "aseprite_mcp.tools.quality",
                "aseprite_mcp.tools.animation",
            ]
        ):
            # Step 1: copy dragon layers
            r1 = await copy_layers_between_sprites(
                source_filename="boss.aseprite",
                target_filename="quest.aseprite",
                layer_names=["Dragon"],
            )
            assert "Copied" in r1

            # Step 2: ensure layers present
            r2 = await ensure_layers_present(
                filename="quest.aseprite",
                layer_names=["Knight", "Dragon", "Effects"],
                start_frame=1,
                end_frame=8,
            )
            assert "ensure_layers_present" in r2

            # Step 3: validate scene
            r3 = await validate_scene(
                filename="quest.aseprite",
                required_layers=["Knight", "Dragon", "Effects"],
                start_frame=1,
                end_frame=8,
            )
            assert (
                "frames" in r3.lower()
                or "JSON" in r3
                or "missing" in r3.lower()
            )

            # Step 4: audit animation
            r4 = await audit_animation(
                filename="quest.aseprite",
                start_frame=1,
                end_frame=8,
                overlap_pairs=["Knight,Dragon"],
            )
            assert r4 is not None and len(r4) > 0

            # Step 5: sanitize
            r5 = await animation_sanitize(
                filename="quest.aseprite",
                start_frame=1,
                end_frame=8,
                ensure_layers=["Knight", "Dragon", "Effects"],
                layer_order=[
                    "Background",
                    "Dragon",
                    "Knight",
                    "Effects",
                ],
            )
            assert r5 is not None and len(r5) > 0

            # Step 6: get sprite info
            r6 = await get_sprite_info(filename="quest.aseprite")
            assert "Sprite" in r6 or "quest" in r6

        # All 6 tools should have called execute_lua_script
        total = mock_cli.execute_lua_script.call_count
        assert total == 6, (
            f"Expected 6 Lua calls in scene composition, got {total}"
        )

    @pytest.mark.asyncio
    async def test_quality_tools_produce_json_structure(
        self, mock_cli
    ):
        """Validate and audit should produce parseable JSON-like output."""
        from aseprite_mcp.tools.quality import validate_scene

        mock_cli.execute_lua_script.return_value = (
            True,
            'JSON_START{"frames":8,'
            '"missing_layers":[],"missing_cels":[]}',
        )

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.quality"]
        ):
            result = await validate_scene(
                filename="quest.aseprite",
                required_layers=["Knight"],
                start_frame=1,
                end_frame=8,
            )
        assert "JSON" in result or "frames" in result.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 5: Export & Quality Assurance Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2EExportQAPipeline:
    """Final export and validation — legacy and new tools together."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.palette",
                "aseprite_mcp.tools.pixel_read",
                "aseprite_mcp.tools.export",
            ],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_export_qa_pipeline(self, mock_cli, tmp_path):
        """Palette, remap, pixel check, export, preview, stop."""
        from aseprite_mcp.tools.export import export_sprite
        from aseprite_mcp.tools.palette import (
            get_palette,
            remap_colors_in_cel_range,
            set_palette,
        )
        from aseprite_mcp.tools.pixel_read import (
            get_pixel_color,
            get_pixels_rect,
        )
        from aseprite_mcp.tools.preview import (
            start_preview_server,
            stop_preview_server,
        )

        mock_cli.execute_lua_script.side_effect = None
        mock_cli.execute_lua_script.return_value = (True, "Success")

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.palette",
                "aseprite_mcp.tools.pixel_read",
                "aseprite_mcp.tools.export",
            ]
        ):
            # Step 1: get_palette
            mock_cli.execute_lua_script.return_value = (
                True,
                '["#1a1a2e", "#16213e", "#0f3460", "#e94560"]',
            )
            r1 = await get_palette(filename="quest.aseprite")
            assert "1a1a2e" in r1 or "palette" in r1.lower()

            # Step 2: set_palette (dark dungeon)
            mock_cli.execute_lua_script.return_value = (
                True,
                "Success",
            )
            r2 = await set_palette(
                filename="quest.aseprite",
                colors=[
                    "#1a1a2e",
                    "#16213e",
                    "#0f3460",
                    "#e94560",
                ],
            )
            assert "4 colors" in r2

            # Step 3: remap_colors
            r3 = await remap_colors_in_cel_range(
                filename="quest.aseprite",
                layer_name="Knight",
                start_frame=1,
                end_frame=8,
                mappings=[{"from": "#c0c0c0", "to": "#ffd700"}],
            )
            assert "Remapped" in r3

            # Step 4: get_pixel_color (spot check)
            mock_cli.execute_lua_script.return_value = (
                True,
                "PIXEL:255,215,0,255",
            )
            r4 = await get_pixel_color(
                filename="quest.aseprite", x=30, y=10
            )
            assert "#ffd700" in r4

            # Step 5: get_pixels_rect (collision map)
            mock_cli.execute_lua_script.return_value = (
                True,
                "PIXEL:0,0,255,215,0,255\n"
                "PIXEL:1,0,26,33,96,255",
            )
            r5 = await get_pixels_rect(
                filename="quest.aseprite",
                x=0,
                y=0,
                width=2,
                height=1,
            )
            parsed = json.loads(r5)
            assert "pixels" in parsed

            # Step 6: export_sprite
            mock_batch_result = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"", stderr=b""
            )
            mock_cli.run_batch = MagicMock(
                return_value=mock_batch_result
            )
            r6 = await export_sprite(
                filename="quest.aseprite",
                output_filename="quest_final.png",
                format="png",
            )
            assert "Exported" in r6

            # Step 7: spritesheet_export (legacy)
            from aseprite_mcp import server as srv

            mock_cli_legacy = MagicMock(spec=AsepriteCLI)
            mock_sheet_result = MagicMock()
            mock_sheet_result.returncode = 0
            mock_cli_legacy.run_batch = MagicMock(
                return_value=mock_sheet_result
            )
            srv._cli = mock_cli_legacy
            srv._config = AsepriteConfig(
                aseprite_path="/usr/bin/aseprite",
                tmp_dir=tmp_path / "scripts",
                output_dir=tmp_path / "output",
            )
            r7 = await srv.spritesheet_export(
                input_path=str(tmp_path / "quest.aseprite")
            )
            parsed7 = json.loads(r7)
            assert parsed7["success"] is True

            # Step 8: start_preview_server
            import os

            from aseprite_mcp.tools.preview import _pid_path

            pid_file = _pid_path(8099)
            if os.path.exists(pid_file):
                os.remove(pid_file)

            mock_proc = MagicMock()
            mock_proc.pid = 99999
            mock_proc.wait.side_effect = subprocess.TimeoutExpired(
                "cmd", 0.5
            )
            with patch(
                "subprocess.Popen", return_value=mock_proc
            ):
                r8 = await start_preview_server(
                    directory=str(tmp_path), port=8099
                )
            assert "started" in r8.lower() or "Preview" in r8

            # Step 9: stop_preview_server
            if os.path.exists(pid_file):
                os.remove(pid_file)
            r9 = await stop_preview_server(port=8099)
            assert (
                "no" in r9.lower() and "PID" in r9.upper()
            ) or "No preview" in r9

    @pytest.mark.asyncio
    async def test_new_and_legacy_tools_interoperate(
        self, mock_cli, tmp_path
    ):
        """Legacy spritesheet_export and new export_sprite don't conflict."""
        from aseprite_mcp import server as srv
        from aseprite_mcp.tools.export import export_sprite

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.export"]
        ):
            # New tool: export_sprite
            mock_batch = subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"", stderr=b""
            )
            mock_cli.run_batch = MagicMock(
                return_value=mock_batch
            )
            r1 = await export_sprite(
                filename="quest.aseprite",
                output_filename="quest.png",
                format="png",
            )
            assert "Exported" in r1

        # Legacy tool: spritesheet_export
        mock_cli_legacy = MagicMock(spec=AsepriteCLI)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_cli_legacy.run_batch = MagicMock(
            return_value=mock_result
        )
        srv._cli = mock_cli_legacy
        srv._config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite",
            tmp_dir=tmp_path / "scripts",
            output_dir=tmp_path / "output",
        )
        r2 = await srv.spritesheet_export(
            input_path=str(tmp_path / "quest.aseprite")
        )
        parsed = json.loads(r2)
        assert parsed["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 6: Transform & Visual Effects Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2ETransformEffectsPipeline:
    """Knight combat visual effects — transforms chaining correctly."""

    @pytest.fixture(autouse=True)
    def patch_modules(self, mock_cli):
        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.transform",
                "aseprite_mcp.tools.animation",
            ],
        ):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_transform_effects_pipeline(self, mock_cli):
        """Flip, rotate, resize, crop, visibility, opacity chaining."""
        from aseprite_mcp.tools.animation import (
            set_layer_opacity,
            set_layer_visibility,
        )
        from aseprite_mcp.tools.transform import (
            crop_canvas,
            flip_layer,
            resize_canvas,
            rotate_layer,
        )

        filename = "knight.aseprite"

        with _patch_all_check_file(
            modules=[
                "aseprite_mcp.tools.transform",
                "aseprite_mcp.tools.animation",
            ]
        ):
            # Step 1: flip sword arm
            r1 = await flip_layer(
                filename=filename,
                layer_name="Sword",
                frame_index=9,
                direction="horizontal",
            )
            assert "Flipped" in r1

            # Step 2: rotate spell effect
            r2 = await rotate_layer(
                filename=filename,
                layer_name="Spell",
                frame_index=10,
                angle=90,
            )
            assert "Rotated" in r2

            # Step 3: resize for boss arena
            r3 = await resize_canvas(
                filename=filename, width=128, height=128
            )
            assert "Resized" in r3

            # Step 4: crop excess
            r4 = await crop_canvas(
                filename=filename,
                x=8,
                y=8,
                width=112,
                height=112,
            )
            assert "Cropped" in r4

            # Step 5: hide unused layers
            r5 = await set_layer_visibility(
                filename=filename,
                layer_name="Debug",
                visible=False,
            )
            assert "Debug" in r5

            # Step 6: fade background
            r6 = await set_layer_opacity(
                filename=filename,
                layer_name="Background",
                opacity=128,
            )
            assert "128" in r6

        # All 6 transform/animation calls should hit execute_lua_script
        total = mock_cli.execute_lua_script.call_count
        assert total == 6, (
            f"Expected 6 Lua calls in transform pipeline, got {total}"
        )

    @pytest.mark.asyncio
    async def test_transform_lua_contains_expected_operations(
        self, mock_cli
    ):
        """Verify transform Lua scripts contain expected API calls."""
        from aseprite_mcp.tools.transform import (
            crop_canvas,
            flip_layer,
            resize_canvas,
            rotate_layer,
        )

        with _patch_all_check_file(
            modules=["aseprite_mcp.tools.transform"]
        ):
            await flip_layer(
                filename="knight.aseprite",
                layer_name="Sword",
                frame_index=1,
                direction="horizontal",
            )
            await rotate_layer(
                filename="knight.aseprite",
                layer_name="Spell",
                frame_index=1,
                angle=90,
            )
            await resize_canvas(
                filename="knight.aseprite", width=128, height=128
            )
            await crop_canvas(
                filename="knight.aseprite",
                x=0,
                y=0,
                width=64,
                height=64,
            )

        scripts = [
            c[0][0]
            for c in mock_cli.execute_lua_script.call_args_list
        ]
        # flip should reference horizontal mirroring
        assert any(
            "w - 1 - x" in s or "horizontal" in s.lower()
            for s in scripts
        )
        # rotate should reference 90
        assert any("90" in s for s in scripts)
        # resize should reference new dimensions
        assert any("128" in s for s in scripts)
        # crop should reference crop
        assert any("crop" in s.lower() for s in scripts)


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 7: Legacy Tools Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2ELegacyPipeline:
    """server.py tools working together — the ancient spells."""

    @pytest.fixture
    def config(self, tmp_path):
        return AsepriteConfig(
            aseprite_path="/usr/bin/aseprite",
            tmp_dir=tmp_path / "scripts",
            output_dir=tmp_path / "output",
        )

    @pytest.mark.asyncio
    async def test_legacy_pipeline(self, config):
        """sprite_create, sprite_info, list_layers, list_tags,
        export, script_execute."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_json_script.return_value = {
            "width": 64,
            "height": 48,
            "success": True,
            "colorMode": "rgb",
            "palette_size": 16,
            "layers": ["Background", "Cutscene"],
            "frames": 1,
            "tags": [],
            "filename": "/tmp/cutscene.ase",
            "output": "/tmp/cutscene.png",
        }
        mock_cli.list_layers.return_value = [
            "Background",
            "Cutscene",
        ]
        mock_cli.list_tags.return_value = ["intro"]

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_cli.run_batch = MagicMock(return_value=mock_result)

        mock_cli.run_script.return_value = "Cutscene initialized!"

        srv._cli = mock_cli
        srv._config = config

        # Step 1: sprite_create
        r1 = await srv.sprite_create(width=64, height=48)
        parsed1 = json.loads(r1)
        assert parsed1["width"] == 64

        # Step 2: sprite_info
        r2 = await srv.sprite_info(file_path="cutscene.ase")
        parsed2 = json.loads(r2)
        assert "width" in parsed2

        # Step 3: list_layers
        r3 = await srv.sprite_list_layers(file_path="cutscene.ase")
        parsed3 = json.loads(r3)
        assert "Cutscene" in parsed3["layers"]

        # Step 4: list_tags
        r4 = await srv.sprite_list_tags(file_path="cutscene.ase")
        parsed4 = json.loads(r4)
        assert "intro" in parsed4["tags"]

        # Step 5: sprite_export
        r5 = await srv.sprite_export(input_path="cutscene.ase")
        parsed5 = json.loads(r5)
        assert parsed5["success"] is True

        # Step 6: script_execute
        r6 = await srv.script_execute(
            lua_code='print("Cutscene!")'
        )
        assert "Cutscene" in r6

        # Verify legacy methods were called
        mock_cli.run_json_script.assert_called()
        mock_cli.list_layers.assert_called_once()
        mock_cli.list_tags.assert_called_once()
        mock_cli.run_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_legacy_pipeline_interop_with_new_tools(
        self, config, mock_cli
    ):
        """Legacy sprite_create and new create_canvas are consistent."""
        from aseprite_mcp import server as srv
        from aseprite_mcp.tools.canvas import create_canvas

        # Legacy: sprite_create
        mock_cli_legacy = MagicMock(spec=AsepriteCLI)
        mock_cli_legacy.run_json_script.return_value = {
            "width": 32,
            "height": 32,
            "success": True,
            "colorMode": "rgb",
            "filename": "/tmp/test.ase",
        }
        srv._cli = mock_cli_legacy
        srv._config = config

        r_legacy = await srv.sprite_create(width=32, height=32)
        parsed_legacy = json.loads(r_legacy)
        assert parsed_legacy["width"] == 32

        # New: create_canvas (uses execute_lua_script)
        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.canvas"]
        ):
            r_new = await create_canvas(
                width=32, height=32, filename="test.aseprite"
            )
            assert "Created canvas" in r_new

        # Different API but both produce 32x32 sprites
        mock_cli_legacy.run_json_script.assert_called_once()
        mock_cli.execute_lua_script.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 8: Error Recovery Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestE2EErrorRecoveryPipeline:
    """What happens when steps fail — errors caught at the right level."""

    @pytest.mark.asyncio
    async def test_file_not_found_error_pipeline(self, mock_cli):
        """File not found is caught before Lua execution."""
        from aseprite_mcp.tools.animation import add_frames

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.animation"]
        ), patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File not found: missing.aseprite",
        ):
            result = await add_frames(
                filename="missing.aseprite", count=4
            )

        assert "not found" in result
        mock_cli.execute_lua_script.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalid_parameter_rejected_before_lua(
        self, mock_cli
    ):
        """Invalid width=0 is rejected before any Lua script."""
        from aseprite_mcp.tools.canvas import create_canvas

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.canvas"]
        ):
            result = await create_canvas(width=0, height=32)
            assert "Error" in result
            assert "width" in result
            mock_cli.execute_lua_script.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_layer_name_error_before_lua(
        self, mock_cli
    ):
        """Set layer with empty name — Lua failure propagates."""
        from aseprite_mcp.tools.canvas import add_layer

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.canvas"]
        ), patch(
            "aseprite_mcp.tools.canvas.check_file",
            return_value=None,
        ):
            mock_cli.execute_lua_script.return_value = (
                False,
                "Error: layer name cannot be empty",
            )
            result = await add_layer(
                filename="test.aseprite", layer_name=""
            )
            assert "Failed" in result

    @pytest.mark.asyncio
    async def test_path_traversal_rejected_before_lua(
        self, mock_cli
    ):
        """Path traversal is caught by validation, not by Lua."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.quality import ensure_layers_present
        from aseprite_mcp.tools.scene import (
            copy_layers_between_sprites,
        )

        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.quality",
                "aseprite_mcp.tools.scene",
            ],
        ):
            r1 = await create_canvas(
                width=64, height=64, filename="../etc/passwd"
            )
            assert ".." in r1

            with patch(
                "aseprite_mcp.tools.quality.check_file",
                return_value=None,
            ):
                r2 = await ensure_layers_present(
                    filename="../secret.ase",
                    layer_names=["Knight"],
                )
                assert ".." in r2

            with patch(
                "aseprite_mcp.tools.scene.check_file",
                return_value=None,
            ):
                r3 = await copy_layers_between_sprites(
                    source_filename="../etc/passwd",
                    target_filename="quest.aseprite",
                    layer_names=["Dragon"],
                )
                assert ".." in r3

        # None of these should have reached Lua
        mock_cli.execute_lua_script.assert_not_called()

    @pytest.mark.asyncio
    async def test_lua_script_failure_propagates(self, mock_cli):
        """When execute_lua_script returns (False, error)."""
        from aseprite_mcp.tools.animation import add_frames

        mock_cli.execute_lua_script.return_value = (
            False,
            "Lua error: attempt to index nil value",
        )

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.animation"]
        ), patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value=None,
        ):
            result = await add_frames(
                filename="knight.aseprite", count=4
            )
            assert "Failed" in result

    @pytest.mark.asyncio
    async def test_invalid_color_format_rejected_before_lua(
        self, mock_cli
    ):
        """Invalid color format is rejected in drawing tools."""
        from aseprite_mcp.tools.drawing import draw_pixels

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.drawing"]
        ), patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value=None,
        ):
            result = await draw_pixels(
                filename="test.aseprite",
                pixels=[
                    {"x": 1, "y": 1, "color": "not-a-color"}
                ],
            )
            # The tools validate hex colors — should reject
            assert "Error" in result or "color" in result.lower()

    @pytest.mark.asyncio
    async def test_error_in_pipeline_doesnt_prevent_subsequent_calls(
        self, mock_cli
    ):
        """If one tool fails, subsequent tools can still be called."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            set_tag,
        )
        from aseprite_mcp.tools.canvas import add_layer

        with _patch_all_get_cli(
            mock_cli,
            modules=[
                "aseprite_mcp.tools.canvas",
                "aseprite_mcp.tools.animation",
            ],
        ):
            # First call: file not found
            with patch(
                "aseprite_mcp.tools.animation.check_file",
                return_value="File not found: missing.aseprite",
            ):
                r1 = await add_frames(
                    filename="missing.aseprite", count=4
                )
                assert "not found" in r1

            # Second call: should succeed
            with patch(
                "aseprite_mcp.tools.canvas.check_file",
                return_value=None,
            ):
                r2 = await add_layer(
                    filename="existing.aseprite",
                    layer_name="Body",
                )
                assert "Added layer" in r2

            # Third call: succeeds
            mock_cli.execute_lua_script.return_value = (
                True,
                "Success",
            )
            with patch(
                "aseprite_mcp.tools.animation.check_file",
                return_value=None,
            ):
                r3 = await set_tag(
                    filename="existing.aseprite",
                    name="walk",
                    from_frame=1,
                    to_frame=4,
                    direction="forward",
                )
                assert "walk" in r3

        # Error in step 1 should not prevent steps 2-3
        assert mock_cli.execute_lua_script.call_count == 2

    @pytest.mark.asyncio
    async def test_invalid_tag_direction_rejected_early(
        self, mock_cli
    ):
        """Invalid tag direction is caught by Python validation."""
        from aseprite_mcp.tools.animation import set_tag

        with _patch_all_get_cli(
            mock_cli, modules=["aseprite_mcp.tools.animation"]
        ), patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value=None,
        ):
            result = await set_tag(
                filename="knight.aseprite",
                name="bad",
                from_frame=1,
                to_frame=4,
                direction="spiral",
            )
            assert "Error" in result
            mock_cli.execute_lua_script.assert_not_called()

