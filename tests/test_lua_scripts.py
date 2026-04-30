"""Tests for aseprite_mcp.lua_scripts module."""

from __future__ import annotations

from aseprite_mcp.lua_scripts import (
    _lua_escape,
    create_sprite_script,
    draw_pixels_script,
    export_sprite_script,
    fill_rect_script,
    sprite_info_script,
    ws_bridge_script,
)


class TestCreateSpriteScript:
    def test_default_rgb(self) -> None:
        script = create_sprite_script(32, 32)
        assert "Sprite(32, 32" in script
        assert "ColorMode.RGB" in script
        assert "app.exit()" in script

    def test_grayscale(self) -> None:
        script = create_sprite_script(64, 32, color_mode="grayscale")
        assert "ColorMode.GRAYSCALE" in script

    def test_indexed(self) -> None:
        script = create_sprite_script(16, 16, color_mode="indexed")
        assert "ColorMode.INDEXED" in script

    def test_contains_json_output(self) -> None:
        script = create_sprite_script(32, 32)
        assert "JSON_START" in script
        assert "json.encode" in script


class TestSpriteInfoScript:
    def test_basic_structure(self) -> None:
        script = sprite_info_script("/path/to/sprite.ase")
        assert 'app.open("/path/to/sprite.ase")' in script
        assert "JSON_START" in script
        assert "sprite.width" in script
        assert "sprite.height" in script
        assert "sprite:close()" in script

    def test_escapes_path(self) -> None:
        script = sprite_info_script('/path/with "quotes"/sprite.ase')
        assert '\\"quotes\\"' in script


class TestExportSpriteScript:
    def test_basic_export(self) -> None:
        script = export_sprite_script("/input.ase", "/output.png")
        assert 'app.open("/input.ase")' in script
        assert 'saveAs("/output.png")' in script
        assert "JSON_START" in script


class TestDrawPixelsScript:
    def test_single_pixel(self) -> None:
        pixels = [{"x": 10, "y": 5, "color": "#ff0000"}]
        script = draw_pixels_script(pixels)
        assert "drawPixel(10, 5" in script
        assert "rgba(#ff0000)" in script

    def test_multiple_pixels(self) -> None:
        pixels = [
            {"x": 0, "y": 0, "color": "#ffffff"},
            {"x": 1, "y": 1, "color": "#000000"},
        ]
        script = draw_pixels_script(pixels)
        assert "drawPixel(0, 0" in script
        assert "drawPixel(1, 1" in script

    def test_no_active_sprite_error(self) -> None:
        script = draw_pixels_script([{"x": 0, "y": 0, "color": "#fff"}])
        assert "No active sprite" in script


class TestFillRectScript:
    def test_basic_fill(self) -> None:
        script = fill_rect_script(0, 0, 8, 8, "#ff0000")
        assert "py = 0, 0 + 8 - 1" in script
        assert "px = 0, 0 + 8 - 1" in script
        assert 'rgba("#ff0000")' in script


class TestWsBridgeScript:
    def test_contains_url(self) -> None:
        script = ws_bridge_script("ws://127.0.0.1:8765")
        assert 'url = "ws://127.0.0.1:8765"' in script

    def test_handles_ping(self) -> None:
        script = ws_bridge_script("ws://127.0.0.1:8765")
        assert '"pong"' in script

    def test_handles_draw_pixels(self) -> None:
        script = ws_bridge_script("ws://127.0.0.1:8765")
        assert "draw_pixels" in script

    def test_handles_fill_rect(self) -> None:
        script = ws_bridge_script("ws://127.0.0.1:8765")
        assert "fill_rect" in script

    def test_handles_close(self) -> None:
        script = ws_bridge_script("ws://127.0.0.1:8765")
        assert "ws:close()" in script


class TestLuaEscape:
    def test_escapes_backslash(self) -> None:
        assert _lua_escape("path\\to") == "path\\\\to"

    def test_escapes_quotes(self) -> None:
        assert _lua_escape('say "hello"') == 'say \\"hello\\"'

    def test_no_escape_needed(self) -> None:
        assert _lua_escape("/simple/path") == "/simple/path"
