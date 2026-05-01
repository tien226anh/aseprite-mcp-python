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

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
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

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
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


class TestDeleteLayer:
    @pytest.mark.asyncio
    async def test_delete_layer_path_traversal(self):
        from aseprite_mcp.tools.canvas import delete_layer

        result = await delete_layer(filename="../etc/passwd", layer_name="Layer1")
        assert ".." in result

    @pytest.mark.asyncio
    async def test_delete_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import delete_layer

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await delete_layer(filename="missing.ase", layer_name="Layer1")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_delete_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import delete_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await delete_layer(filename="test.ase", layer_name="Layer1")
        assert "Deleted layer" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "deleteLayer" in script

    @pytest.mark.asyncio
    async def test_delete_layer_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import delete_layer

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await delete_layer(filename="test.ase", layer_name="Layer1")
        assert "Failed" in result


class TestRenameLayer:
    @pytest.mark.asyncio
    async def test_rename_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import rename_layer

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await rename_layer(
                filename="missing.ase", layer_name="Old", new_name="New"
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_rename_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import rename_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await rename_layer(
                filename="test.ase", layer_name="Old", new_name="New"
            )
        assert "Renamed" in result
        assert "Old" in result
        assert "New" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert 'target.name = "New"' in script

    @pytest.mark.asyncio
    async def test_rename_layer_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import rename_layer

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await rename_layer(
                filename="test.ase", layer_name="Old", new_name="New"
            )
        assert "Failed" in result


class TestReorderLayer:
    @pytest.mark.asyncio
    async def test_reorder_layer_invalid_position(self):
        from aseprite_mcp.tools.canvas import reorder_layer

        result = await reorder_layer(
            filename="test.ase", layer_name="Layer1", position=0
        )
        assert "Error" in result
        assert "position" in result

    @pytest.mark.asyncio
    async def test_reorder_layer_negative_position(self):
        from aseprite_mcp.tools.canvas import reorder_layer

        result = await reorder_layer(
            filename="test.ase", layer_name="Layer1", position=-1
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_reorder_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import reorder_layer

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await reorder_layer(
                filename="missing.ase", layer_name="Layer1", position=1
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_reorder_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import reorder_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await reorder_layer(
                filename="test.ase", layer_name="Layer1", position=2
            )
        assert "Moved layer" in result
        assert "position 2" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "stackIndex" in script
        assert "2" in script

    @pytest.mark.asyncio
    async def test_reorder_layer_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import reorder_layer

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await reorder_layer(
                filename="test.ase", layer_name="Layer1", position=2
            )
        assert "Failed" in result


class TestDuplicateLayer:
    @pytest.mark.asyncio
    async def test_duplicate_layer_path_traversal(self):
        from aseprite_mcp.tools.canvas import duplicate_layer

        result = await duplicate_layer(
            filename="../etc/passwd", layer_name="Layer1", new_layer_name="Copy"
        )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_duplicate_layer_file_not_found(self):
        from aseprite_mcp.tools.canvas import duplicate_layer

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await duplicate_layer(
                filename="missing.ase", layer_name="Layer1", new_layer_name="Copy"
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_duplicate_layer_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import duplicate_layer

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await duplicate_layer(
                filename="test.ase", layer_name="Layer1", new_layer_name="Layer1_Copy"
            )
        assert "Duplicated" in result
        assert "Layer1" in result
        assert "Layer1_Copy" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "newLayer" in script
        assert "Image(srcCel.image)" in script

    @pytest.mark.asyncio
    async def test_duplicate_layer_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import duplicate_layer

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await duplicate_layer(
                filename="test.ase", layer_name="Layer1", new_layer_name="Copy"
            )
        assert "Failed" in result


class TestMergeLayerDown:
    @pytest.mark.asyncio
    async def test_merge_layer_down_path_traversal(self):
        from aseprite_mcp.tools.canvas import merge_layer_down

        result = await merge_layer_down(
            filename="../etc/passwd", layer_name="Layer1"
        )
        assert ".." in result

    @pytest.mark.asyncio
    async def test_merge_layer_down_file_not_found(self):
        from aseprite_mcp.tools.canvas import merge_layer_down

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await merge_layer_down(
                filename="missing.ase", layer_name="Layer1"
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_merge_layer_down_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import merge_layer_down

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await merge_layer_down(
                filename="test.ase", layer_name="Layer1"
            )
        assert "Merged" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "MergeDownLayer" in script

    @pytest.mark.asyncio
    async def test_merge_layer_down_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import merge_layer_down

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await merge_layer_down(
                filename="test.ase", layer_name="Layer1"
            )
        assert "Failed" in result


class TestSetLayerBlendMode:
    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_invalid_mode(self):
        from aseprite_mcp.tools.canvas import set_layer_blend_mode

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer_blend_mode(
                filename="test.ase", layer_name="Layer1", blend_mode="invalid"
            )
        assert "Error" in result
        assert "blend_mode" in result

    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_file_not_found(self):
        from aseprite_mcp.tools.canvas import set_layer_blend_mode

        with patch(
            "aseprite_mcp.tools.canvas.check_file", return_value="File not found"
        ):
            result = await set_layer_blend_mode(
                filename="missing.ase", layer_name="Layer1", blend_mode="multiply"
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_success(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_layer_blend_mode

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer_blend_mode(
                filename="test.ase", layer_name="Layer1", blend_mode="multiply"
            )
        assert "blend mode" in result
        assert "multiply" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "BlendMode.MULTIPLY" in script

    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_default_normal(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_layer_blend_mode

        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer_blend_mode(
                filename="test.ase", layer_name="Layer1"
            )
        assert "normal" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "BlendMode.NORMAL" in script

    @pytest.mark.asyncio
    async def test_set_layer_blend_mode_failure(self, mock_cli):
        from aseprite_mcp.tools.canvas import set_layer_blend_mode

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.canvas.check_file", return_value=None):
            result = await set_layer_blend_mode(
                filename="test.ase", layer_name="Layer1", blend_mode="screen"
            )
        assert "Failed" in result
