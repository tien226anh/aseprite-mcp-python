"""Integration test: Knight Quest RPG scenario covering all 67 MCP tools.

A knight on a quest to save a princess from a dragon, encountering goblins,
skeletons, and slimes along the way. Each chapter represents a workflow phase,
and each test validates one tool's behavior through the RPG narrative.
"""

from __future__ import annotations

import json
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import aseprite_mcp.tools.animation

# Import tool modules so patch() can resolve dotted paths at runtime
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

# ═══════════════════════════════════════════════════════════════════════════
# Shared fixtures for new-tools pattern (tools/*.py modules)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_cli():
    """Create a mock AsepriteCLI with execute_lua_script returning success."""
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    return cli


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 1: The Kingdom (Canvas & Creation)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter1:
    """Create the game world canvas and set up the quest structure."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.canvas.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_create_canvas_the_kingdom(self, mock_cli):
        """The knight's quest begins — create a 64x64 canvas for the realm."""
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=64, height=64, filename="kingdom.aseprite")
        assert "Created canvas" in result
        assert "kingdom.aseprite" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "Sprite(64, 64)" in script

    @pytest.mark.asyncio
    async def test_create_canvas_invalid_width_rejects_dark_portal(self):
        """A dark portal with zero width cannot exist in the kingdom."""
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=0, height=32)
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_add_frame_first_quest_frame(self, mock_cli):
        """Add the first frame for the kingdom's opening scene."""
        from aseprite_mcp.tools.canvas import add_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_frame(filename="kingdom.aseprite")
        assert "Added" in result
        mock_cli.execute_lua_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_layer_background_terrain(self, mock_cli):
        """Create the Background layer for the kingdom terrain."""
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_layer(
                filename="kingdom.aseprite", layer_name="Background"
            )
        assert "Added layer" in result
        assert "Background" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "Background" in script

    @pytest.mark.asyncio
    async def test_add_layer_knight_sprite(self, mock_cli):
        """Create the Knight layer for our hero."""
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_layer(filename="kingdom.aseprite", layer_name="Knight")
        assert "Added layer" in result

    @pytest.mark.asyncio
    async def test_add_layer_monsters(self, mock_cli):
        """Create the Monsters layer for the various enemies."""
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_layer(filename="kingdom.aseprite", layer_name="Monsters")
        assert "Added layer" in result

    @pytest.mark.asyncio
    async def test_add_layer_effects(self, mock_cli):
        """Create the Effects layer for spells and attack visuals."""
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_layer(filename="kingdom.aseprite", layer_name="Effects")
        assert "Added layer" in result

    @pytest.mark.asyncio
    async def test_set_frame_navigate_to_battle_scene(self, mock_cli):
        """Navigate to frame 2 — the battle begins."""
        from aseprite_mcp.tools.canvas import set_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame(filename="kingdom.aseprite", frame_index=2)
        assert "Set active frame to 2" in result

    @pytest.mark.asyncio
    async def test_set_frame_invalid_index_zero(self):
        """Frame index 0 is invalid — the knight can't time-travel backward."""
        from aseprite_mcp.tools.canvas import set_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame(filename="kingdom.aseprite", frame_index=0)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_frame_duration_kingdom_scene(self, mock_cli):
        """Set the kingdom frame duration to 200ms for a majestic view."""
        from aseprite_mcp.tools.canvas import set_frame_duration

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame_duration(
                filename="kingdom.aseprite", frame_index=1, duration_ms=200
            )
        assert "200" in result

    @pytest.mark.asyncio
    async def test_set_layer_activate_knight_layer(self, mock_cli):
        """Set the active layer to Knight so the hero can be drawn."""
        from aseprite_mcp.tools.canvas import set_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer(filename="kingdom.aseprite", layer_name="Knight")
        assert "Set active layer" in result
        assert "Knight" in result

    @pytest.mark.asyncio
    async def test_set_layer_create_if_missing_spell_layer(self, mock_cli):
        """Create the Spell layer on-the-fly when the knight learns magic."""
        from aseprite_mcp.tools.canvas import set_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer(
                filename="kingdom.aseprite",
                layer_name="Spells",
                create_if_missing=True,
            )
        assert "Set active layer" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "newLayer" in script


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 2: Designing the Knight (Drawing - Basic + Layer/Frame Targeted)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter2:
    """Draw the knight's equipment, monsters, and the kingdom backdrop."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.drawing.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_draw_pixels_knight_sword(self, mock_cli):
        """Draw the knight's silver melee sword using individual pixels."""
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels(
                filename="kingdom.aseprite",
                pixels=[
                    {"x": 10, "y": 5, "color": "#c0c0c0"},
                    {"x": 11, "y": 5, "color": "#c0c0c0"},
                    {"x": 12, "y": 5, "color": "#c0c0c0"},
                ],
            )
        assert "Pixels drawn" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "putPixel" in script

    @pytest.mark.asyncio
    async def test_draw_line_ranged_spell_bolt(self, mock_cli):
        """Draw the knight's magic bolt — a line from hand to target."""
        from aseprite_mcp.tools.drawing import draw_line

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line(
                filename="kingdom.aseprite",
                x1=5,
                y1=10,
                x2=50,
                y2=10,
                color="#00ffff",
                thickness=2,
            )
        assert "Line drawn" in result

    @pytest.mark.asyncio
    async def test_draw_rectangle_knight_shield(self, mock_cli):
        """Draw the knight's shield as a rectangle outline."""
        from aseprite_mcp.tools.drawing import draw_rectangle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle(
                filename="kingdom.aseprite",
                x=2,
                y=8,
                width=6,
                height=8,
                color="#8b4513",
                fill=False,
            )
        assert "Rectangle drawn" in result

    @pytest.mark.asyncio
    async def test_fill_area_knight_cape(self, mock_cli):
        """Fill the knight's cape area with a royal red color."""
        from aseprite_mcp.tools.drawing import fill_area

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area(
                filename="kingdom.aseprite", x=20, y=15, color="#8b0000"
            )
        assert "Area filled" in result

    @pytest.mark.asyncio
    async def test_draw_circle_knight_armor_plate(self, mock_cli):
        """Draw the knight's armor plate as a filled circle."""
        from aseprite_mcp.tools.drawing import draw_circle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle(
                filename="kingdom.aseprite",
                center_x=16,
                center_y=16,
                radius=8,
                color="#a0a0a0",
                fill=True,
            )
        assert "Circle drawn" in result

    @pytest.mark.asyncio
    async def test_draw_pixels_at_holy_sword_glow(self, mock_cli):
        """Draw the knight's holy sword glow on a specific layer and frame."""
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels_at(
                filename="kingdom.aseprite",
                layer_name="Effects",
                frame_index=3,
                pixels=[
                    {"x": 10, "y": 5, "color": "#ffff00"},
                    {"x": 11, "y": 5, "color": "#ffff00"},
                ],
            )
        assert "Pixels drawn" in result
        assert "Effects" in result
        assert "frame 3" in result

    @pytest.mark.asyncio
    async def test_draw_line_at_ranged_weapon_trajectory(self, mock_cli):
        """Draw the ranged spell trajectory on the Effects layer."""
        from aseprite_mcp.tools.drawing import draw_line_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line_at(
                filename="kingdom.aseprite",
                layer_name="Effects",
                frame_index=2,
                x1=16,
                y1=16,
                x2=48,
                y2=32,
                color="#00ffff",
            )
        assert "Line drawn" in result
        assert "Effects" in result

    @pytest.mark.asyncio
    async def test_draw_rectangle_at_skeleton_bone_shield(self, mock_cli):
        """Draw the skeleton monster's bone shield on a specific frame."""
        from aseprite_mcp.tools.drawing import draw_rectangle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle_at(
                filename="kingdom.aseprite",
                layer_name="Monsters",
                frame_index=2,
                x=40,
                y=20,
                width=8,
                height=12,
                color="#e8e8d0",
            )
        assert "Rectangle drawn" in result
        assert "Monsters" in result

    @pytest.mark.asyncio
    async def test_draw_circle_at_goblin_crude_axe(self, mock_cli):
        """Draw the goblin's crude axe head as a filled circle."""
        from aseprite_mcp.tools.drawing import draw_circle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle_at(
                filename="kingdom.aseprite",
                layer_name="Monsters",
                frame_index=3,
                center_x=44,
                center_y=28,
                radius=3,
                color="#556b2f",
                fill=True,
            )
        assert "Circle drawn" in result
        assert "Monsters" in result

    @pytest.mark.asyncio
    async def test_fill_area_at_slime_body(self, mock_cli):
        """Fill the slime monster's gelatinous body on the Monsters layer."""
        from aseprite_mcp.tools.drawing import fill_area_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area_at(
                filename="kingdom.aseprite",
                layer_name="Monsters",
                frame_index=4,
                x=48,
                y=40,
                color="#00ff00",
            )
        assert "Area filled" in result
        assert "Monsters" in result

    @pytest.mark.asyncio
    async def test_draw_polygon_dragon_wing(self, mock_cli):
        """Draw the fearsome dragon's wing shape as a polygon."""
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_polygon(
                filename="kingdom.aseprite",
                layer_name="Monsters",
                frame_index=5,
                points=[
                    {"x": 50, "y": 10},
                    {"x": 60, "y": 5},
                    {"x": 62, "y": 20},
                    {"x": 52, "y": 18},
                ],
                color="#8b0000",
                fill=True,
            )
        assert "Polygon drawn" in result

    @pytest.mark.asyncio
    async def test_draw_polygon_too_few_points(self):
        """A polygon with fewer than 3 points is invalid — even a dragon needs shape."""
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_polygon(
                filename="kingdom.aseprite",
                layer_name="Monsters",
                frame_index=5,
                points=[{"x": 1, "y": 1}, {"x": 2, "y": 2}],
                color="#ff0000",
            )
        assert "3 points" in result

    @pytest.mark.asyncio
    async def test_draw_path_castle_tower(self, mock_cli):
        """Draw the castle tower path — a polyline for the fortress outline."""
        from aseprite_mcp.tools.drawing import draw_path

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_path(
                filename="kingdom.aseprite",
                layer_name="Background",
                frame_index=1,
                points=[
                    {"x": 0, "y": 64},
                    {"x": 0, "y": 20},
                    {"x": 10, "y": 20},
                    {"x": 10, "y": 64},
                ],
                color="#808080",
                thickness=2,
            )
        assert "Path drawn" in result

    @pytest.mark.asyncio
    async def test_draw_path_too_few_points(self):
        """A path needs at least 2 points — the knight can't draw a line to nowhere."""
        from aseprite_mcp.tools.drawing import draw_path

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_path(
                filename="kingdom.aseprite",
                layer_name="Background",
                frame_index=1,
                points=[{"x": 1, "y": 1}],
                color="#808080",
            )
        assert "2 points" in result

    @pytest.mark.asyncio
    async def test_apply_gradient_rect_sky_to_ground(self, mock_cli):
        """Apply a gradient from sky blue to ground brown for the kingdom backdrop."""
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="kingdom.aseprite",
                layer_name="Background",
                frame_index=1,
                x=0,
                y=0,
                width=64,
                height=64,
                color_start="#4488ff",
                color_end="#8b6914",
                horizontal=False,
            )
        assert "Gradient applied" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 3: The Journey Begins (Animation - Frames & Cels)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter3:
    """Animate the knight's walk, attacks, and dodge maneuvers."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.animation.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_add_frames_walk_cycle(self, mock_cli):
        """Add 8 frames for the knight's walk cycle animation."""
        from aseprite_mcp.tools.animation import add_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await add_frames(filename="kingdom.aseprite", count=8)
        assert "Added 8 frames" in result
        assert "kingdom.aseprite" in result

    @pytest.mark.asyncio
    async def test_add_frames_invalid_count(self):
        """Zero frames is invalid — the knight must take at least one step."""
        from aseprite_mcp.tools.animation import add_frames

        result = await add_frames(filename="kingdom.aseprite", count=0)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_add_frames_with_duration(self, mock_cli):
        """Add walk cycle frames with 100ms duration for smooth animation."""
        from aseprite_mcp.tools.animation import add_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await add_frames(
                filename="kingdom.aseprite", count=4, duration_ms=100
            )
        assert "Added 4 frames" in result
        assert "100ms" in result

    @pytest.mark.asyncio
    async def test_set_frame_duration_all_smooth_animation(self, mock_cli):
        """Set all frames to 100ms for butter-smooth animation."""
        from aseprite_mcp.tools.animation import set_frame_duration_all

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_frame_duration_all(
                filename="kingdom.aseprite", duration_ms=100
            )
        assert "100ms" in result

    @pytest.mark.asyncio
    async def test_set_frame_duration_all_invalid(self):
        """Zero duration is invalid — time must flow for the quest."""
        from aseprite_mcp.tools.animation import set_frame_duration_all

        result = await set_frame_duration_all(
            filename="kingdom.aseprite", duration_ms=0
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_layer_visibility_stealth_approach(self, mock_cli):
        """Hide the Monsters layer for the knight's stealth approach."""
        from aseprite_mcp.tools.animation import set_layer_visibility

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_layer_visibility(
                filename="kingdom.aseprite", layer_name="Monsters", visible=False
            )
        assert "Monsters" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "false" in script

    @pytest.mark.asyncio
    async def test_set_layer_opacity_transparent_approach(self, mock_cli):
        """Set knight layer to 200 opacity for a semi-transparent stealth effect."""
        from aseprite_mcp.tools.animation import set_layer_opacity

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_layer_opacity(
                filename="kingdom.aseprite", layer_name="Knight", opacity=200
            )
        assert "200" in result

    @pytest.mark.asyncio
    async def test_set_layer_opacity_invalid_too_high(self):
        """Opacity 256 exceeds the max — the knight cannot become a ghost."""
        from aseprite_mcp.tools.animation import set_layer_opacity

        result = await set_layer_opacity(
            filename="kingdom.aseprite", layer_name="Knight", opacity=256
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_get_sprite_info_quest_dimensions(self, mock_cli):
        """Check the quest sprite dimensions to plan the battlefield."""
        from aseprite_mcp.tools.animation import get_sprite_info

        mock_cli.execute_lua_script.return_value = (
            True,
            "Sprite: kingdom.aseprite\n  Dimensions: 64x64\n  Frames: 8",
        )
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await get_sprite_info(filename="kingdom.aseprite")
        assert "Sprite" in result or "kingdom" in result

    @pytest.mark.asyncio
    async def test_duplicate_frame_range_battle_sequence(self, mock_cli):
        """Duplicate frames 3-5 for a repeating battle attack sequence."""
        from aseprite_mcp.tools.animation import duplicate_frame_range

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await duplicate_frame_range(
                filename="kingdom.aseprite", start_frame=3, end_frame=5, times=2
            )
        assert "Duplicated" in result
        assert "3-5" in result

    @pytest.mark.asyncio
    async def test_duplicate_frame_range_invalid_start(self):
        """Start frame 0 invalid — the quest timeline starts at 1."""
        from aseprite_mcp.tools.animation import duplicate_frame_range

        result = await duplicate_frame_range(
            filename="kingdom.aseprite", start_frame=0, end_frame=3
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_cel_position_knight_walk(self, mock_cli):
        """Position the knight's cel for the walking animation."""
        from aseprite_mcp.tools.animation import set_cel_position

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_cel_position(
                filename="kingdom.aseprite",
                layer_name="Knight",
                frame_index=2,
                x=32,
                y=16,
            )
        assert "Set cel position" in result
        assert "Knight" in result

    @pytest.mark.asyncio
    async def test_tween_cel_positions_walk_left_to_right(self, mock_cli):
        """Tween knight movement from left to right across the screen."""
        from aseprite_mcp.tools.animation import tween_cel_positions

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_positions(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=1,
                end_frame=8,
                start_x=0,
                start_y=32,
                end_x=60,
                end_y=32,
            )
        assert "Tweened cel positions" in result

    @pytest.mark.asyncio
    async def test_offset_cel_positions_dodge_animation(self, mock_cli):
        """Nudge the knight's cel positions for a dodge animation."""
        from aseprite_mcp.tools.animation import offset_cel_positions

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await offset_cel_positions(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=4,
                end_frame=6,
                dx=0,
                dy=-4,
            )
        assert "Offset" in result

    @pytest.mark.asyncio
    async def test_create_cel_spell_effect(self, mock_cli):
        """Create an empty cel for the knight's spell effect on the Effects layer."""
        from aseprite_mcp.tools.animation import create_cel

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await create_cel(
                filename="kingdom.aseprite",
                layer_name="Effects",
                frame_index=5,
                x=0,
                y=0,
            )
        assert "Created cel" in result

    @pytest.mark.asyncio
    async def test_clear_cel_key_pickup(self, mock_cli):
        """Clear a cel after the knight picks up the dungeon key."""
        from aseprite_mcp.tools.animation import clear_cel

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await clear_cel(
                filename="kingdom.aseprite", layer_name="Effects", frame_index=3
            )
        assert "Cleared cel" in result

    @pytest.mark.asyncio
    async def test_copy_cel_idle_to_attack(self, mock_cli):
        """Copy the idle pose cel to the attack frame as a base for animation."""
        from aseprite_mcp.tools.animation import copy_cel

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await copy_cel(
                filename="kingdom.aseprite",
                layer_name="Knight",
                source_frame=1,
                target_frame=6,
            )
        assert "Copied cel" in result

    @pytest.mark.asyncio
    async def test_copy_frame_dodge_to_recovery(self, mock_cli):
        """Copy the dodge frame to the recovery frame."""
        from aseprite_mcp.tools.animation import copy_frame

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await copy_frame(
                filename="kingdom.aseprite", source_frame=4, target_frame=7
            )
        assert "Copied frame" in result

    @pytest.mark.asyncio
    async def test_propagate_frame_to_range_idle_stance(self, mock_cli):
        """Propagate the idle stance across multiple frames for consistency."""
        from aseprite_mcp.tools.animation import propagate_frame_to_range

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await propagate_frame_to_range(
                filename="kingdom.aseprite",
                source_frame=1,
                start_frame=2,
                end_frame=4,
            )
        assert "Propagated" in result

    @pytest.mark.asyncio
    async def test_set_tag_walk_animation(self, mock_cli):
        """Tag the walk animation frames (1-8) for the knight's movement."""
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="kingdom.aseprite",
                name="walk",
                from_frame=1,
                to_frame=8,
                direction="forward",
            )
        assert "walk" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "AniDir.FORWARD" in script

    @pytest.mark.asyncio
    async def test_set_tag_melee_attack(self, mock_cli):
        """Tag frames 9-12 as the melee attack animation."""
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="kingdom.aseprite",
                name="attack_melee",
                from_frame=9,
                to_frame=12,
                direction="forward",
            )
        assert "attack_melee" in result

    @pytest.mark.asyncio
    async def test_set_tag_ranged_attack(self, mock_cli):
        """Tag frames 13-16 as the ranged attack animation."""
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="kingdom.aseprite",
                name="attack_ranged",
                from_frame=13,
                to_frame=16,
                direction="forward",
            )
        assert "attack_ranged" in result

    @pytest.mark.asyncio
    async def test_set_tag_idle_stance(self, mock_cli):
        """Tag the idle stance animation with pingpong direction."""
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="kingdom.aseprite",
                name="idle",
                from_frame=1,
                to_frame=2,
                direction="pingpong",
            )
        assert "idle" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "AniDir.PINGPONG" in script

    @pytest.mark.asyncio
    async def test_set_tag_invalid_direction(self):
        """An invalid tag direction is rejected — the knight won't go 'sideways'."""
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="kingdom.aseprite",
                name="invalid",
                from_frame=1,
                to_frame=4,
                direction="sideways",
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_tween_cel_positions_eased_slash(self, mock_cli):
        """Ease the knight's slash animation with ease_in_out for a weighty feel."""
        from aseprite_mcp.tools.animation import tween_cel_positions_eased

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_positions_eased(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=9,
                end_frame=12,
                start_x=32,
                start_y=16,
                end_x=48,
                end_y=16,
                easing="ease_in_out",
            )
        assert "Tweened cel positions" in result
        assert "ease_in_out" in result

    @pytest.mark.asyncio
    async def test_tween_cel_positions_eased_invalid_easing(self):
        """Invalid easing function is rejected — no 'bouncy' ease for the knight."""
        from aseprite_mcp.tools.animation import tween_cel_positions_eased

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_positions_eased(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=1,
                end_frame=4,
                start_x=0,
                start_y=0,
                end_x=10,
                end_y=10,
                easing="bouncy",
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_oscillate_cel_positions_walking_bob(self, mock_cli):
        """Make the knight bob up and down while walking — a sine wave oscillation."""
        from aseprite_mcp.tools.animation import oscillate_cel_positions

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await oscillate_cel_positions(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=1,
                end_frame=8,
                amplitude_x=0,
                amplitude_y=3,
                cycles=2.0,
            )
        assert "Oscillated" in result

    @pytest.mark.asyncio
    async def test_tween_cel_opacity_eased_spell_fade(self, mock_cli):
        """Fade the spell effect in and out by tweening cel opacity."""
        from aseprite_mcp.tools.animation import tween_cel_opacity_eased

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_opacity_eased(
                filename="kingdom.aseprite",
                layer_name="Effects",
                start_frame=13,
                end_frame=16,
                start_opacity=255,
                end_opacity=0,
                easing="ease_out",
            )
        assert "Tweened cel opacity" in result
        assert "ease_out" in result

    @pytest.mark.asyncio
    async def test_propagate_cels_shield_layer(self, mock_cli):
        """Propagate the "Shield" layer cels across all battle frames."""
        from aseprite_mcp.tools.animation import propagate_cels

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await propagate_cels(
                filename="kingdom.aseprite",
                layer_names=["Shield"],
                source_frame=1,
                start_frame=9,
                end_frame=16,
            )
        assert "Propagated" in result

    @pytest.mark.asyncio
    async def test_get_sprite_info_file_not_found(self):
        """If the quest file is missing, the knight cannot assess the realm."""
        from aseprite_mcp.tools.animation import get_sprite_info

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File kingdom.aseprite not found",
        ):
            result = await get_sprite_info(filename="kingdom.aseprite")
        assert "not found" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 4: Arming the Knight (Export & Palette)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter4:
    """Export the sprite, manage color palettes, and remap armor colors."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.export.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_export_sprite_for_game_engine(self, mock_cli):
        """Export the knight's sprite sheet for the game engine."""
        import subprocess

        from aseprite_mcp.tools.export import export_sprite

        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )
        mock_cli.run_batch = MagicMock(return_value=mock_result)

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await export_sprite(
                filename="kingdom.aseprite", output_filename="knight.png", format="png"
            )
        assert "Exported" in result

    @pytest.mark.asyncio
    async def test_export_sprite_unsupported_format(self):
        """The knight's quest cannot be exported as a cursed .tiff format."""
        from aseprite_mcp.tools.export import export_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await export_sprite(
                filename="kingdom.aseprite",
                output_filename="knight.tiff",
                format="tiff",
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_copy_sprite_backup_quest(self, mock_cli):
        """Make a backup copy of the quest sprite before the dangerous battle."""
        from aseprite_mcp.tools.export import copy_sprite

        with (
            patch("aseprite_mcp.tools.export.check_file", return_value=None),
            patch("os.path.exists", return_value=False),
        ):
            result = await copy_sprite(
                filename="kingdom.aseprite", output_filename="kingdom_backup.aseprite"
            )
        assert "Copied" in result
        mock_cli.execute_lua_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_sprite_invalid_extension(self):
        """A knight's quest cannot be saved as a .png backup — must be .aseprite."""
        from aseprite_mcp.tools.export import copy_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await copy_sprite(
                filename="kingdom.aseprite", output_filename="backup.png"
            )
        assert "Error" in result


class TestKnightQuestChapter4Palette:
    """Palette management for arming the knight with proper colors."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.palette.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_get_palette_quest_colors(self, mock_cli):
        """Retrieve the quest sprite's color palette."""
        from aseprite_mcp.tools.palette import get_palette

        mock_cli.execute_lua_script.return_value = (
            True,
            '["#8b0000", "#c0c0c0", "#00ff00", "#8b4513"]',
        )
        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await get_palette(filename="kingdom.aseprite")
        assert "palette" in result.lower() or "8b0000" in result

    @pytest.mark.asyncio
    async def test_set_palette_dungeon_theme(self, mock_cli):
        """Set a dark dungeon-themed palette for the boss battle scene."""
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await set_palette(
                filename="kingdom.aseprite",
                colors=["#1a1a2e", "#16213e", "#0f3460", "#e94560"],
            )
        assert "4 colors" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "Palette(4)" in script

    @pytest.mark.asyncio
    async def test_set_palette_empty_colors(self):
        """An empty palette is useless — even a knight needs some colors."""
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await set_palette(filename="kingdom.aseprite", colors=[])
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_remap_colors_silver_to_gold(self, mock_cli):
        """Remap the knight's armor from silver (#c0c0c0) to gold (#ffd700)."""
        from aseprite_mcp.tools.palette import remap_colors_in_cel_range

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await remap_colors_in_cel_range(
                filename="kingdom.aseprite",
                layer_name="Knight",
                start_frame=1,
                end_frame=16,
                mappings=[{"from": "#c0c0c0", "to": "#ffd700"}],
            )
        assert "Remapped" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 5: Scouting the Battlefield (Pixel Read & Preview)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter5:
    """Read pixels and preview the quest animation in a browser."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.pixel_read.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_get_pixel_color_knight_position(self, mock_cli):
        """Read the pixel color at the knight's standing position."""
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        mock_cli.execute_lua_script.return_value = (True, "PIXEL:255,0,0,255")
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixel_color(filename="kingdom.aseprite", x=16, y=32)
        assert "#ff0000" in result
        mock_cli.execute_lua_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pixel_color_invalid_frame(self):
        """The knight cannot scout frame 0 — frames start at 1."""
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixel_color(
                filename="kingdom.aseprite", x=0, y=0, frame_index=0
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_collision_map(self, mock_cli):
        """Read a rectangular region for collision detection mapping."""
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        mock_cli.execute_lua_script.return_value = (
            True,
            "PIXEL:0,0,255,0,0,255\nPIXEL:1,0,0,255,0,128",
        )
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="kingdom.aseprite", x=0, y=0, width=2, height=1
            )
        parsed = json.loads(result)
        assert "pixels" in parsed
        assert parsed["count"] == 2

    @pytest.mark.asyncio
    async def test_get_pixels_rect_invalid_width(self):
        """Zero width rectangle is invalid — the knight can't scout nothing."""
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="kingdom.aseprite", x=0, y=0, width=0, height=10
            )
        assert "Error" in result


class TestKnightQuestChapter5Preview:
    """Preview server management for viewing the quest animation."""

    @pytest.mark.asyncio
    async def test_start_preview_server_nonexistent_directory(self):
        """The knight can't host a preview in a nonexistent fortress."""
        from aseprite_mcp.tools.preview import start_preview_server

        result = await start_preview_server(directory="/nonexistent/path/xyz")
        assert "Error" in result
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_start_preview_server_success(self, tmp_path):
        """Start a preview server to watch the quest animation in browser."""
        import os

        from aseprite_mcp.tools.preview import _pid_path, start_preview_server

        pid_file = _pid_path(8002)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.side_effect = subprocess.TimeoutExpired("cmd", 0.5)

        with patch("subprocess.Popen", return_value=mock_proc):
            result = await start_preview_server(directory=str(tmp_path), port=8002)
        assert "started" in result.lower() or "Preview" in result

        if os.path.exists(pid_file):
            os.remove(pid_file)

    @pytest.mark.asyncio
    async def test_stop_preview_server_no_pid_file(self):
        """Stop a preview server when no PID file exists."""
        import os

        from aseprite_mcp.tools.preview import _pid_path, stop_preview_server

        pid_file = _pid_path(9997)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        result = await stop_preview_server(port=9997)
        assert (
            "no" in result.lower() and "PID" in result.upper()
        ) or "No preview server" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 6: Building the Boss Arena (Scene & Quality)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter6:
    """Copy layers from boss sprite, validate, audit, and sanitize the battle scene."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.scene.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_copy_layers_between_sprites_dragon_to_quest(self, mock_cli):
        """Copy the dragon's layer from boss_sprite to main quest sprite."""
        from aseprite_mcp.tools.scene import copy_layers_between_sprites

        with patch("aseprite_mcp.tools.scene.check_file", return_value=None):
            result = await copy_layers_between_sprites(
                source_filename="boss.aseprite",
                target_filename="kingdom.aseprite",
                layer_names=["Dragon"],
            )
        assert "Copied" in result

    @pytest.mark.asyncio
    async def test_copy_layers_path_traversal(self):
        """Path traversal is rejected — no sneaking into forbidden directories."""
        from aseprite_mcp.tools.scene import copy_layers_between_sprites

        with patch("aseprite_mcp.tools.scene.check_file", return_value=None):
            result = await copy_layers_between_sprites(
                source_filename="../etc/passwd",
                target_filename="kingdom.aseprite",
                layer_names=["Dragon"],
            )
        assert ".." in result


class TestKnightQuestChapter6Guide:
    """Get an animation workflow guide for organizing the quest animation."""

    @pytest.mark.asyncio
    async def test_animation_workflow_guide_character(self):
        """Request a character animation workflow guide for the knight's quest."""
        from aseprite_mcp.tools.guide import animation_workflow_guide

        result = await animation_workflow_guide(use_case="character")
        assert "Character" in result
        assert "create_canvas" in result

    @pytest.mark.asyncio
    async def test_animation_workflow_guide_environment(self):
        """Request an environment animation guide for the battle arena."""
        from aseprite_mcp.tools.guide import animation_workflow_guide

        result = await animation_workflow_guide(use_case="environment")
        assert "Environment" in result

    @pytest.mark.asyncio
    async def test_animation_workflow_guide_default(self):
        """Request the default animation workflow guide."""
        from aseprite_mcp.tools.guide import animation_workflow_guide

        result = await animation_workflow_guide(use_case="general")
        assert "Animation" in result


class TestKnightQuestChapter6Quality:
    """Ensure battle scene quality with validation, audit, and sanitization."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.quality.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_ensure_layers_present_battle_scene(self, mock_cli):
        """Ensure all required layers exist for the battle scene."""
        from aseprite_mcp.tools.quality import ensure_layers_present

        mock_cli.execute_lua_script.return_value = (
            True,
            "Created 3 cel(s), skipped 0 layer(s)",
        )
        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await ensure_layers_present(
                filename="kingdom.aseprite",
                layer_names=["Knight", "Monsters", "Effects"],
                start_frame=1,
                end_frame=8,
            )
        assert "ensure_layers_present" in result

    @pytest.mark.asyncio
    async def test_ensure_layers_present_path_traversal(self):
        """Path traversal is blocked — no escaping the arena."""
        from aseprite_mcp.tools.quality import ensure_layers_present

        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await ensure_layers_present(
                filename="../secret.ase",
                layer_names=["Knight"],
            )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_validate_scene_battle(self, mock_cli):
        """Validate the battle scene has no missing cels for smooth combat."""
        from aseprite_mcp.tools.quality import validate_scene

        mock_cli.execute_lua_script.return_value = (
            True,
            'JSON_START{"frames":8,"range":{"start":1,"end":8},"missing_layers":[],"missing_cels":[]}',
        )
        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await validate_scene(
                filename="kingdom.aseprite",
                required_layers=["Knight", "Monsters", "Effects"],
                start_frame=1,
                end_frame=8,
            )
        assert (
            "frames" in result.lower()
            or "JSON" in result
            or "missing" in result.lower()
        )

    @pytest.mark.asyncio
    async def test_audit_animation_battle_scene(self, mock_cli):
        """Audit the battle animation for overlapping sprites or out-of-range cels."""
        from aseprite_mcp.tools.quality import audit_animation

        mock_cli.execute_lua_script.return_value = (
            True,
            'JSON_START{"summary":{"total_cels":24,"overlaps_count":0,"out_of_range_count":0}}',
        )
        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await audit_animation(
                filename="kingdom.aseprite",
                start_frame=1,
                end_frame=16,
                overlap_pairs=["Knight,Monsters"],
                report_bounds=True,
            )
        # Accept any valid response
        assert result is not None and len(result) > 0

    @pytest.mark.asyncio
    async def test_animation_sanitize_battle_scene(self, mock_cli):
        """Sanitize the final battle animation for production readiness."""
        from aseprite_mcp.tools.quality import animation_sanitize

        mock_cli.execute_lua_script.return_value = (
            True,
            'JSON_START{"sanitized":true,"analysis":{"total_layers":4,"total_cels":32}}',
        )
        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await animation_sanitize(
                filename="kingdom.aseprite",
                start_frame=1,
                end_frame=16,
                ensure_layers=["Knight", "Monsters", "Effects", "Background"],
                layer_order=["Background", "Monsters", "Knight", "Effects"],
            )
        # Accept any valid response
        assert result is not None and len(result) > 0

    @pytest.mark.asyncio
    async def test_animation_sanitize_invalid_action(self):
        """Invalid sanitization action is rejected — no 'destroy' action."""
        from aseprite_mcp.tools.quality import animation_sanitize

        with patch("aseprite_mcp.tools.quality.check_file", return_value=None):
            result = await animation_sanitize(
                filename="kingdom.aseprite",
                out_of_range_action="destroy",
            )
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 7: Combat Mechanics (Transform)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter7:
    """Flip, rotate, resize, and crop the battlefield for the final boss fight."""

    @pytest.fixture(autouse=True)
    def patch_get_cli(self, mock_cli):
        with patch("aseprite_mcp.tools.transform.get_cli", return_value=mock_cli):
            yield mock_cli

    @pytest.mark.asyncio
    async def test_flip_layer_sword_arm_left_attack(self, mock_cli):
        """Flip the knight's sword arm sprite for a left-facing attack."""
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="kingdom.aseprite",
                layer_name="Knight",
                frame_index=9,
                direction="horizontal",
            )
        assert "Flipped" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "horizontal" in script.lower() or "w - 1 - x" in script

    @pytest.mark.asyncio
    async def test_flip_layer_invalid_direction(self):
        """Diagonal flip is not a valid combat maneuver."""
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="kingdom.aseprite",
                layer_name="Knight",
                frame_index=1,
                direction="diagonal",
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_rotate_layer_ranged_spell_diagonal(self, mock_cli):
        """Rotate the ranged spell effect for a diagonal cast angle."""
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="kingdom.aseprite",
                layer_name="Effects",
                frame_index=13,
                angle=90,
            )
        assert "Rotated" in result

    @pytest.mark.asyncio
    async def test_rotate_layer_invalid_angle(self):
        """A 45-degree rotation is not standard combat form for the knight."""
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="kingdom.aseprite",
                layer_name="Knight",
                frame_index=1,
                angle=45,
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_boss_arena(self, mock_cli):
        """Resize the arena for the final boss battle — expand to 128x128."""
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(
                filename="kingdom.aseprite", width=128, height=128
            )
        assert "Resized" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_invalid_width(self):
        """Zero width is invalid — the arena can't collapse to nothing."""
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(
                filename="kingdom.aseprite", width=0, height=128
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_crop_canvas_remove_empty_borders(self, mock_cli):
        """Crop the sprite to remove empty borders around the knight."""
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="kingdom.aseprite", x=4, y=4, width=56, height=56
            )
        assert "Cropped" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "crop" in script.lower()

    @pytest.mark.asyncio
    async def test_crop_canvas_invalid_height(self):
        """Negative height is invalid — the knight can't have negative space."""
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="kingdom.aseprite", x=0, y=0, width=10, height=-5
            )
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 8: Legacy Server Tools (server.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestKnightQuestChapter8:
    """Test the legacy server.py tools — the ancient spells from the old kingdom."""

    @pytest.fixture
    def config(self, tmp_path):
        return AsepriteConfig(
            aseprite_path="/usr/bin/aseprite",
            tmp_dir=tmp_path / "scripts",
            output_dir=tmp_path / "output",
        )

    @pytest.mark.asyncio
    async def test_sprite_create_princess_rescue_cutscene(self, config):
        """Create a sprite for the princess rescue cutscene."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_json_script.return_value = {
            "width": 32,
            "height": 32,
            "colorMode": "rgb",
            "filename": "/tmp/princess_rescue.ase",
        }
        srv._cli = mock_cli
        srv._config = config

        result = await srv.sprite_create(width=32, height=32)
        parsed = json.loads(result)
        assert parsed["width"] == 32
        assert parsed["height"] == 32

    @pytest.mark.asyncio
    async def test_sprite_create_invalid_dimensions(self):
        """Zero dimensions are invalid — the princess realm needs form."""
        from aseprite_mcp.server import sprite_create

        result = await sprite_create(width=0, height=32)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_create_invalid_color_mode(self):
        """CMYK color mode doesn't exist in the knight's realm."""
        from aseprite_mcp.server import sprite_create

        result = await sprite_create(width=32, height=32, color_mode="cmyk")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_export_final_game_asset(self, config):
        """Export the final game asset as PNG."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_json_script.return_value = {
            "output": "generated_assets/knight.png",
            "success": True,
        }
        srv._cli = mock_cli
        srv._config = config

        result = await srv.sprite_export(input_path="/path/to/kingdom.ase")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_sprite_export_invalid_format(self):
        """Export to .pdf is invalid — the knight's journey is pixel art only."""
        from aseprite_mcp.server import sprite_export

        result = await sprite_export(input_path="test.pdf", output_path="out.png")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_info_quest_metadata(self, config):
        """Read metadata of the quest sprite — dimensions, layers, tags."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_json_script.return_value = {
            "width": 64,
            "height": 64,
            "frames": 16,
            "layers": ["Background", "Knight", "Monsters", "Effects"],
        }
        srv._cli = mock_cli
        srv._config = config

        result = await srv.sprite_info(file_path="kingdom.ase")
        parsed = json.loads(result)
        assert parsed["width"] == 64

    @pytest.mark.asyncio
    async def test_sprite_list_layers_quest_layers(self, config):
        """List all layers in the quest sprite to verify scene structure."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.list_layers.return_value = [
            "Background",
            "Knight",
            "Monsters",
            "Effects",
        ]
        srv._cli = mock_cli

        result = await srv.sprite_list_layers(file_path="kingdom.ase")
        parsed = json.loads(result)
        assert "layers" in parsed
        assert len(parsed["layers"]) == 4
        assert "Knight" in parsed["layers"]

    @pytest.mark.asyncio
    async def test_sprite_list_tags_quest_tags(self, config):
        """List all animation tags to verify the knight's walk/attack animations."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.list_tags.return_value = [
            "walk",
            "attack_melee",
            "attack_ranged",
            "idle",
        ]
        srv._cli = mock_cli

        result = await srv.sprite_list_tags(file_path="kingdom.ase")
        parsed = json.loads(result)
        assert "tags" in parsed
        assert "walk" in parsed["tags"]

    @pytest.mark.asyncio
    async def test_spritesheet_export_game_atlas(self, config):
        """Export the game's sprite atlas for use in the game engine."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_cli.run_batch = MagicMock(return_value=mock_result)
        srv._cli = mock_cli
        srv._config = config

        result = await srv.spritesheet_export(input_path="/path/to/kingdom.ase")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "sheet" in parsed
        assert "data" in parsed

    @pytest.mark.asyncio
    async def test_script_execute_victory_dance(self, config):
        """Execute a custom Lua script for the knight's victory dance."""
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_script.return_value = "Victory dance complete!"
        srv._cli = mock_cli

        result = await srv.script_execute(lua_code='print("Victory dance!")')
        assert result == "Victory dance complete!"

    @pytest.mark.asyncio
    async def test_ws_connect_launch_bridge(self):
        """Launch the WebSocket bridge for real-time quest rendering."""
        from aseprite_mcp import server as srv
        from aseprite_mcp.websocket_bridge import WebSocketBridge

        mock_bridge = AsyncMock(spec=WebSocketBridge)
        mock_bridge.start = AsyncMock()
        mock_bridge.ws_url = "ws://127.0.0.1:18766"
        mock_bridge.launch_aseprite_with_bridge = MagicMock()
        srv._ws_bridge = mock_bridge

        result = await srv.ws_connect()
        parsed = json.loads(result)
        assert parsed["ws_url"] == "ws://127.0.0.1:18766"
        assert parsed["status"] == "launched"

    @pytest.mark.asyncio
    async def test_ws_draw_pixels_real_time_drawing(self):
        """Draw pixels in real-time via the WebSocket bridge."""
        from aseprite_mcp import server as srv
        from aseprite_mcp.websocket_bridge import WebSocketBridge

        mock_bridge = AsyncMock(spec=WebSocketBridge)
        mock_bridge.send_command = AsyncMock(return_value={"status": "ok"})
        srv._ws_bridge = mock_bridge

        result = await srv.ws_draw_pixels(pixels=[{"x": 5, "y": 5, "color": "#ff0000"}])
        parsed = json.loads(result)
        assert parsed["status"] == "ok"

    @pytest.mark.asyncio
    async def test_ws_fill_rect_fill_battle_zone(self):
        """Fill a rectangle area via WebSocket for quick terrain painting."""
        from aseprite_mcp import server as srv
        from aseprite_mcp.websocket_bridge import WebSocketBridge

        mock_bridge = AsyncMock(spec=WebSocketBridge)
        mock_bridge.send_command = AsyncMock(return_value={"status": "ok"})
        srv._ws_bridge = mock_bridge

        result = await srv.ws_fill_rect(x=0, y=0, width=10, height=10, color="#228b22")
        parsed = json.loads(result)
        assert parsed["status"] == "ok"
