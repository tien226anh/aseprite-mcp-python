"""Tests for aseprite_mcp.tools.animation module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI


@pytest.fixture
def mock_cli():
    """Create a mock AsepriteCLI with execute_lua_script returning success."""
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    return cli


@pytest.fixture(autouse=True)
def patch_get_cli(mock_cli):
    """Patch get_cli to return our mock for all tests in this module."""
    with patch("aseprite_mcp.tools.animation.get_cli", return_value=mock_cli):
        yield mock_cli


def _no_file(filename):
    """Helper: check_file that reports file not found."""
    return f"File {filename} not found"


class TestAddFrames:
    @pytest.mark.asyncio
    async def test_add_frames_count_zero(self):
        from aseprite_mcp.tools.animation import add_frames

        result = await add_frames(filename="test.ase", count=0)
        assert "Error" in result
        assert "count" in result

    @pytest.mark.asyncio
    async def test_add_frames_count_negative(self):
        from aseprite_mcp.tools.animation import add_frames

        result = await add_frames(filename="test.ase", count=-1)
        assert "Error" in result
        assert "count" in result

    @pytest.mark.asyncio
    async def test_add_frames_file_not_found(self):
        from aseprite_mcp.tools.animation import add_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value="File test.ase not found"):
            result = await add_frames(filename="test.ase", count=3)
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_add_frames_success(self, mock_cli):
        from aseprite_mcp.tools.animation import add_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await add_frames(filename="test.ase", count=3)
        assert "Added 3 frames" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "3" in script

    @pytest.mark.asyncio
    async def test_add_frames_with_duration(self, mock_cli):
        from aseprite_mcp.tools.animation import add_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await add_frames(filename="test.ase", count=2, duration_ms=100)
        assert "Added 2 frames" in result
        assert "100ms" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "0.1" in script  # 100ms = 0.1s


class TestSetFrameDurationAll:
    @pytest.mark.asyncio
    async def test_set_frame_duration_all_invalid(self):
        from aseprite_mcp.tools.animation import set_frame_duration_all

        result = await set_frame_duration_all(filename="test.ase", duration_ms=0)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_frame_duration_all_success(self, mock_cli):
        from aseprite_mcp.tools.animation import set_frame_duration_all

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_frame_duration_all(filename="test.ase", duration_ms=200)
        assert "200ms" in result


class TestSetLayerVisibility:
    @pytest.mark.asyncio
    async def test_set_layer_visibility_file_not_found(self):
        from aseprite_mcp.tools.animation import set_layer_visibility

        with patch("aseprite_mcp.tools.animation.check_file", return_value="File missing"):
            result = await set_layer_visibility(filename="missing.ase", layer_name="BG", visible=True)
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_set_layer_visibility_success(self, mock_cli):
        from aseprite_mcp.tools.animation import set_layer_visibility

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_layer_visibility(
                filename="test.ase", layer_name="Layer1", visible=False
            )
        assert "visibility" in result.lower() or "True" in result or "False" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "false" in script


class TestSetLayerOpacity:
    @pytest.mark.asyncio
    async def test_set_layer_opacity_too_high(self):
        from aseprite_mcp.tools.animation import set_layer_opacity

        result = await set_layer_opacity(
            filename="test.ase", layer_name="BG", opacity=256
        )
        assert "Error" in result
        assert "opacity" in result

    @pytest.mark.asyncio
    async def test_set_layer_opacity_negative(self):
        from aseprite_mcp.tools.animation import set_layer_opacity

        result = await set_layer_opacity(
            filename="test.ase", layer_name="BG", opacity=-1
        )
        assert "Error" in result
        assert "opacity" in result

    @pytest.mark.asyncio
    async def test_set_layer_opacity_file_not_found(self):
        from aseprite_mcp.tools.animation import set_layer_opacity

        with patch("aseprite_mcp.tools.animation.check_file", return_value="File missing"):
            result = await set_layer_opacity(
                filename="missing.ase", layer_name="BG", opacity=128
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_set_layer_opacity_success(self, mock_cli):
        from aseprite_mcp.tools.animation import set_layer_opacity

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_layer_opacity(
                filename="test.ase", layer_name="Layer1", opacity=128
            )
        assert "128" in result
        mock_cli.execute_lua_script.assert_called_once()


class TestGetSpriteInfo:
    @pytest.mark.asyncio
    async def test_get_sprite_info_file_not_found(self):
        from aseprite_mcp.tools.animation import get_sprite_info

        with patch("aseprite_mcp.tools.animation.check_file", return_value="File missing"):
            result = await get_sprite_info(filename="missing.ase")
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_get_sprite_info_success(self, mock_cli):
        from aseprite_mcp.tools.animation import get_sprite_info

        mock_cli.execute_lua_script.return_value = (
            True,
            "Sprite: test.ase\n  Dimensions: 32x32\n  Frames: 4",
        )
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await get_sprite_info(filename="test.ase")
        assert "Sprite" in result or "test.ase" in result


class TestSetTag:
    @pytest.mark.asyncio
    async def test_set_tag_invalid_direction(self):
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="test.ase", name="walk", from_frame=1, to_frame=4, direction="sideways"
            )
        assert "Error" in result
        assert "direction" in result

    @pytest.mark.asyncio
    async def test_set_tag_invalid_frame_range(self):
        from aseprite_mcp.tools.animation import set_tag

        result = await set_tag(
            filename="test.ase", name="walk", from_frame=0, to_frame=4
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_tag_from_greater_than_to(self):
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="test.ase", name="walk", from_frame=5, to_frame=2
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_tag_file_not_found(self):
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value="File missing"):
            result = await set_tag(
                filename="missing.ase", name="walk", from_frame=1, to_frame=4
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_set_tag_success(self, mock_cli):
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="test.ase", name="walk", from_frame=1, to_frame=4, direction="forward"
            )
        assert "walk" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "AniDir.FORWARD" in script


class TestDuplicateFrameRange:
    @pytest.mark.asyncio
    async def test_duplicate_invalid_start(self):
        from aseprite_mcp.tools.animation import duplicate_frame_range

        result = await duplicate_frame_range(
            filename="test.ase", start_frame=0, end_frame=3
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_duplicate_end_before_start(self):
        from aseprite_mcp.tools.animation import duplicate_frame_range

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await duplicate_frame_range(
                filename="test.ase", start_frame=5, end_frame=2
            )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_duplicate_invalid_times(self):
        from aseprite_mcp.tools.animation import duplicate_frame_range

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await duplicate_frame_range(
                filename="test.ase", start_frame=1, end_frame=3, times=0
            )
        assert "Error" in result