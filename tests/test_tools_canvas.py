"""Tests for aseprite_mcp.tools.canvas module."""

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
    with patch("aseprite_mcp.tools.canvas.get_cli", return_value=mock_cli):
        yield mock_cli


class TestCreateCanvas:
    @pytest.mark.asyncio
    async def test_create_canvas_invalid_width(self):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=0, height=32)
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_create_canvas_negative_width(self):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=-5, height=32)
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_create_canvas_invalid_height(self):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=32, height=0)
        assert "Error" in result
        assert "height" in result

    @pytest.mark.asyncio
    async def test_create_canvas_path_traversal(self):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=32, height=32, filename="../etc/passwd")
        assert ".." in result

    @pytest.mark.asyncio
    async def test_create_canvas_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=64, height=48, filename="test.aseprite")
        assert "Created canvas" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "Sprite(64, 48)" in script
        assert "test.aseprite" in script

    @pytest.mark.asyncio
    async def test_create_canvas_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import create_canvas

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        result = await create_canvas(width=32, height=32)
        assert "Failed" in result

    @pytest.mark.asyncio
    async def test_create_canvas_default_filename(self, mock_cli):
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=32, height=32)
        assert "Created canvas" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "canvas.aseprite" in script


class TestAddLayer:
    @pytest.mark.asyncio
    async def test_add_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value="File not found"):
            result = await add_layer(filename="nonexistent.ase", layer_name="Layer1")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_add_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import add_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_layer(filename="test.ase", layer_name="NewLayer")
        assert "Added layer" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "NewLayer" in script
        # Verify filename is passed as second arg
        assert mock_cli.execute_lua_script.call_args[0][1] == "test.ase"


class TestAddFrame:
    @pytest.mark.asyncio
    async def test_add_frame_file_not_found(self):
        from aseprite_mcp.tools.canvas import add_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value="File missing"):
            result = await add_frame(filename="missing.ase")
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_add_frame_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import add_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await add_frame(filename="test.ase")
        assert "Added" in result
        mock_cli.execute_lua_script.assert_called_once()


class TestSetFrame:
    @pytest.mark.asyncio
    async def test_set_frame_invalid_index(self):
        from aseprite_mcp.tools.canvas import set_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame(filename="test.ase", frame_index=0)
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_set_frame_negative_index(self):
        from aseprite_mcp.tools.canvas import set_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame(filename="test.ase", frame_index=-1)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_set_frame_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_frame

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_frame(filename="test.ase", frame_index=2)
        assert "Set active frame to 2" in result
        mock_cli.execute_lua_script.assert_called_once()


class TestSetLayer:
    @pytest.mark.asyncio
    async def test_set_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import set_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value="File not found"):
            result = await set_layer(filename="missing.ase", layer_name="BG")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_set_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer(filename="test.ase", layer_name="Layer1")
        assert "Set active layer" in result
        mock_cli.execute_lua_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_layer_create_if_missing(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer(
                filename="test.ase", layer_name="NewLayer", create_if_missing=True
            )
        assert "Set active layer" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "newLayer" in script