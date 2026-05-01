"""Tests for aseprite_mcp.tools.adjust module."""

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
    with patch("aseprite_mcp.tools.adjust.get_cli", return_value=mock_cli):
        yield mock_cli


# ── adjust_colors ────────────────────────────────────────────────────────────


class TestAdjustColors:
    @pytest.mark.asyncio
    async def test_path_traversal(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        result = await adjust_colors(
            filename="../etc/passwd",
            layer_name="Layer 1",
            frame_index=1,
        )
        assert "Error" in result
        assert ".." in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch(
            "aseprite_mcp.tools.adjust.check_file",
            return_value="File not_found.ase not found",
        ):
            result = await adjust_colors(
                filename="not_found.ase",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "not found" in result

    @pytest.mark.asyncio
    async def test_frame_index_less_than_1(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=0,
            )
            assert "Error" in result
            assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_brightness_out_of_range_low(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                brightness=-300,
            )
            assert "Error" in result
            assert "brightness" in result

    @pytest.mark.asyncio
    async def test_brightness_out_of_range_high(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                brightness=300,
            )
            assert "Error" in result
            assert "brightness" in result

    @pytest.mark.asyncio
    async def test_contrast_out_of_range(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                contrast=500,
            )
            assert "Error" in result
            assert "contrast" in result

    @pytest.mark.asyncio
    async def test_hue_shift_out_of_range(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                hue_shift=-200,
            )
            assert "Error" in result
            assert "hue_shift" in result

    @pytest.mark.asyncio
    async def test_saturation_out_of_range(self):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                saturation=500,
            )
            assert "Error" in result
            assert "saturation" in result

    @pytest.mark.asyncio
    async def test_success_no_adjustments(self, mock_cli):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "Adjusted colors" in result
            mock_cli.execute_lua_script.assert_called_once()
            script = mock_cli.execute_lua_script.call_args[0][0]
            assert "Layer 1" in script
            assert "1" in script

    @pytest.mark.asyncio
    async def test_success_with_all_adjustments(self, mock_cli):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="BG",
                frame_index=3,
                brightness=50,
                contrast=30,
                hue_shift=90,
                saturation=100,
            )
            assert "Adjusted colors" in result
            mock_cli.execute_lua_script.assert_called_once()
            script = mock_cli.execute_lua_script.call_args[0][0]
            assert "rgbToHsv" in script
            assert "hsvToRgb" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.adjust import adjust_colors

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "Failed" in result

    @pytest.mark.asyncio
    async def test_boundary_values_accepted(self, mock_cli):
        from aseprite_mcp.tools.adjust import adjust_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            # brightness -255, contrast -255, hue -180, saturation -255
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                brightness=-255,
                contrast=-255,
                hue_shift=-180,
                saturation=-255,
            )
            assert "Adjusted colors" in result

            # brightness 255, contrast 255, hue 180, saturation 255
            result = await adjust_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
                brightness=255,
                contrast=255,
                hue_shift=180,
                saturation=255,
            )
            assert "Adjusted colors" in result


# ── invert_colors ─────────────────────────────────────────────────────────────


class TestInvertColors:
    @pytest.mark.asyncio
    async def test_path_traversal(self):
        from aseprite_mcp.tools.adjust import invert_colors

        result = await invert_colors(
            filename="../etc/passwd",
            layer_name="Layer 1",
            frame_index=1,
        )
        assert "Error" in result
        assert ".." in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.adjust import invert_colors

        with patch(
            "aseprite_mcp.tools.adjust.check_file",
            return_value="File not_found.ase not found",
        ):
            result = await invert_colors(
                filename="not_found.ase",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "not found" in result

    @pytest.mark.asyncio
    async def test_frame_index_less_than_1(self):
        from aseprite_mcp.tools.adjust import invert_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await invert_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=0,
            )
            assert "Error" in result
            assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.adjust import invert_colors

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await invert_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "Inverted colors" in result
            mock_cli.execute_lua_script.assert_called_once()
            script = mock_cli.execute_lua_script.call_args[0][0]
            assert "255 - r" in script
            assert "255 - g" in script
            assert "255 - b" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.adjust import invert_colors

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await invert_colors(
                filename="test.aseprite",
                layer_name="Layer 1",
                frame_index=1,
            )
            assert "Failed" in result


# ── flatten_layers ────────────────────────────────────────────────────────────


class TestFlattenLayers:
    @pytest.mark.asyncio
    async def test_path_traversal(self):
        from aseprite_mcp.tools.adjust import flatten_layers

        result = await flatten_layers(filename="../etc/passwd")
        assert "Error" in result
        assert ".." in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.adjust import flatten_layers

        with patch(
            "aseprite_mcp.tools.adjust.check_file",
            return_value="File not_found.ase not found",
        ):
            result = await flatten_layers(filename="not_found.ase")
            assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.adjust import flatten_layers

        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await flatten_layers(filename="test.aseprite")
            assert "Flattened all layers" in result
            mock_cli.execute_lua_script.assert_called_once()
            script = mock_cli.execute_lua_script.call_args[0][0]
            assert "FlattenLayers" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.adjust import flatten_layers

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.adjust.check_file", return_value=None):
            result = await flatten_layers(filename="test.aseprite")
            assert "Failed" in result
