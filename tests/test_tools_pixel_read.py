"""Tests for aseprite_mcp.tools.pixel_read module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI


@pytest.fixture
def mock_cli():
    """Create a mock AsepriteCLI with execute_lua_script returning success."""
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "PIXEL:255,0,0,128")
    return cli


@pytest.fixture(autouse=True)
def patch_get_cli(mock_cli):
    """Patch get_cli to return our mock for all tests in this module."""
    with patch("aseprite_mcp.tools.pixel_read.get_cli", return_value=mock_cli):
        yield mock_cli


class TestGetPixelColor:
    @pytest.mark.asyncio
    async def test_get_pixel_color_file_not_found(self):
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        with patch(
            "aseprite_mcp.tools.pixel_read.check_file", return_value="File missing"
        ):
            result = await get_pixel_color(filename="missing.ase", x=5, y=10)
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_get_pixel_color_invalid_frame_index(self):
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixel_color(filename="test.ase", x=0, y=0, frame_index=0)
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_get_pixel_color_success(self, mock_cli):
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        mock_cli.execute_lua_script.return_value = (
            True,
            "PIXEL:255,0,0,128",
        )
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixel_color(filename="test.ase", x=5, y=10)
        assert "#ff0000" in result
        mock_cli.execute_lua_script.assert_called_once()
        # Verify filename passed as second arg
        assert mock_cli.execute_lua_script.call_args[0][1] == "test.ase"

    @pytest.mark.asyncio
    async def test_get_pixel_color_failure(self, mock_cli):
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixel_color(filename="test.ase", x=0, y=0)
        assert "Failed" in result

    @pytest.mark.asyncio
    async def test_get_pixel_color_with_layer_name(self, mock_cli):
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        mock_cli.execute_lua_script.return_value = (
            True,
            "PIXEL:100,200,50,255",
        )
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            await get_pixel_color(
                filename="test.ase", x=0, y=0, layer_name="BG"
            )
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "BG" in script


class TestGetPixelsRect:
    @pytest.mark.asyncio
    async def test_get_pixels_rect_file_not_found(self):
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        with patch(
            "aseprite_mcp.tools.pixel_read.check_file", return_value="File missing"
        ):
            result = await get_pixels_rect(
                filename="missing.ase", x=0, y=0, width=10, height=10
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_invalid_width(self):
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="test.ase", x=0, y=0, width=0, height=10
            )
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_invalid_height(self):
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="test.ase", x=0, y=0, width=10, height=-5
            )
        assert "Error" in result
        assert "height" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_invalid_frame_index(self):
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="test.ase", x=0, y=0, width=10, height=10, frame_index=0
            )
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_success(self, mock_cli):
        import json

        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        mock_cli.execute_lua_script.return_value = (
            True,
            "PIXEL:0,0,255,0,0,255\nPIXEL:1,0,0,255,0,255",
        )
        with patch("aseprite_mcp.tools.pixel_read.check_file", return_value=None):
            result = await get_pixels_rect(
                filename="test.ase", x=0, y=0, width=2, height=1
            )
        parsed = json.loads(result)
        assert "pixels" in parsed
        assert parsed["count"] == 2
