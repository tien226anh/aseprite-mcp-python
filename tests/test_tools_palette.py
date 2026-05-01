"""Tests for aseprite_mcp.tools.palette module."""

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
    with patch("aseprite_mcp.tools.palette.get_cli", return_value=mock_cli):
        yield mock_cli


class TestGetPalette:
    @pytest.mark.asyncio
    async def test_get_palette_file_not_found(self):
        from aseprite_mcp.tools.palette import get_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value="File missing"):
            result = await get_palette(filename="missing.ase")
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_get_palette_success(self, mock_cli):
        from aseprite_mcp.tools.palette import get_palette

        mock_cli.execute_lua_script.return_value = (
            True,
            '["#ff0000", "#00ff00", "#0000ff"]',
        )
        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await get_palette(filename="test.ase")
        assert "palette" in result.lower() or "ff0000" in result


class TestSetPalette:
    @pytest.mark.asyncio
    async def test_set_palette_empty_colors(self):
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await set_palette(filename="test.ase", colors=[])
        assert "Error" in result
        assert "empty" in result.lower()

    @pytest.mark.asyncio
    async def test_set_palette_invalid_color(self):
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await set_palette(
                filename="test.ase", colors=["#ff0000", "invalid"]
            )
        assert "Error" in result
        assert "invalid" in result.lower()

    @pytest.mark.asyncio
    async def test_set_palette_file_not_found(self):
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value="File missing"):
            result = await set_palette(
                filename="missing.ase", colors=["#ff0000"]
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_set_palette_success(self, mock_cli):
        from aseprite_mcp.tools.palette import set_palette

        with patch("aseprite_mcp.tools.palette.check_file", return_value=None):
            result = await set_palette(
                filename="test.ase", colors=["#ff0000", "#00ff00", "#0000ff"]
            )
        assert "3 colors" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "Palette(3)" in script