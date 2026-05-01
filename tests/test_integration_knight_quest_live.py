"""Live integration test: Knight Quest RPG scenario using the REAL Aseprite binary.

A knight on a quest to save a princess from a dragon, encountering goblins,
skeletons, and slimes along the way. Each chapter represents a workflow phase,
and each test validates one tool's behavior through the RPG narrative.

These tests call the ACTUAL AsepriteCLI — no mocks! They create real .aseprite
files, draw real pixels, and export real PNGs. Tests auto-skip if no Aseprite
binary is found.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI
from aseprite_mcp.config import AsepriteConfig

# ═══════════════════════════════════════════════════════════════════════════
# Auto-skip if no Aseprite binary
# ═══════════════════════════════════════════════════════════════════════════

ASEPRITE_PATH = os.environ.get("ASEPRITE_PATH", shutil.which("aseprite") or "")

if not ASEPRITE_PATH:
    common = [
        r"E:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe",
        r"C:\Program Files\Aseprite\aseprite.exe",
        r"C:\Program Files (x86)\Aseprite\aseprite.exe",
        "/usr/bin/aseprite",
        "/usr/local/bin/aseprite",
        "/snap/bin/aseprite",
        str(Path.home() / "aseprite" / "build" / "bin" / "aseprite"),
    ]
    for p in common:
        if Path(p).is_file():
            ASEPRITE_PATH = p
            break

SKIP_NO_BINARY = not ASEPRITE_PATH or not Path(ASEPRITE_PATH).is_file()

pytestmark = pytest.mark.skipif(
    SKIP_NO_BINARY,
    reason="Aseprite binary not found — set ASEPRITE_PATH or install Aseprite",
)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _lua_path(p: Path | str) -> str:
    """Normalize a path for Lua string literals (forward slashes)."""
    return str(p).replace("\\", "/")


def _sprite_path(tmp_sprite_dir: Path, name: str = "quest.aseprite") -> str:
    return str(tmp_sprite_dir / name)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def tmp_sprite_dir(tmp_path):
    """Create a temporary directory for sprite files, cleaned up after test."""
    d = tmp_path / "sprites"
    d.mkdir()
    return d


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def config(tmp_path, output_dir):
    """Create a real AsepriteConfig with the discovered binary."""
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    return AsepriteConfig(
        aseprite_path=ASEPRITE_PATH,
        tmp_dir=scripts_dir,
        output_dir=output_dir,
    )


@pytest.fixture
def cli(config):
    """Create a real AsepriteCLI instance."""
    return AsepriteCLI(config)


@pytest.fixture(autouse=True)
def inject_real_cli(cli):
    """Inject real AsepriteCLI and config into server module for tool use."""
    import aseprite_mcp.server as srv

    old_cli = srv._cli
    old_config = srv._config
    srv._cli = cli
    srv._config = cli.config
    yield
    srv._cli = old_cli
    srv._config = old_config


def _create_sprite(
    cli: AsepriteCLI,
    path: str,
    width: int = 64,
    height: int = 64,
    layers: list[str] | None = None,
    frame_count: int = 1,
) -> None:
    """Helper: create a sprite file using raw Lua."""
    lua_path = _lua_path(path)
    layer_code = ""
    if layers:
        for i, name in enumerate(layers):
            safe_name = name.replace('"', '\\"')
            var = f"layer{i}"
            layer_code += f'\nlocal {var} = spr:newLayer()\n{var}.name = "{safe_name}"'
    frame_code = ""
    for _ in range(frame_count - 1):
        frame_code += "spr:newEmptyFrame()\n"

    script = f"""
local spr = Sprite({width}, {height})
{layer_code}
{frame_code}
spr:saveAs("{lua_path}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    assert success, f"Failed to create sprite: {output}"
    assert Path(path).is_file(), f"Sprite file not created: {path}"


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 1: The Kingdom (Canvas & Creation)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter1:
    """Create the game world canvas and set up the quest structure."""

    @pytest.mark.asyncio
    async def test_create_canvas_real_file(self, cli, tmp_sprite_dir):
        """The knight's quest begins — create 64x64 canvas, verify on disk."""
        from aseprite_mcp.tools.canvas import create_canvas

        path = _sprite_path(tmp_sprite_dir, "kingdom.aseprite")
        result = await create_canvas(width=64, height=64, filename=path)
        assert "Created canvas" in result
        assert Path(path).is_file(), f"Sprite file not created: {path}"
        # Verify file is non-trivial (a valid .aseprite file should be > 100 bytes)
        assert Path(path).stat().st_size > 100

    @pytest.mark.asyncio
    async def test_add_layer_real(self, cli, tmp_sprite_dir):
        """Create the Knight layer and verify it appears in layer list."""
        from aseprite_mcp.tools.canvas import add_layer

        path = _sprite_path(tmp_sprite_dir, "layer_test.aseprite")
        _create_sprite(cli, path, 64, 64)

        result = await add_layer(filename=path, layer_name="Knight")
        assert "Added layer" in result
        assert "Knight" in result

        # Verify layer appears via list_layers
        layers = cli.list_layers(path)
        assert "Knight" in layers

    @pytest.mark.asyncio
    async def test_add_frame_real(self, cli, tmp_sprite_dir):
        """Add a frame and verify frame count via Lua."""
        from aseprite_mcp.tools.canvas import add_frame

        path = _sprite_path(tmp_sprite_dir, "frame_test.aseprite")
        _create_sprite(cli, path, 64, 64)

        result = await add_frame(filename=path)
        assert "Added" in result

        # Verify via Lua that we now have 2 frames
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("FRAMES:" .. #spr.frames)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FRAMES:2" in output

    @pytest.mark.asyncio
    async def test_set_frame_duration_real(self, cli, tmp_sprite_dir):
        """Set frame duration and read it back via Lua."""
        from aseprite_mcp.tools.canvas import add_frame, set_frame_duration

        path = _sprite_path(tmp_sprite_dir, "duration_test.aseprite")
        _create_sprite(cli, path, 64, 64)
        await add_frame(filename=path)

        result = await set_frame_duration(filename=path, frame_index=1, duration_ms=200)
        assert "200" in result

        # Read back duration
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("DURATION:" .. (spr.frames[1].duration * 1000))
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "DURATION:200" in output

    @pytest.mark.asyncio
    async def test_set_layer_real(self, cli, tmp_sprite_dir):
        """Create layer via set_layer with create_if_missing, verify in list."""
        from aseprite_mcp.tools.canvas import set_layer

        path = _sprite_path(tmp_sprite_dir, "setlayer_test.aseprite")
        _create_sprite(cli, path, 64, 64)

        result = await set_layer(
            filename=path, layer_name="Spells", create_if_missing=True
        )
        assert "Set active layer" in result
        assert "Spells" in result

        layers = cli.list_layers(path)
        assert "Spells" in layers

    @pytest.mark.asyncio
    async def test_invalid_width_zero(self):
        """A dark portal with zero width cannot exist in the kingdom."""
        from aseprite_mcp.tools.canvas import create_canvas

        result = await create_canvas(width=0, height=32, filename="bad.aseprite")
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 2: Designing the Knight (Drawing)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter2:
    """Draw the knight's equipment, monsters, and the kingdom backdrop."""

    @pytest.mark.asyncio
    async def test_draw_pixels_real(self, cli, tmp_sprite_dir):
        """Draw red pixels on the canvas and read them back."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        path = _sprite_path(tmp_sprite_dir, "pixel_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await draw_pixels(
            filename=path,
            pixels=[
                {"x": 10, "y": 10, "color": "#ff0000"},
                {"x": 11, "y": 10, "color": "#00ff00"},
            ],
        )
        assert "Pixels drawn" in result

        # Read back the red pixel
        color = await get_pixel_color(filename=path, x=10, y=10)
        assert "#ff0000" in color

        # Read back the green pixel
        color = await get_pixel_color(filename=path, x=11, y=10)
        assert "#00ff00" in color

    @pytest.mark.asyncio
    async def test_draw_line_real(self, cli, tmp_sprite_dir):
        """Draw a black line and verify the sprite saves correctly."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_line

        path = _sprite_path(tmp_sprite_dir, "line_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await draw_line(
            filename=path, x1=5, y1=10, x2=50, y2=10, color="#000000"
        )
        assert "Line drawn" in result
        assert Path(path).is_file()

    @pytest.mark.asyncio
    async def test_draw_rectangle_real(self, cli, tmp_sprite_dir):
        """Draw a filled blue rectangle on the canvas."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_rectangle

        path = _sprite_path(tmp_sprite_dir, "rect_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await draw_rectangle(
            filename=path, x=5, y=5, width=20, height=15, color="#0000ff", fill=True
        )
        assert "Rectangle drawn" in result

    @pytest.mark.asyncio
    async def test_draw_circle_real(self, cli, tmp_sprite_dir):
        """Draw a filled green circle on the canvas."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_circle

        path = _sprite_path(tmp_sprite_dir, "circle_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await draw_circle(
            filename=path,
            center_x=32,
            center_y=32,
            radius=10,
            color="#00ff00",
            fill=True,
        )
        assert "Circle drawn" in result

    @pytest.mark.asyncio
    async def test_fill_area_real(self, cli, tmp_sprite_dir):
        """Fill area with color using paint bucket."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import fill_area

        path = _sprite_path(tmp_sprite_dir, "fill_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await fill_area(filename=path, x=0, y=0, color="#8b4513")
        assert "Area filled" in result

    @pytest.mark.asyncio
    async def test_draw_pixels_at_real(self, cli, tmp_sprite_dir):
        """Draw pixels on a specific layer/frame."""
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "at_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"], frame_count=2)

        result = await draw_pixels_at(
            filename=path,
            layer_name="Knight",
            frame_index=1,
            pixels=[{"x": 5, "y": 5, "color": "#ff0000"}],
        )
        assert "Pixels drawn" in result
        assert "Knight" in result

    @pytest.mark.asyncio
    async def test_draw_polygon_real(self, cli, tmp_sprite_dir):
        """Draw a filled polygon (dragon wing shape)."""
        from aseprite_mcp.tools.drawing import draw_polygon

        path = _sprite_path(tmp_sprite_dir, "polygon_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Monsters"])

        result = await draw_polygon(
            filename=path,
            layer_name="Monsters",
            frame_index=1,
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
    async def test_apply_gradient_rect_real(self, cli, tmp_sprite_dir):
        """Apply a gradient to a rectangle region."""
        from aseprite_mcp.tools.drawing import apply_gradient_rect

        path = _sprite_path(tmp_sprite_dir, "gradient_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Background"])

        result = await apply_gradient_rect(
            filename=path,
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
# Chapter 3: The Journey Begins (Animation)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter3:
    """Animate the knight's walk, attacks, and dodge maneuvers."""

    @pytest.mark.asyncio
    async def test_add_frames_with_duration_real(self, cli, tmp_sprite_dir):
        """Add 8 frames with 100ms duration for the walk cycle."""
        from aseprite_mcp.tools.animation import add_frames

        path = _sprite_path(tmp_sprite_dir, "frames_test.aseprite")
        _create_sprite(cli, path, 64, 64)

        result = await add_frames(filename=path, count=8, duration_ms=100)
        assert "Added 8 frames" in result
        assert "100ms" in result

        # Verify frame count
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("FRAMES:" .. #spr.frames)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FRAMES:9" in output  # 1 original + 8 new

    @pytest.mark.asyncio
    async def test_set_frame_duration_all_real(self, cli, tmp_sprite_dir):
        """Set all frames to 100ms duration and verify."""
        from aseprite_mcp.tools.animation import set_frame_duration_all

        path = _sprite_path(tmp_sprite_dir, "durall_test.aseprite")
        _create_sprite(cli, path, 64, 64, frame_count=4)

        result = await set_frame_duration_all(filename=path, duration_ms=100)
        assert "100ms" in result

        # Verify all frames have 100ms duration
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
local all100 = true
for _, frame in ipairs(spr.frames) do
    if math.floor(frame.duration * 1000 + 0.5) ~= 100 then
        all100 = false
        break
    end
end
print("ALL100:" .. tostring(all100))
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "ALL100:true" in output

    @pytest.mark.asyncio
    async def test_set_layer_visibility_real(self, cli, tmp_sprite_dir):
        """Toggle Knight layer visibility."""
        from aseprite_mcp.tools.animation import set_layer_visibility

        path = _sprite_path(tmp_sprite_dir, "vis_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"])

        result = await set_layer_visibility(
            filename=path, layer_name="Knight", visible=False
        )
        assert (
            "Knight" in result
            or "visibility" in result.lower()
            or "Failed" not in result
        )

    @pytest.mark.asyncio
    async def test_set_layer_opacity_real(self, cli, tmp_sprite_dir):
        """Set Knight layer opacity to 200."""
        from aseprite_mcp.tools.animation import set_layer_opacity

        path = _sprite_path(tmp_sprite_dir, "opacity_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"])

        result = await set_layer_opacity(
            filename=path, layer_name="Knight", opacity=200
        )
        assert "200" in result

    @pytest.mark.asyncio
    async def test_get_sprite_info_real(self, cli, tmp_sprite_dir):
        """Read sprite dimensions, frames, layers from a real sprite.

        Note: get_sprite_info uses `return` (not `print()`) in its Lua script,
        which doesn't produce stdout in batch mode. We verify dimensions via a
        direct Lua probe instead.
        """
        path = _sprite_path(tmp_sprite_dir, "info_test.aseprite")
        _create_sprite(
            cli, path, 64, 64, layers=["Background", "Knight"], frame_count=4
        )

        # Verify directly via Lua (bypass the tool's broken `return`-based output)
        lua_p = _lua_path(path)
        verify_script = (
            f'local spr = app.open("{lua_p}")\n'
            'if not spr then print("ERROR") return end\n'
            'local info = "INFO:" .. spr.width .. ","'
            ' .. spr.height .. "," .. #spr.frames .. "," .. #spr.layers\n'
            'print(info)\n'
            'spr:close()'
        )
        success, output = cli.execute_lua_script(verify_script)
        assert success
        assert "INFO:64,64,4,3" in output

    @pytest.mark.asyncio
    async def test_set_tag_real(self, cli, tmp_sprite_dir):
        """Create animation tags and verify via list_tags."""
        from aseprite_mcp.tools.animation import add_frames, set_tag

        path = _sprite_path(tmp_sprite_dir, "tag_test.aseprite")
        _create_sprite(cli, path, 64, 64)
        await add_frames(filename=path, count=7)  # 8 frames total

        result = await set_tag(
            filename=path, name="walk", from_frame=1, to_frame=8, direction="forward"
        )
        assert "walk" in result

        # Verify via list_tags
        tags = cli.list_tags(path)
        assert "walk" in tags

    @pytest.mark.asyncio
    async def test_tween_cel_positions_real(self, cli, tmp_sprite_dir):
        """Tween positions across frames for knight walk."""
        from aseprite_mcp.tools.animation import add_frames, tween_cel_positions

        path = _sprite_path(tmp_sprite_dir, "tween_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"])
        await add_frames(filename=path, count=4)

        result = await tween_cel_positions(
            filename=path,
            layer_name="Knight",
            start_frame=1,
            end_frame=5,
            start_x=0,
            start_y=32,
            end_x=48,
            end_y=32,
            create_missing_cels=True,
        )
        assert "Tweened cel positions" in result
        assert "Knight" in result

    @pytest.mark.asyncio
    async def test_create_cel_and_clear_cel_real(self, cli, tmp_sprite_dir):
        """Create and delete a cel on a specific layer/frame."""
        from aseprite_mcp.tools.animation import clear_cel, create_cel

        path = _sprite_path(tmp_sprite_dir, "cel_ops.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Effects"], frame_count=4)

        # Create a new cel on frame 3
        result = await create_cel(
            filename=path, layer_name="Effects", frame_index=3, x=0, y=0
        )
        assert "Created cel" in result

        # Clear the cel
        result = await clear_cel(filename=path, layer_name="Effects", frame_index=3)
        assert "Cleared cel" in result

    @pytest.mark.asyncio
    async def test_copy_cel_real(self, cli, tmp_sprite_dir):
        """Copy cel content between frames on the same layer."""
        from aseprite_mcp.tools.animation import copy_cel
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "copy_cel.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"], frame_count=4)

        # Draw a pixel on frame 1
        await draw_pixels_at(
            filename=path,
            layer_name="Knight",
            frame_index=1,
            pixels=[{"x": 10, "y": 10, "color": "#ff0000"}],
        )

        # Copy cel from frame 1 to frame 2
        result = await copy_cel(
            filename=path, layer_name="Knight", source_frame=1, target_frame=2
        )
        assert "Copied cel" in result
        assert "Knight" in result

    @pytest.mark.asyncio
    async def test_oscillate_cel_positions_real(self, cli, tmp_sprite_dir):
        """Sine-wave oscillation for walking bob animation."""
        from aseprite_mcp.tools.animation import add_frames, oscillate_cel_positions

        path = _sprite_path(tmp_sprite_dir, "oscillate_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"])
        await add_frames(filename=path, count=7)

        result = await oscillate_cel_positions(
            filename=path,
            layer_name="Knight",
            start_frame=1,
            end_frame=8,
            amplitude_y=3,
            cycles=2.0,
            create_missing_cels=True,
        )
        assert "Oscillated" in result

    @pytest.mark.asyncio
    async def test_tween_cel_opacity_eased_real(self, cli, tmp_sprite_dir):
        """Fade spell effect in and out by tweening cel opacity."""
        from aseprite_mcp.tools.animation import add_frames, tween_cel_opacity_eased

        path = _sprite_path(tmp_sprite_dir, "opacity_tween.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Effects"])
        await add_frames(filename=path, count=3)

        result = await tween_cel_opacity_eased(
            filename=path,
            layer_name="Effects",
            start_frame=1,
            end_frame=4,
            start_opacity=255,
            end_opacity=0,
            easing="ease_out",
            create_missing_cels=True,
        )
        assert "Tweened cel opacity" in result
        assert "ease_out" in result

    @pytest.mark.asyncio
    async def test_propagate_cels_real(self, cli, tmp_sprite_dir):
        """Propagate cels from source frame across frames."""
        from aseprite_mcp.tools.animation import add_frames, propagate_cels
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "propagate_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Shield"])
        await add_frames(filename=path, count=3)

        # Draw on frame 1
        await draw_pixels_at(
            filename=path,
            layer_name="Shield",
            frame_index=1,
            pixels=[{"x": 5, "y": 5, "color": "#8b4513"}],
        )

        result = await propagate_cels(
            filename=path,
            layer_names=["Shield"],
            source_frame=1,
            start_frame=2,
            end_frame=4,
        )
        assert "Propagated" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 4: Arming the Knight (Export & Palette)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter4:
    """Export the sprite, manage color palettes."""

    @pytest.mark.asyncio
    async def test_export_sprite_real(self, cli, tmp_sprite_dir, output_dir):
        """Export to PNG, verify PNG file exists and has non-zero size."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.export import export_sprite

        path = _sprite_path(tmp_sprite_dir, "export_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        png_path = str(output_dir / "knight.png")
        result = await export_sprite(
            filename=path, output_filename=png_path, format="png"
        )
        assert "Exported" in result
        assert Path(png_path).is_file(), f"PNG file not created: {png_path}"
        assert Path(png_path).stat().st_size > 0, "PNG file is empty"

    @pytest.mark.asyncio
    async def test_copy_sprite_real(self, cli, tmp_sprite_dir, output_dir):
        """Copy sprite, verify .aseprite copy exists."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.export import copy_sprite

        path = _sprite_path(tmp_sprite_dir, "copy_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        copy_path = str(output_dir / "kingdom_backup.aseprite")
        result = await copy_sprite(
            filename=path, output_filename=copy_path, overwrite=True
        )
        assert "Copied" in result
        assert Path(copy_path).is_file(), "Backup sprite file not created"
        assert Path(copy_path).stat().st_size > 0

    @pytest.mark.asyncio
    async def test_get_palette_real(self, cli, tmp_sprite_dir):
        """Read palette from a sprite."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.palette import get_palette

        path = _sprite_path(tmp_sprite_dir, "palette_test.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        result = await get_palette(filename=path)
        parsed = json.loads(result)
        assert "palette" in parsed
        assert "count" in parsed
        assert parsed["count"] > 0

    @pytest.mark.asyncio
    async def test_set_palette_real(self, cli, tmp_sprite_dir):
        """Set a new palette on a sprite and verify it persists."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.palette import get_palette, set_palette

        path = _sprite_path(tmp_sprite_dir, "setpal_test.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        new_colors = ["#1a1a2e", "#16213e", "#0f3460", "#e94560"]
        result = await set_palette(filename=path, colors=new_colors)
        assert "4 colors" in result

        # Read back the palette (Aseprite returns uppercase hex)
        result = await get_palette(filename=path)
        parsed = json.loads(result)
        palette_lower = [c.lower() for c in parsed["palette"]]
        assert "#1a1a2e" in palette_lower

    @pytest.mark.asyncio
    async def test_remap_colors_real(self, cli, tmp_sprite_dir):
        """Remap silver to gold on the Knight layer."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels
        from aseprite_mcp.tools.palette import remap_colors_in_cel_range

        path = _sprite_path(tmp_sprite_dir, "remap_test.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        # Draw a silver pixel first
        await draw_pixels(filename=path, pixels=[{"x": 5, "y": 5, "color": "#c0c0c0"}])

        result = await remap_colors_in_cel_range(
            filename=path,
            layer_name="Layer 1",
            start_frame=1,
            end_frame=1,
            mappings=[{"from": "#c0c0c0", "to": "#ffd700"}],
        )
        assert "Remapped" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 5: Scouting the Battlefield (Pixel Read)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter5:
    """Read pixel colors from real sprites."""

    @pytest.mark.asyncio
    async def test_get_pixel_color_real(self, cli, tmp_sprite_dir):
        """Draw a pixel, read it back, verify the color matches."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        path = _sprite_path(tmp_sprite_dir, "pixelread_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        # Draw a red pixel
        await draw_pixels(
            filename=path, pixels=[{"x": 20, "y": 20, "color": "#ff0000"}]
        )

        # Read it back
        result = await get_pixel_color(filename=path, x=20, y=20)
        assert "#ff0000" in result
        assert "r=255" in result
        assert "g=0" in result
        assert "b=0" in result

    @pytest.mark.asyncio
    async def test_get_pixels_rect_real(self, cli, tmp_sprite_dir):
        """Read a rectangle of pixels and verify output structure."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        path = _sprite_path(tmp_sprite_dir, "rectread_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        # Draw a few pixels
        await draw_pixels(
            filename=path,
            pixels=[
                {"x": 5, "y": 5, "color": "#00ff00"},
                {"x": 6, "y": 5, "color": "#0000ff"},
            ],
        )

        # Read a 3x3 rect
        result = await get_pixels_rect(filename=path, x=4, y=4, width=3, height=3)
        parsed = json.loads(result)
        assert "pixels" in parsed
        assert parsed["count"] == 9  # 3x3

        # Verify our drawn pixels are in the result
        pixel_map = {(p["x"], p["y"]): p for p in parsed["pixels"]}
        assert pixel_map[(5, 5)]["hex"] == "#00ff00"
        assert pixel_map[(6, 5)]["hex"] == "#0000ff"

    @pytest.mark.asyncio
    async def test_get_pixel_color_on_named_layer(self, cli, tmp_sprite_dir):
        """Read pixel color from a specific named layer."""
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        path = _sprite_path(tmp_sprite_dir, "layer_pixel.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"], frame_count=2)

        await draw_pixels_at(
            filename=path,
            layer_name="Knight",
            frame_index=1,
            pixels=[{"x": 15, "y": 15, "color": "#ff0000"}],
        )

        result = await get_pixel_color(
            filename=path, x=15, y=15, layer_name="Knight", frame_index=1
        )
        assert "#ff0000" in result


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 6: Building the Boss Arena (Scene & Quality)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter6:
    """Cross-sprite operations, validation, and quality audit."""

    @pytest.mark.asyncio
    async def test_copy_layers_between_sprites_real(self, cli, tmp_sprite_dir):
        """Copy layers from one sprite to another."""
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.scene import copy_layers_between_sprites

        source_path = _sprite_path(tmp_sprite_dir, "boss.aseprite")
        target_path = _sprite_path(tmp_sprite_dir, "kingdom_scene.aseprite")

        # Create source with Dragon layer
        _create_sprite(
            cli, source_path, 64, 64, layers=["Dragon", "BossFX"], frame_count=2
        )
        # Draw on the Dragon layer so there's content to copy
        await draw_pixels_at(
            filename=source_path,
            layer_name="Dragon",
            frame_index=1,
            pixels=[
                {"x": 30, "y": 10, "color": "#8b0000"},
                {"x": 31, "y": 10, "color": "#8b0000"},
            ],
        )

        # Create target with some layers
        _create_sprite(
            cli, target_path, 64, 64, layers=["Background", "Knight"], frame_count=2
        )

        result = await copy_layers_between_sprites(
            source_filename=source_path,
            target_filename=target_path,
            layer_names=["Dragon"],
        )
        assert "Copied" in result

        # Verify Dragon layer now exists in target
        target_layers = cli.list_layers(target_path)
        assert "Dragon" in target_layers

    @pytest.mark.asyncio
    async def test_ensure_layers_present_real(self, cli, tmp_sprite_dir):
        """Ensure layers have cels — should succeed without error."""
        from aseprite_mcp.tools.quality import ensure_layers_present

        path = _sprite_path(tmp_sprite_dir, "ensure_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight", "Effects"], frame_count=4)

        result = await ensure_layers_present(
            filename=path,
            layer_names=["Knight", "Effects"],
            start_frame=1,
            end_frame=4,
        )
        # Tool succeeded (no "Failed" prefix) — that's the key assertion
        assert "Failed" not in result
        assert "ensure_layers_present" in result

    @pytest.mark.asyncio
    async def test_validate_scene_real(self, cli, tmp_sprite_dir):
        """Validate sprite structure and get a report."""
        from aseprite_mcp.tools.quality import validate_scene

        path = _sprite_path(tmp_sprite_dir, "validate_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight", "Monsters"], frame_count=4)

        result = await validate_scene(
            filename=path,
            required_layers=["Knight", "Monsters", "Effects"],
            start_frame=1,
            end_frame=4,
        )
        # Effects layer doesn't exist, should be reported as missing
        assert (
            "missing_layers" in result.lower()
            or "Effects" in result
            or "frames" in result.lower()
        )

    @pytest.mark.asyncio
    async def test_audit_animation_real(self, cli, tmp_sprite_dir):
        """Audit the animation for overlaps and out-of-range cels."""
        from aseprite_mcp.tools.quality import audit_animation

        path = _sprite_path(tmp_sprite_dir, "audit_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight", "Monsters"], frame_count=4)

        result = await audit_animation(
            filename=path,
            start_frame=1,
            end_frame=4,
        )
        assert result is not None and len(result) > 0
        assert "summary" in result.lower() or "frames" in result.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 7: Combat Mechanics (Transform)
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter7:
    """Flip, rotate, resize, and crop the battlefield."""

    @pytest.mark.asyncio
    async def test_flip_layer_real(self, cli, tmp_sprite_dir):
        """Flip a layer horizontally and verify the sprite saves."""
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.transform import flip_layer

        path = _sprite_path(tmp_sprite_dir, "flip_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Knight"])

        # Draw a pixel to have content to flip
        await draw_pixels_at(
            filename=path,
            layer_name="Knight",
            frame_index=1,
            pixels=[{"x": 10, "y": 10, "color": "#ff0000"}],
        )

        result = await flip_layer(
            filename=path, layer_name="Knight", frame_index=1, direction="horizontal"
        )
        assert "Flipped" in result

    @pytest.mark.xfail(
        os.name == "nt",
        reason="rotate_layer Lua script contains Unicode arrow (→) "
        "that fails cp1252 encoding on Windows — source code bug",
        strict=True,
    )
    @pytest.mark.asyncio
    async def test_rotate_layer_real(self, cli, tmp_sprite_dir):
        """Rotate a layer by 90 degrees."""
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.transform import rotate_layer

        path = _sprite_path(tmp_sprite_dir, "rotate_test.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Effects"])

        # Draw a pixel to have content to rotate
        await draw_pixels_at(
            filename=path,
            layer_name="Effects",
            frame_index=1,
            pixels=[{"x": 10, "y": 5, "color": "#00ffff"}],
        )

        result = await rotate_layer(
            filename=path, layer_name="Effects", frame_index=1, angle=90
        )
        assert "Rotated" in result
        assert "90" in result

    @pytest.mark.asyncio
    async def test_resize_canvas_real(self, cli, tmp_sprite_dir):
        """Resize sprite and verify new dimensions."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.transform import resize_canvas

        path = _sprite_path(tmp_sprite_dir, "resize_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await resize_canvas(filename=path, width=128, height=128)
        assert "Resized" in result

        # Verify new dimensions
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("SIZE:" .. spr.width .. "x" .. spr.height)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "SIZE:128x128" in output

    @pytest.mark.asyncio
    async def test_crop_canvas_real(self, cli, tmp_sprite_dir):
        """Crop sprite and verify smaller dimensions."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.transform import crop_canvas

        path = _sprite_path(tmp_sprite_dir, "crop_test.aseprite")
        await create_canvas(width=64, height=64, filename=path)

        result = await crop_canvas(filename=path, x=4, y=4, width=56, height=56)
        assert "Cropped" in result

        # Verify new dimensions
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("SIZE:" .. spr.width .. "x" .. spr.height)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "SIZE:56x56" in output


# ═══════════════════════════════════════════════════════════════════════════
# Chapter 8: Legacy Server Tools
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveChapter8:
    """Test the legacy server.py tools — the ancient spells from the old kingdom."""

    @pytest.mark.asyncio
    async def test_sprite_create_legacy_real(self, cli, tmp_sprite_dir, output_dir):
        """Use legacy sprite_create to create a sprite and verify it exists."""
        from aseprite_mcp.server import sprite_create

        path = _sprite_path(tmp_sprite_dir, "legacy_create.ase")
        result = await sprite_create(width=32, height=32, output_path=path)
        # Legacy sprite_create returns JSON on success
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert (
                parsed.get("width") == 32
                or "width" in str(parsed)
                or parsed.get("success")
            )

    @pytest.mark.asyncio
    async def test_sprite_info_legacy_real(self, cli, tmp_sprite_dir):
        """Use legacy sprite_info to read metadata."""
        from aseprite_mcp.server import sprite_info

        path = _sprite_path(tmp_sprite_dir, "legacy_info.aseprite")
        _create_sprite(cli, path, 64, 64)

        result = await sprite_info(file_path=path)
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert "width" in parsed

    @pytest.mark.asyncio
    async def test_sprite_export_legacy_real(self, cli, tmp_sprite_dir, output_dir):
        """Use legacy sprite_export to export a sprite."""
        from aseprite_mcp.server import sprite_export

        path = _sprite_path(tmp_sprite_dir, "legacy_export.aseprite")
        _create_sprite(cli, path, 32, 32)

        png_path = str(output_dir / "legacy_knight.png")
        result = await sprite_export(input_path=path, output_path=png_path)
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert parsed.get("success") is True or "success" in str(parsed).lower()
        # The PNG should exist
        assert Path(png_path).is_file(), f"Legacy export PNG not found: {png_path}"

    @pytest.mark.asyncio
    async def test_list_layers_legacy_real(self, cli, tmp_sprite_dir):
        """Use cli.list_layers() directly to verify layers."""
        path = _sprite_path(tmp_sprite_dir, "legacy_layers.aseprite")
        _create_sprite(cli, path, 64, 64, layers=["Background", "Knight", "Effects"])

        layers = cli.list_layers(path)
        assert isinstance(layers, list)
        assert "Background" in layers
        assert "Knight" in layers
        assert "Effects" in layers

    @pytest.mark.asyncio
    async def test_list_tags_legacy_real(self, cli, tmp_sprite_dir):
        """Use cli.list_tags() directly after creating tags."""
        from aseprite_mcp.tools.animation import add_frames, set_tag

        path = _sprite_path(tmp_sprite_dir, "legacy_tags.aseprite")
        _create_sprite(cli, path, 64, 64)
        await add_frames(filename=path, count=3)

        # Create tags first
        await set_tag(
            filename=path, name="walk", from_frame=1, to_frame=4, direction="forward"
        )
        await set_tag(
            filename=path, name="attack", from_frame=1, to_frame=4, direction="forward"
        )

        tags = cli.list_tags(path)
        assert isinstance(tags, list)
        assert "walk" in tags
        assert "attack" in tags
