"""Tests for aseprite_mcp.tools.transform module."""

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
    with patch("aseprite_mcp.tools.transform.get_cli", return_value=mock_cli):
        yield mock_cli


class TestFlipLayer:
    @pytest.mark.asyncio
    async def test_flip_layer_invalid_direction(self):
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                direction="diagonal",
            )
        assert "Error" in result
        assert "direction" in result

    @pytest.mark.asyncio
    async def test_flip_layer_file_not_found(self):
        from aseprite_mcp.tools.transform import flip_layer

        with patch(
            "aseprite_mcp.tools.transform.check_file", return_value="File missing"
        ):
            result = await flip_layer(
                filename="missing.ase", layer_name="BG", frame_index=1
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_flip_layer_invalid_frame_index(self):
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="test.ase", layer_name="BG", frame_index=0
            )
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_flip_layer_path_traversal(self):
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="../etc/test.ase", layer_name="BG", frame_index=1
            )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_flip_layer_horizontal_success(self, mock_cli):
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                direction="horizontal",
            )
        assert "Flipped" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "horizontal" in script.lower() or "w - 1 - x" in script

    @pytest.mark.asyncio
    async def test_flip_layer_vertical_success(self, mock_cli):
        from aseprite_mcp.tools.transform import flip_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await flip_layer(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                direction="vertical",
            )
        assert "Flipped" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "h - 1 - y" in script


class TestRotateLayer:
    @pytest.mark.asyncio
    async def test_rotate_layer_invalid_angle(self):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="test.ase", layer_name="BG", frame_index=1, angle=45
            )
        assert "Error" in result
        assert "angle" in result

    @pytest.mark.asyncio
    async def test_rotate_layer_invalid_frame_index(self):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="test.ase", layer_name="BG", frame_index=0, angle=90
            )
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_rotate_layer_file_not_found(self):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch(
            "aseprite_mcp.tools.transform.check_file", return_value="File missing"
        ):
            result = await rotate_layer(
                filename="missing.ase", layer_name="BG", frame_index=1
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_rotate_layer_path_traversal(self):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="../secret/test.ase", layer_name="BG", frame_index=1
            )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_rotate_layer_success_90(self, mock_cli):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="test.ase", layer_name="BG", frame_index=1, angle=90
            )
        assert "Rotated" in result
        mock_cli.execute_lua_script.assert_called_once()

    @pytest.mark.asyncio
    async def test_rotate_layer_success_180(self, mock_cli):
        from aseprite_mcp.tools.transform import rotate_layer

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await rotate_layer(
                filename="test.ase", layer_name="BG", frame_index=1, angle=180
            )
        assert "Rotated" in result


class TestResizeCanvas:
    @pytest.mark.asyncio
    async def test_resize_canvas_invalid_width(self):
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(filename="test.ase", width=0, height=32)
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_invalid_height(self):
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(filename="test.ase", width=32, height=-5)
        assert "Error" in result
        assert "height" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_path_traversal(self):
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(filename="../secret.ase", width=32, height=32)
        assert ".." in result

    @pytest.mark.asyncio
    async def test_resize_canvas_file_not_found(self):
        from aseprite_mcp.tools.transform import resize_canvas

        with patch(
            "aseprite_mcp.tools.transform.check_file", return_value="File missing"
        ):
            result = await resize_canvas(filename="missing.ase", width=64, height=64)
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_success(self, mock_cli):
        from aseprite_mcp.tools.transform import resize_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await resize_canvas(filename="test.ase", width=64, height=48)
        assert "Resized" in result
        mock_cli.execute_lua_script.assert_called_once()


class TestCropCanvas:
    @pytest.mark.asyncio
    async def test_crop_canvas_invalid_width(self):
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="test.ase", x=0, y=0, width=0, height=10
            )
        assert "Error" in result
        assert "width" in result

    @pytest.mark.asyncio
    async def test_crop_canvas_invalid_height(self):
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="test.ase", x=0, y=0, width=10, height=-5
            )
        assert "Error" in result
        assert "height" in result

    @pytest.mark.asyncio
    async def test_crop_canvas_path_traversal(self):
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="../secret.ase", x=0, y=0, width=10, height=10
            )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_crop_canvas_file_not_found(self):
        from aseprite_mcp.tools.transform import crop_canvas

        with patch(
            "aseprite_mcp.tools.transform.check_file", return_value="File missing"
        ):
            result = await crop_canvas(
                filename="missing.ase", x=0, y=0, width=10, height=10
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_crop_canvas_success(self, mock_cli):
        from aseprite_mcp.tools.transform import crop_canvas

        with patch("aseprite_mcp.tools.transform.check_file", return_value=None):
            result = await crop_canvas(
                filename="test.ase", x=5, y=5, width=20, height=20
            )
        assert "Cropped" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "crop" in script.lower()
