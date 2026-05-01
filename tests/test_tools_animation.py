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

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File test.ase not found",
        ):
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

        with patch(
            "aseprite_mcp.tools.animation.check_file", return_value="File missing"
        ):
            result = await set_layer_visibility(
                filename="missing.ase", layer_name="BG", visible=True
            )
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

        with patch(
            "aseprite_mcp.tools.animation.check_file", return_value="File missing"
        ):
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

        with patch(
            "aseprite_mcp.tools.animation.check_file", return_value="File missing"
        ):
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
                filename="test.ase",
                name="walk",
                from_frame=1,
                to_frame=4,
                direction="sideways",
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

        with patch(
            "aseprite_mcp.tools.animation.check_file", return_value="File missing"
        ):
            result = await set_tag(
                filename="missing.ase", name="walk", from_frame=1, to_frame=4
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_set_tag_success(self, mock_cli):
        from aseprite_mcp.tools.animation import set_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await set_tag(
                filename="test.ase",
                name="walk",
                from_frame=1,
                to_frame=4,
                direction="forward",
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


class TestDeleteFrames:
    @pytest.mark.asyncio
    async def test_delete_frames_start_zero(self):
        from aseprite_mcp.tools.animation import delete_frames

        result = await delete_frames(filename="test.ase", start_frame=0, end_frame=3)
        assert "Error" in result
        assert "start_frame" in result

    @pytest.mark.asyncio
    async def test_delete_frames_negative_start(self):
        from aseprite_mcp.tools.animation import delete_frames

        result = await delete_frames(filename="test.ase", start_frame=-1, end_frame=3)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_delete_frames_end_before_start(self):
        from aseprite_mcp.tools.animation import delete_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_frames(filename="test.ase", start_frame=5, end_frame=2)
        assert "Error" in result
        assert "end_frame" in result

    @pytest.mark.asyncio
    async def test_delete_frames_path_traversal(self):
        from aseprite_mcp.tools.animation import delete_frames

        result = await delete_frames(filename="../etc/passwd", start_frame=1, end_frame=3)
        assert ".." in result

    @pytest.mark.asyncio
    async def test_delete_frames_file_not_found(self):
        from aseprite_mcp.tools.animation import delete_frames

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File test.ase not found",
        ):
            result = await delete_frames(filename="test.ase", start_frame=1, end_frame=3)
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_delete_frames_success(self, mock_cli):
        from aseprite_mcp.tools.animation import delete_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_frames(filename="test.ase", start_frame=2, end_frame=4)
        assert "Deleted frames 2-4" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "deleteFrame" in script
        # Must iterate backwards
        assert "for i = 4, 2, -1 do" in script

    @pytest.mark.asyncio
    async def test_delete_frames_single_frame(self, mock_cli):
        from aseprite_mcp.tools.animation import delete_frames

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_frames(filename="test.ase", start_frame=3, end_frame=3)
        assert "Deleted frames 3-3" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "for i = 3, 3, -1 do" in script

    @pytest.mark.asyncio
    async def test_delete_frames_failure(self, mock_cli):
        from aseprite_mcp.tools.animation import delete_frames

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_frames(filename="test.ase", start_frame=1, end_frame=2)
        assert "Failed" in result


class TestDeleteTag:
    @pytest.mark.asyncio
    async def test_delete_tag_file_not_found(self):
        from aseprite_mcp.tools.animation import delete_tag

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File missing",
        ):
            result = await delete_tag(filename="missing.ase", name="walk")
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_delete_tag_success(self, mock_cli):
        from aseprite_mcp.tools.animation import delete_tag

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_tag(filename="test.ase", name="walk")
        assert "Deleted tag" in result
        assert "walk" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "deleteTag" in script

    @pytest.mark.asyncio
    async def test_delete_tag_failure(self, mock_cli):
        from aseprite_mcp.tools.animation import delete_tag

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await delete_tag(filename="test.ase", name="walk")
        assert "Failed" in result


class TestTweenCelRotation:
    @pytest.mark.asyncio
    async def test_invalid_easing(self):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_rotation(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_angle=0.0,
                end_angle=90.0,
                easing="bounce",
            )
        assert "Error" in result
        assert "easing" in result

    @pytest.mark.asyncio
    async def test_start_frame_zero(self):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        result = await tween_cel_rotation(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=0,
            end_frame=4,
            start_angle=0.0,
            end_angle=90.0,
        )
        assert "Error" in result
        assert "frame" in result.lower()

    @pytest.mark.asyncio
    async def test_end_frame_not_greater(self):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        result = await tween_cel_rotation(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=4,
            end_frame=4,
            start_angle=0.0,
            end_angle=90.0,
        )
        assert "Error" in result
        assert "end_frame" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File missing",
        ):
            result = await tween_cel_rotation(
                filename="missing.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_angle=0.0,
                end_angle=90.0,
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_success_default_pivot(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_rotation(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_angle=0.0,
                end_angle=90.0,
            )
        assert "Tweened cel rotation" in result
        assert "linear" in result
        assert "Layer1" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "rotate_image" in script
        assert "autoPivot = true" in script
        assert "ease(t)" in script

    @pytest.mark.asyncio
    async def test_success_custom_pivot_and_easing(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_rotation(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=8,
                start_angle=0.0,
                end_angle=360.0,
                pivot_x=16,
                pivot_y=16,
                easing="smoothstep",
                create_missing_cels=True,
                source_frame_index=2,
            )
        assert "Tweened cel rotation" in result
        assert "smoothstep" in result
        assert "360" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "rotate_image" in script
        assert "autoPivot = false" in script
        assert "gPivotX = 16" in script
        assert "gPivotY = 16" in script
        assert "t * t * (3 - 2 * t)" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_rotation

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_rotation(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_angle=0.0,
                end_angle=90.0,
            )
        assert "Failed" in result


class TestTweenCelScale:
    @pytest.mark.asyncio
    async def test_invalid_easing(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_scale(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_scale=1.0,
                end_scale=2.0,
                easing="elastic",
            )
        assert "Error" in result
        assert "easing" in result

    @pytest.mark.asyncio
    async def test_start_scale_zero(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=1,
            end_frame=4,
            start_scale=0.0,
            end_scale=2.0,
        )
        assert "Error" in result
        assert "start_scale" in result

    @pytest.mark.asyncio
    async def test_start_scale_negative(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=1,
            end_frame=4,
            start_scale=-0.5,
            end_scale=2.0,
        )
        assert "Error" in result
        assert "start_scale" in result

    @pytest.mark.asyncio
    async def test_end_scale_zero(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=1,
            end_frame=4,
            start_scale=1.0,
            end_scale=0.0,
        )
        assert "Error" in result
        assert "end_scale" in result

    @pytest.mark.asyncio
    async def test_end_scale_negative(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=1,
            end_frame=4,
            start_scale=1.0,
            end_scale=-1.0,
        )
        assert "Error" in result
        assert "end_scale" in result

    @pytest.mark.asyncio
    async def test_frame_indices_invalid(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=0,
            end_frame=4,
            start_scale=1.0,
            end_scale=2.0,
        )
        assert "Error" in result
        assert "frame" in result.lower()

    @pytest.mark.asyncio
    async def test_end_frame_not_greater(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        result = await tween_cel_scale(
            filename="test.ase",
            layer_name="Layer1",
            start_frame=4,
            end_frame=4,
            start_scale=1.0,
            end_scale=2.0,
        )
        assert "Error" in result
        assert "end_frame" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.animation import tween_cel_scale

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File missing",
        ):
            result = await tween_cel_scale(
                filename="missing.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_scale=1.0,
                end_scale=2.0,
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_success_default_pivot(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_scale

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_scale(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_scale=1.0,
                end_scale=2.0,
            )
        assert "Tweened cel scale" in result
        assert "linear" in result
        assert "Layer1" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "scale_image" in script
        assert "autoPivot = true" in script

    @pytest.mark.asyncio
    async def test_success_custom_pivot_and_easing(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_scale

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_scale(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=8,
                start_scale=0.5,
                end_scale=1.5,
                pivot_x=16,
                pivot_y=16,
                easing="ease_in_out",
                create_missing_cels=True,
                source_frame_index=2,
            )
        assert "Tweened cel scale" in result
        assert "ease_in_out" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "scale_image" in script
        assert "autoPivot = false" in script
        assert "gPivotX = 16" in script
        assert "gPivotY = 16" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.animation import tween_cel_scale

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await tween_cel_scale(
                filename="test.ase",
                layer_name="Layer1",
                start_frame=1,
                end_frame=4,
                start_scale=1.0,
                end_scale=2.0,
            )
        assert "Failed" in result
