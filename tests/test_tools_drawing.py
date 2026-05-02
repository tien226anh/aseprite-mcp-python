"""Tests for aseprite_mcp.tools.drawing module."""

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
    with patch("aseprite_mcp.tools.drawing.get_cli", return_value=mock_cli):
        yield mock_cli


# ---------------------------------------------------------------------------
# draw_pixels
# ---------------------------------------------------------------------------


class TestDrawPixels:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels(
                filename="test.ase",
                pixels=[{"x": 0, "y": 0, "color": "bad"}],
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_pixels(
                filename="missing.ase", pixels=[{"x": 0, "y": 0}]
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_invalid_alpha(self):
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels(
                filename="test.ase",
                pixels=[{"x": 0, "y": 0}],
                alpha=300,
            )
        assert "Error" in result
        assert "alpha" in result

    @pytest.mark.asyncio
    async def test_per_pixel_alpha_invalid(self):
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels(
                filename="test.ase",
                pixels=[{"x": 0, "y": 0, "color": "#ff0000", "alpha": 999}],
            )
        assert "Error" in result
        assert "per-pixel alpha" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_pixels

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels(
                filename="test.ase",
                pixels=[{"x": 5, "y": 10, "color": "#ff0000"}],
            )
        assert "Pixels drawn successfully" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "putPixel" in script
        assert "ox" in script
        assert "oy" in script


# ---------------------------------------------------------------------------
# draw_line
# ---------------------------------------------------------------------------


class TestDrawLine:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_line

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line(
                filename="test.ase", x1=0, y1=0, x2=10, y2=10, color="xyz"
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_invalid_alpha(self):
        from aseprite_mcp.tools.drawing import draw_line

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line(
                filename="test.ase", x1=0, y1=0, x2=10, y2=10, alpha=-1
            )
        assert "Error" in result
        assert "alpha" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_line

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line(
                filename="test.ase",
                x1=0,
                y1=0,
                x2=10,
                y2=10,
                color="#00ff00",
                alpha=200,
            )
        assert "Line drawn successfully" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "draw_line" in script
        assert "ox" in script
        assert "oy" in script
        assert "200" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_line

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line(
                filename="test.ase", x1=0, y1=0, x2=10, y2=10
            )
        assert "Failed" in result


# ---------------------------------------------------------------------------
# draw_rectangle
# ---------------------------------------------------------------------------


class TestDrawRectangle:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_rectangle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle(
                filename="test.ase", x=0, y=0, width=10, height=10, color="bad"
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_rectangle

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_rectangle(
                filename="missing.ase", x=0, y=0, width=10, height=10
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_rectangle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle(
                filename="test.ase", x=5, y=5, width=20, height=15
            )
        assert "Rectangle drawn successfully" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "rectangle" in script

    @pytest.mark.asyncio
    async def test_fill_mode(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_rectangle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle(
                filename="test.ase", x=0, y=0, width=10, height=10, fill=True
            )
        assert "Rectangle drawn successfully" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "filled_rectangle" in script


# ---------------------------------------------------------------------------
# draw_circle
# ---------------------------------------------------------------------------


class TestDrawCircle:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_circle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius=5,
                color="xxx",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_circle

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_circle(
                filename="missing.ase", center_x=10, center_y=10, radius=5
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_circle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle(
                filename="test.ase",
                center_x=16,
                center_y=16,
                radius=8,
                color="#ff0000",
            )
        assert "Circle drawn successfully" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "ellipse" in script
        # Verify points: center-radius and center+radius
        assert "Point(8, 8)" in script
        assert "Point(24, 24)" in script

    @pytest.mark.asyncio
    async def test_filled(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_circle

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_circle(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius=5,
                fill=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "filled_ellipse" in script


# ---------------------------------------------------------------------------
# draw_ellipse
# ---------------------------------------------------------------------------


class TestDrawEllipse:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_ellipse

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_ellipse(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius_x=8,
                radius_y=4,
                color="badcolor",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_ellipse

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_ellipse(
                filename="missing.ase",
                center_x=10,
                center_y=10,
                radius_x=8,
                radius_y=4,
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_invalid_alpha(self):
        from aseprite_mcp.tools.drawing import draw_ellipse

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_ellipse(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius_x=8,
                radius_y=4,
                alpha=300,
            )
        assert "Error" in result
        assert "alpha" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_ellipse

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_ellipse(
                filename="test.ase",
                center_x=20,
                center_y=15,
                radius_x=10,
                radius_y=5,
                color="#00ff00",
                alpha=180,
            )
        assert "Ellipse drawn successfully" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "ellipse" in script
        # Verify separate radii produce different points
        assert "Point(10, 10)" in script  # 20-10, 15-5
        assert "Point(30, 20)" in script  # 20+10, 15+5
        assert "180" in script
        assert "Color(0, 255, 0, 180)" in script

    @pytest.mark.asyncio
    async def test_filled_mode(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_ellipse

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_ellipse(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius_x=6,
                radius_y=3,
                fill=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "filled_ellipse" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_ellipse

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_ellipse(
                filename="test.ase",
                center_x=10,
                center_y=10,
                radius_x=5,
                radius_y=5,
            )
        assert "Failed" in result


# ---------------------------------------------------------------------------
# fill_area
# ---------------------------------------------------------------------------


class TestFillArea:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import fill_area

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area(
                filename="test.ase", x=5, y=5, color="bad"
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import fill_area

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await fill_area(filename="missing.ase", x=5, y=5)
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import fill_area

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area(
                filename="test.ase", x=5, y=5, color="#0000ff"
            )
        assert "Area filled" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "paint_bucket" in script


# ---------------------------------------------------------------------------
# draw_pixels_at
# ---------------------------------------------------------------------------


class TestDrawPixelsAt:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                pixels=[{"x": 0, "y": 0, "color": "zzz"}],
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_pixels_at(
                filename="missing.ase",
                layer_name="BG",
                frame_index=1,
                pixels=[{"x": 0, "y": 0}],
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_pixels_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=2,
                pixels=[{"x": 3, "y": 7, "color": "#ff0000"}],
            )
        assert "Pixels drawn" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "BG" in script
        assert "putPixel" in script
        assert "ox" in script

    @pytest.mark.asyncio
    async def test_create_if_missing(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_pixels_at(
                filename="test.ase",
                layer_name="NewLayer",
                frame_index=1,
                pixels=[{"x": 0, "y": 0, "color": "#ff0000"}],
                create_if_missing=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "newCel" in script

    @pytest.mark.asyncio
    async def test_no_create_if_missing(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_pixels_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_pixels_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                pixels=[{"x": 0, "y": 0, "color": "#ff0000"}],
                create_if_missing=False,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "false" in script


# ---------------------------------------------------------------------------
# draw_line_at
# ---------------------------------------------------------------------------


class TestDrawLineAt:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_line_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x1=0,
                y1=0,
                x2=10,
                y2=10,
                color="xxx",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_invalid_alpha(self):
        from aseprite_mcp.tools.drawing import draw_line_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x1=0,
                y1=0,
                x2=10,
                y2=10,
                alpha=500,
            )
        assert "Error" in result
        assert "alpha" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_line_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_line_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x1=0,
                y1=0,
                x2=10,
                y2=10,
                color="#ffffff",
                alpha=128,
            )
        assert "Line drawn" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "draw_line" in script
        assert "128" in script


# ---------------------------------------------------------------------------
# draw_rectangle_at
# ---------------------------------------------------------------------------


class TestDrawRectangleAt:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_rectangle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                color="bad",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_rectangle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_rectangle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=20,
                height=10,
            )
        assert "Rectangle drawn" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "rectangle" in script

    @pytest.mark.asyncio
    async def test_fill(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_rectangle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_rectangle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                fill=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "filled_rectangle" in script


# ---------------------------------------------------------------------------
# draw_circle_at
# ---------------------------------------------------------------------------


class TestDrawCircleAt:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_circle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                center_x=10,
                center_y=10,
                radius=5,
                color="zzz",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_circle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_circle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                center_x=16,
                center_y=16,
                radius=8,
            )
        assert "Circle drawn" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "ellipse" in script
        assert "Point(8, 8)" in script
        assert "Point(24, 24)" in script

    @pytest.mark.asyncio
    async def test_fill(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_circle_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_circle_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                center_x=10,
                center_y=10,
                radius=5,
                fill=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "filled_ellipse" in script


# ---------------------------------------------------------------------------
# fill_area_at
# ---------------------------------------------------------------------------


class TestFillAreaAt:
    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import fill_area_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=5,
                y=5,
                color="bad",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import fill_area_at

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await fill_area_at(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=5,
                y=5,
            )
        assert "Area filled" in result
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "paint_bucket" in script


# ---------------------------------------------------------------------------
# draw_polygon
# ---------------------------------------------------------------------------


class TestDrawPolygon:
    @pytest.mark.asyncio
    async def test_too_few_points(self):
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_polygon(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[{"x": 0, "y": 0}, {"x": 1, "y": 1}],
                color="#ff0000",
            )
        assert "3 points" in result

    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_polygon(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[
                    {"x": 0, "y": 0},
                    {"x": 10, "y": 0},
                    {"x": 5, "y": 10},
                ],
                color="bad",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_polygon(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[
                    {"x": 0, "y": 0},
                    {"x": 10, "y": 0},
                    {"x": 5, "y": 10},
                ],
                color="#ff0000",
            )
        assert "Polygon drawn" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "draw_line" in script
        assert "ox" in script

    @pytest.mark.asyncio
    async def test_filled(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_polygon

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_polygon(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[
                    {"x": 0, "y": 0},
                    {"x": 10, "y": 0},
                    {"x": 5, "y": 10},
                ],
                fill=True,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "fill_polygon" in script


# ---------------------------------------------------------------------------
# draw_path
# ---------------------------------------------------------------------------


class TestDrawPath:
    @pytest.mark.asyncio
    async def test_too_few_points(self):
        from aseprite_mcp.tools.drawing import draw_path

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_path(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[{"x": 0, "y": 0}],
            )
        assert "2 points" in result

    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_path

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_path(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[{"x": 0, "y": 0}, {"x": 10, "y": 10}],
                color="bad",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_path

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_path(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                points=[{"x": 0, "y": 0}, {"x": 10, "y": 10}, {"x": 20, "y": 5}],
                color="#00ff00",
                thickness=2,
            )
        assert "Path drawn" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "draw_line" in script
        assert "ox" in script
        assert "2" in script  # thickness


# ---------------------------------------------------------------------------
# apply_gradient_rect
# ---------------------------------------------------------------------------


class TestApplyGradientRect:
    @pytest.mark.asyncio
    async def test_width_zero(self):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=0,
                height=10,
                color_start="#ff0000",
                color_end="#0000ff",
            )
        assert "Width" in result or "> 0" in result

    @pytest.mark.asyncio
    async def test_height_zero(self):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=0,
                color_start="#ff0000",
                color_end="#0000ff",
            )
        assert "height" in result.lower() or "> 0" in result

    @pytest.mark.asyncio
    async def test_invalid_color_start(self):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                color_start="bad",
                color_end="#0000ff",
            )
        assert "Invalid" in result and "color_start" in result

    @pytest.mark.asyncio
    async def test_invalid_color_end(self):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                color_start="#ff0000",
                color_end="bad",
            )
        assert "Invalid" in result and "color_end" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=5,
                color_start="#ff0000",
                color_end="#0000ff",
                alpha=200,
            )
        assert "Gradient applied" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "putPixel" in script
        assert "ox" in script
        assert "200" in script

    @pytest.mark.asyncio
    async def test_vertical_gradient(self, mock_cli):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                color_start="#ff0000",
                color_end="#0000ff",
                horizontal=False,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "false" in script  # horiz_flag

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await apply_gradient_rect(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                width=10,
                height=10,
                color_start="#ff0000",
                color_end="#0000ff",
            )
        assert "Failed" in result


# ---------------------------------------------------------------------------
# draw_text
# ---------------------------------------------------------------------------


class TestDrawText:
    @pytest.mark.asyncio
    async def test_empty_text(self):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="",
            )
        assert "Error" in result
        assert "text" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.drawing import draw_text

        with patch(
            "aseprite_mcp.tools.drawing.check_file",
            return_value="File not found",
        ):
            result = await draw_text(
                filename="missing.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="Hello",
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_invalid_color(self):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="Hello",
                color="badcolor",
            )
        assert "Invalid color" in result

    @pytest.mark.asyncio
    async def test_invalid_alpha(self):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="Hello",
                alpha=300,
            )
        assert "Error" in result
        assert "alpha" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=10,
                y=20,
                text="Hello World",
                color="#ffffff",
                alpha=255,
            )
        assert "Text drawn" in result
        mock_cli.execute_lua_script.assert_called_once()
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert 'tool="text"' in script
        assert "Hello World" in script
        assert "Point(10, 20)" in script
        assert "Color(255, 255, 255, 255)" in script

    @pytest.mark.asyncio
    async def test_lua_escape_used(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text='He said "hello"',
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        # _lua_escape should escape double quotes
        assert '\\"' in script

    @pytest.mark.asyncio
    async def test_layer_name_escaped(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_text(
                filename="test.ase",
                layer_name='Layer "test"',
                frame_index=1,
                x=0,
                y=0,
                text="Hi",
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        # Layer name should be escaped
        assert "Layer \\" in script or "Layer%_" in script

    @pytest.mark.asyncio
    async def test_create_if_missing_false(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_text

        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="Hello",
                create_if_missing=False,
            )
        script = mock_cli.execute_lua_script.call_args[0][0]
        assert "false" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_cli):
        from aseprite_mcp.tools.drawing import draw_text

        mock_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.drawing.check_file", return_value=None):
            result = await draw_text(
                filename="test.ase",
                layer_name="BG",
                frame_index=1,
                x=0,
                y=0,
                text="Hello",
            )
        assert "Failed" in result


# ---------------------------------------------------------------------------
# clear_cel_image (in animation.py)
# ---------------------------------------------------------------------------


class TestClearCelImage:
    @pytest.fixture
    def mock_anim_cli(self):
        cli = MagicMock(spec=AsepriteCLI)
        cli.execute_lua_script.return_value = (True, "Success")
        return cli

    @pytest.fixture(autouse=True)
    def patch_anim_get_cli(self, mock_anim_cli):
        with patch(
            "aseprite_mcp.tools.animation.get_cli", return_value=mock_anim_cli
        ):
            yield mock_anim_cli

    @pytest.mark.asyncio
    async def test_frame_less_than_one(self):
        from aseprite_mcp.tools.animation import clear_cel_image

        result = await clear_cel_image(
            filename="test.ase", layer_name="BG", frame_index=0
        )
        assert "Error" in result
        assert "frame_index" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        from aseprite_mcp.tools.animation import clear_cel_image

        with patch(
            "aseprite_mcp.tools.animation.check_file",
            return_value="File not found",
        ):
            result = await clear_cel_image(
                filename="missing.ase", layer_name="BG", frame_index=1
            )
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_success(self, mock_anim_cli):
        from aseprite_mcp.tools.animation import clear_cel_image

        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await clear_cel_image(
                filename="test.ase", layer_name="BG", frame_index=3
            )
        assert "Cleared cel image" in result
        assert "BG" in result
        mock_anim_cli.execute_lua_script.assert_called_once()
        script = mock_anim_cli.execute_lua_script.call_args[0][0]
        assert "cel.image:clear()" in script
        assert "transaction" in script

    @pytest.mark.asyncio
    async def test_failure(self, mock_anim_cli):
        from aseprite_mcp.tools.animation import clear_cel_image

        mock_anim_cli.execute_lua_script.return_value = (False, "Aseprite error")
        with patch("aseprite_mcp.tools.animation.check_file", return_value=None):
            result = await clear_cel_image(
                filename="test.ase", layer_name="BG", frame_index=1
            )
        assert "Failed" in result
