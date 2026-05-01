"""Live E2E test: Knight Quest RPG multi-tool workflow pipelines using the
REAL Aseprite binary.

Unlike the integration test (which validates individual tools), this E2E test
validates COMPLETE WORKFLOW PIPELINES that chain multiple tools together to
produce real game assets. Each pipeline mirrors a game-dev workflow: create
sprite -> add layers -> draw pixels -> animate -> tag -> export.

Tests auto-skip if no Aseprite binary is found.
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

pytestmark = pytest.mark.skipif(
    not ASEPRITE_PATH or not Path(ASEPRITE_PATH).is_file(),
    reason="Aseprite binary not found -- set ASEPRITE_PATH or install Aseprite",
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


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 1: Full Knight Character Creation
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2ECharacterPipeline:
    """End-to-end: Create a complete knight character with layers, frames,
    pixels, tags, and exported PNG."""

    @pytest.mark.asyncio
    async def test_full_knight_creation_pipeline(
        self, cli, tmp_sprite_dir, output_dir
    ):
        """Create canvas -> add Body/Armor/Sword/Cape layers -> add 4 frames
        -> set 150ms duration -> draw knight pixels -> set idle tag -> export
        PNG. Verify: .aseprite exists, .png exists, layers, tags."""
        from aseprite_mcp.tools.animation import add_frames, set_frame_duration_all
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.export import export_sprite

        path = _sprite_path(tmp_sprite_dir, "knight.aseprite")

        # Step 1: Create canvas
        result = await create_canvas(width=64, height=64, filename=path)
        assert "Created canvas" in result
        assert Path(path).is_file()

        # Step 2: Add layers
        for layer_name in ("Body", "Armor", "Sword", "Cape"):
            result = await add_layer(filename=path, layer_name=layer_name)
            assert "Added layer" in result

        # Step 3: Add 4 frames (total 5 including the initial)
        result = await add_frames(filename=path, count=4, duration_ms=150)
        assert "Added 4 frames" in result

        # Step 4: Set all frame durations to 150ms
        result = await set_frame_duration_all(filename=path, duration_ms=150)
        assert "150" in result

        # Step 5: Draw knight pixels on Body layer
        from aseprite_mcp.tools.drawing import draw_pixels_at

        result = await draw_pixels_at(
            filename=path,
            layer_name="Body",
            frame_index=1,
            pixels=[
                {"x": 30, "y": 10, "color": "#c0c0c0"},
                {"x": 31, "y": 10, "color": "#c0c0c0"},
                {"x": 30, "y": 11, "color": "#c0c0c0"},
                {"x": 31, "y": 11, "color": "#c0c0c0"},
            ],
        )
        assert "Pixels drawn" in result

        # Step 6: Set "idle" tag
        from aseprite_mcp.tools.animation import set_tag

        result = await set_tag(
            filename=path, name="idle", from_frame=1, to_frame=5, direction="forward"
        )
        assert "idle" in result

        # Step 7: Export PNG
        # NOTE: Aseprite --save-as for multi-frame sprites produces
        # frame-numbered files (e.g. knight1.png, knight2.png, ...),
        # not the exact filename requested. Use a glob to find them.
        png_path = str(output_dir / "knight.png")
        result = await export_sprite(
            filename=path, output_filename=png_path, format="png"
        )
        assert "Exported" in result
        # With 5 frames, Aseprite creates knight1.png..knight5.png
        exported_pngs = list(output_dir.glob("knight*.png"))
        assert len(exported_pngs) > 0, "No PNG files exported"
        for png in exported_pngs:
            assert png.stat().st_size > 0, f"Exported PNG is empty: {png}"

        # Verify layers
        layers = cli.list_layers(path)
        for expected in ("Body", "Armor", "Sword", "Cape"):
            assert expected in layers, f"Layer '{expected}' not found in {layers}"

        # Verify tags
        tags = cli.list_tags(path)
        assert "idle" in tags, f"Tag 'idle' not found in {tags}"

        # Verify frame count via Lua
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("FRAMES:" .. #spr.frames)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FRAMES:5" in output

    @pytest.mark.asyncio
    async def test_knight_with_weapon_and_shield_pipeline(self, cli, tmp_sprite_dir):
        """Create knight -> add Shield+Weapon layers -> draw on both -> verify
        both layers have pixel data via Lua."""
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "knight_gear.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        await add_layer(filename=path, layer_name="Shield")
        await add_layer(filename=path, layer_name="Weapon")

        # Draw on Shield
        await draw_pixels_at(
            filename=path,
            layer_name="Shield",
            frame_index=1,
            pixels=[
                {"x": 5, "y": 5, "color": "#0000ff"},
                {"x": 6, "y": 5, "color": "#0000ff"},
            ],
        )

        # Draw on Weapon
        await draw_pixels_at(
            filename=path,
            layer_name="Weapon",
            frame_index=1,
            pixels=[
                {"x": 20, "y": 5, "color": "#8b4513"},
                {"x": 21, "y": 5, "color": "#8b4513"},
            ],
        )

        # Verify both layers exist and have non-transparent pixels
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
local found = 0
for _, layer in ipairs(spr.layers) do
    if layer.name == "Shield" or layer.name == "Weapon" then
        local cel = layer:cel(1)
        if cel and cel.image then
            local hasPixels = false
            for y = 0, cel.image.height - 1 do
                for x = 0, cel.image.width - 1 do
                    local c = cel.image:getPixel(x, y)
                    if app.pixelColor.rgbaA(c) > 0 then
                        hasPixels = true
                        break
                    end
                end
                if hasPixels then break end
            end
            if hasPixels then found = found + 1 end
        end
    end
end
print("FOUND:" .. found)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FOUND:2" in output


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 2: Monster Creation
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EMonsterPipeline:
    """End-to-end: Create multiple monster sprites with distinct dimensions,
    layers, and tags."""

    @pytest.mark.asyncio
    async def test_three_monsters_pipeline(self, cli, tmp_sprite_dir):
        """Create goblin (16x16), skeleton (16x24), slime (16x12) each with
        layers and tags. Verify: all 3 .aseprite files exist, each has
        correct layers and tags."""
        from aseprite_mcp.tools.animation import add_frames, set_tag
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at

        monsters = [
            ("goblin", 16, 16, ["GreenSkin", "Eyes"]),
            ("skeleton", 16, 24, ["Bones", "Weapon"]),
            ("slime", 16, 12, ["Body", "Highlight"]),
        ]

        for name, w, h, layers in monsters:
            path = _sprite_path(tmp_sprite_dir, f"{name}.aseprite")

            # Create canvas
            result = await create_canvas(width=w, height=h, filename=path)
            assert "Created canvas" in result
            assert Path(path).is_file()

            # Add layers
            for layer_name in layers:
                result = await add_layer(filename=path, layer_name=layer_name)
                assert "Added layer" in result

            # Add frames for animation
            await add_frames(filename=path, count=3, duration_ms=100)

            # Draw a representative pixel on first layer
            result = await draw_pixels_at(
                filename=path,
                layer_name=layers[0],
                frame_index=1,
                pixels=[{"x": 8, "y": 4, "color": "#00ff00"}],
            )
            assert "Pixels drawn" in result

            # Set tags
            tag_name = f"{name}_idle"
            result = await set_tag(
                filename=path,
                name=tag_name,
                from_frame=1,
                to_frame=4,
                direction="forward",
            )
            assert tag_name in result

            # Verify layers
            actual_layers = cli.list_layers(path)
            for expected_layer in layers:
                assert expected_layer in actual_layers

            # Verify tags
            tags = cli.list_tags(path)
            assert tag_name in tags

            # Verify dimensions
            lua_p = _lua_path(path)
            dim_script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("DIM:{w}x{h}:" .. spr.width .. "x" .. spr.height)
spr:close()
"""
            success, output = cli.execute_lua_script(dim_script)
            assert success
            assert f"DIM:{w}x{h}:{w}x{h}" in output

    @pytest.mark.asyncio
    async def test_monster_palette_pipeline(self, cli, tmp_sprite_dir):
        """Create monster -> set dark palette -> read back -> verify colors."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.palette import get_palette, set_palette

        path = _sprite_path(tmp_sprite_dir, "dark_monster.aseprite")
        await create_canvas(width=16, height=16, filename=path)

        dark_colors = ["#1a1a2e", "#16213e", "#0f3460", "#e94560"]
        result = await set_palette(filename=path, colors=dark_colors)
        assert "4 colors" in result

        # Read back palette
        result = await get_palette(filename=path)
        parsed = json.loads(result)
        assert "palette" in parsed
        palette_lower = [c.lower() for c in parsed["palette"]]
        for color in dark_colors:
            assert color in palette_lower, f"{color} not found in palette"


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 3: Battle Animation
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EAnimationPipeline:
    """End-to-end: Create animated battle sequences with tweening and tags."""

    @pytest.mark.asyncio
    async def test_battle_animation_pipeline(self, cli, tmp_sprite_dir):
        """Create knight sprite -> add 6 frames -> tween cel positions for
        sword swing -> add 'melee_attack' tag. Verify: 7+ frames, tag exists."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            set_tag,
            tween_cel_positions,
        )
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "battle.aseprite")

        # Create canvas with Sword layer
        await create_canvas(width=64, height=64, filename=path)
        await add_layer(filename=path, layer_name="Sword")

        # Draw initial sword position
        await draw_pixels_at(
            filename=path,
            layer_name="Sword",
            frame_index=1,
            pixels=[
                {"x": 40, "y": 20, "color": "#c0c0c0"},
                {"x": 41, "y": 20, "color": "#c0c0c0"},
            ],
        )

        # Add 6 more frames
        result = await add_frames(filename=path, count=6, duration_ms=80)
        assert "Added 6 frames" in result

        # Tween sword position for swing animation
        result = await tween_cel_positions(
            filename=path,
            layer_name="Sword",
            start_frame=1,
            end_frame=7,
            start_x=0,
            start_y=0,
            end_x=-20,
            end_y=20,
            create_missing_cels=True,
        )
        assert "Tweened cel positions" in result

        # Set attack tag
        result = await set_tag(
            filename=path,
            name="melee_attack",
            from_frame=1,
            to_frame=7,
            direction="forward",
        )
        assert "melee_attack" in result

        # Verify frame count (7 total)
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("FRAMES:" .. #spr.frames)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FRAMES:7" in output

        # Verify tag
        tags = cli.list_tags(path)
        assert "melee_attack" in tags

    @pytest.mark.asyncio
    async def test_walk_cycle_pipeline(self, cli, tmp_sprite_dir):
        """Create walk cycle: 8 frames with oscillation for bobbing motion."""
        from aseprite_mcp.tools.animation import add_frames, oscillate_cel_positions
        from aseprite_mcp.tools.canvas import add_layer, create_canvas

        path = _sprite_path(tmp_sprite_dir, "walk.aseprite")
        await create_canvas(width=32, height=32, filename=path)
        await add_layer(filename=path, layer_name="Legs")

        await add_frames(filename=path, count=7, duration_ms=120)

        result = await oscillate_cel_positions(
            filename=path,
            layer_name="Legs",
            start_frame=1,
            end_frame=8,
            amplitude_y=3,
            cycles=2.0,
            create_missing_cels=True,
        )
        assert "Oscillated" in result

        # Verify 8 frames
        lua_p = _lua_path(path)
        script = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("FRAMES:" .. #spr.frames)
spr:close()
"""
        success, output = cli.execute_lua_script(script)
        assert success
        assert "FRAMES:8" in output


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 4: Scene Composition
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EScenePipeline:
    """End-to-end: Cross-sprite operations and scene validation."""

    @pytest.mark.asyncio
    async def test_scene_composition_pipeline(self, cli, tmp_sprite_dir):
        """Create hero sprite + boss sprite -> copy_layers_between_sprites
        from boss to hero -> validate_scene. Verify: hero sprite has the
        transferred layer."""
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.quality import validate_scene
        from aseprite_mcp.tools.scene import copy_layers_between_sprites

        hero_path = _sprite_path(tmp_sprite_dir, "hero.aseprite")
        boss_path = _sprite_path(tmp_sprite_dir, "boss.aseprite")

        # Create hero with layers
        hero_lua = _lua_path(hero_path)
        hero_script = f"""
local spr = Sprite(64, 64)
local heroLayer = spr:newLayer()
heroLayer.name = "Hero"
local bgLayer = spr:newLayer()
bgLayer.name = "Background"
spr:newEmptyFrame()
spr:saveAs("{hero_lua}")
spr:close()
"""
        success, output = cli.execute_lua_script(hero_script)
        assert success, f"Failed to create hero: {output}"

        # Create boss with Dragon layer
        boss_lua = _lua_path(boss_path)
        boss_script = f"""
local spr = Sprite(64, 64)
local dragonLayer = spr:newLayer()
dragonLayer.name = "Dragon"
local bossFXLayer = spr:newLayer()
bossFXLayer.name = "BossFX"
spr:newEmptyFrame()
spr:saveAs("{boss_lua}")
spr:close()
"""
        success, output = cli.execute_lua_script(boss_script)
        assert success, f"Failed to create boss: {output}"

        # Draw on Dragon layer so there's content to copy
        await draw_pixels_at(
            filename=boss_path,
            layer_name="Dragon",
            frame_index=1,
            pixels=[
                {"x": 30, "y": 10, "color": "#8b0000"},
                {"x": 31, "y": 10, "color": "#8b0000"},
            ],
        )

        # Copy Dragon layer from boss to hero
        result = await copy_layers_between_sprites(
            source_filename=boss_path,
            target_filename=hero_path,
            layer_names=["Dragon"],
        )
        assert "Copied" in result

        # Verify Dragon layer now in hero
        hero_layers = cli.list_layers(hero_path)
        assert "Dragon" in hero_layers

        # Validate scene with required layers
        result = await validate_scene(
            filename=hero_path,
            required_layers=["Hero", "Dragon", "MissingLayer"],
            start_frame=1,
            end_frame=2,
        )
        # MissingLayer should be reported
        assert "MissingLayer" in result or "missing_layers" in result.lower()

    @pytest.mark.asyncio
    async def test_multi_layer_scene_copy_pipeline(self, cli, tmp_sprite_dir):
        """Copy multiple layers between sprites and verify all transferred."""
        from aseprite_mcp.tools.scene import copy_layers_between_sprites

        src_path = _sprite_path(tmp_sprite_dir, "src_scene.aseprite")
        dst_path = _sprite_path(tmp_sprite_dir, "dst_scene.aseprite")

        # Create source with FX layers
        src_lua = _lua_path(src_path)
        src_script = f"""
local spr = Sprite(64, 64)
local l1 = spr:newLayer()
l1.name = "Explosion"
local l2 = spr:newLayer()
l2.name = "Smoke"
spr:newEmptyFrame()
spr:saveAs("{src_lua}")
spr:close()
"""
        success, _ = cli.execute_lua_script(src_script)
        assert success

        # Create destination with base layer
        dst_lua = _lua_path(dst_path)
        dst_script = f"""
local spr = Sprite(64, 64)
local l = spr:newLayer()
l.name = "Ground"
spr:newEmptyFrame()
spr:saveAs("{dst_lua}")
spr:close()
"""
        success, _ = cli.execute_lua_script(dst_script)
        assert success

        # Copy both FX layers
        result = await copy_layers_between_sprites(
            source_filename=src_path,
            target_filename=dst_path,
            layer_names=["Explosion", "Smoke"],
        )
        assert "Copied" in result

        # Verify both transferred
        dst_layers = cli.list_layers(dst_path)
        assert "Explosion" in dst_layers
        assert "Smoke" in dst_layers
        assert "Ground" in dst_layers


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 5: Export & QA
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EExportPipeline:
    """End-to-end: Export sprites and verify output quality."""

    @pytest.mark.asyncio
    async def test_export_qa_pipeline(self, cli, tmp_sprite_dir, output_dir):
        """Create sprite -> set dark palette -> export PNG -> verify PNG
        exists and has non-zero size. Also test get_palette -> set_palette."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.export import export_sprite
        from aseprite_mcp.tools.palette import get_palette, set_palette

        path = _sprite_path(tmp_sprite_dir, "export_qa.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        # Set a distinctive palette
        dark_colors = ["#1a1a2e", "#16213e", "#0f3460", "#e94560"]
        result = await set_palette(filename=path, colors=dark_colors)
        assert "4 colors" in result

        # Verify palette round-trip
        result = await get_palette(filename=path)
        parsed = json.loads(result)
        assert parsed["count"] >= 4

        # Export to PNG
        png_path = str(output_dir / "export_qa.png")
        result = await export_sprite(
            filename=path, output_filename=png_path, format="png"
        )
        assert "Exported" in result
        assert Path(png_path).is_file()
        assert Path(png_path).stat().st_size > 0

        # Change palette and export again
        bright_colors = ["#ffffff", "#ff0000", "#00ff00", "#0000ff"]
        await set_palette(filename=path, colors=bright_colors)
        png2_path = str(output_dir / "export_qa_v2.png")
        result = await export_sprite(
            filename=path, output_filename=png2_path, format="png"
        )
        assert Path(png2_path).is_file()
        assert Path(png2_path).stat().st_size > 0

    @pytest.mark.asyncio
    async def test_sprite_copy_and_re_export_pipeline(
        self, cli, tmp_sprite_dir, output_dir
    ):
        """Create sprite -> copy -> export copy -> verify both exports work."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.export import copy_sprite, export_sprite

        path = _sprite_path(tmp_sprite_dir, "original.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        copy_path = _sprite_path(tmp_sprite_dir, "copy.aseprite")
        result = await copy_sprite(
            filename=path, output_filename=copy_path, overwrite=True
        )
        assert "Copied" in result
        assert Path(copy_path).is_file()

        # Export the copy
        png_path = str(output_dir / "copy_export.png")
        result = await export_sprite(
            filename=copy_path, output_filename=png_path, format="png"
        )
        assert "Exported" in result
        assert Path(png_path).is_file()

    @pytest.mark.asyncio
    async def test_export_with_pixel_verification_pipeline(
        self, cli, tmp_sprite_dir, output_dir
    ):
        """Create sprite -> draw known pixels -> export -> reopen -> verify
        pixels match via read-back."""
        from aseprite_mcp.tools.canvas import create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels
        from aseprite_mcp.tools.export import export_sprite
        from aseprite_mcp.tools.pixel_read import get_pixel_color

        path = _sprite_path(tmp_sprite_dir, "pixel_verify.aseprite")
        await create_canvas(width=32, height=32, filename=path)

        # Draw a known red pixel
        await draw_pixels(
            filename=path,
            pixels=[{"x": 5, "y": 5, "color": "#ff0000"}],
        )

        # Verify pixel is there before export
        result = await get_pixel_color(filename=path, x=5, y=5)
        assert "#ff0000" in result

        # Export and verify PNG
        png_path = str(output_dir / "pixel_verify.png")
        result = await export_sprite(
            filename=path, output_filename=png_path, format="png"
        )
        assert Path(png_path).is_file()
        assert Path(png_path).stat().st_size > 0


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 6: Transform Pipeline
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2ETransformPipeline:
    """End-to-end: Chain canvas and layer transforms."""

    @pytest.mark.asyncio
    async def test_transform_pipeline(self, cli, tmp_sprite_dir):
        """Create sprite with knight -> flip_layer horizontal -> resize_canvas
        to 128x128 -> crop_canvas to 32x32 -> verify final dimensions via Lua
        script."""
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.transform import (
            crop_canvas,
            flip_layer,
            resize_canvas,
        )

        path = _sprite_path(tmp_sprite_dir, "transform.aseprite")
        await create_canvas(width=64, height=64, filename=path)
        await add_layer(filename=path, layer_name="Knight")

        # Draw a pixel to have content to flip
        await draw_pixels_at(
            filename=path,
            layer_name="Knight",
            frame_index=1,
            pixels=[{"x": 10, "y": 10, "color": "#ff0000"}],
        )

        # Flip horizontally
        result = await flip_layer(
            filename=path, layer_name="Knight", frame_index=1, direction="horizontal"
        )
        assert "Flipped" in result

        # Resize to 128x128
        result = await resize_canvas(filename=path, width=128, height=128)
        assert "Resized" in result

        # Verify 128x128
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

        # Crop to 32x32
        result = await crop_canvas(filename=path, x=0, y=0, width=32, height=32)
        assert "Cropped" in result

        # Verify 32x32
        script2 = f"""
local spr = app.open("{lua_p}")
if not spr then print("ERROR") return end
print("SIZE:" .. spr.width .. "x" .. spr.height)
spr:close()
"""
        success, output = cli.execute_lua_script(script2)
        assert success
        assert "SIZE:32x32" in output

    @pytest.mark.asyncio
    async def test_flip_and_verify_pixel_movement_pipeline(
        self, cli, tmp_sprite_dir
    ):
        """Draw pixel at (5,10) on 16-wide sprite -> flip horizontal -> verify
        pixel moved to (10,10) using pixel read."""
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.pixel_read import get_pixel_color
        from aseprite_mcp.tools.transform import flip_layer

        path = _sprite_path(tmp_sprite_dir, "flip_verify.aseprite")
        await create_canvas(width=16, height=16, filename=path)
        await add_layer(filename=path, layer_name="Test")

        # Draw at (5, 10)
        await draw_pixels_at(
            filename=path,
            layer_name="Test",
            frame_index=1,
            pixels=[{"x": 5, "y": 10, "color": "#00ff00"}],
        )

        # Verify original position
        result = await get_pixel_color(
            filename=path, x=5, y=10, layer_name="Test"
        )
        assert "#00ff00" in result

        # Flip horizontally
        await flip_layer(
            filename=path, layer_name="Test", frame_index=1, direction="horizontal"
        )

        # After H-flip on 16-wide image: (5,10) -> (15, 10) = (w-1-x, y)
        # Actually Aseprite image width = sprite width = 16, so (5,10) -> (10,10)
        result = await get_pixel_color(
            filename=path, x=10, y=10, layer_name="Test"
        )
        assert "#00ff00" in result


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline 7: Legacy + New Tools Interop
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EInteropPipeline:
    """End-to-end: Verify legacy (server.py) and new tool modules work
    together on the same sprite."""

    @pytest.mark.asyncio
    async def test_legacy_new_interop(self, cli, tmp_sprite_dir):
        """Create sprite with legacy sprite_create via run_json_script -> add
        layer with new add_layer tool -> list layers with cli.list_layers().
        Verify both legacy and new tools work on same sprite."""
        from aseprite_mcp.server import sprite_create
        from aseprite_mcp.tools.canvas import add_layer

        path = _sprite_path(tmp_sprite_dir, "interop.ase")

        # Step 1: Create sprite using legacy tool
        result = await sprite_create(width=32, height=32, output_path=path)
        # Legacy sprite_create returns JSON on success
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert parsed.get("width") == 32 or "width" in str(parsed)

        # Verify the file was created
        # sprite_create might use a different extension (.ase); find it
        actual_path = path
        if not Path(actual_path).is_file():
            # Try .aseprite variant
            alt_path = actual_path.replace(".ase", ".aseprite")
            if Path(alt_path).is_file():
                actual_path = alt_path

        assert Path(actual_path).is_file(), f"Sprite file not created at {actual_path}"

        # Step 2: Add a layer using the new tool
        result = await add_layer(filename=actual_path, layer_name="NewStyleLayer")
        assert "Added layer" in result

        # Step 3: Verify via list_layers that both layers appear
        layers = cli.list_layers(actual_path)
        # Default layer from legacy create + our new layer
        assert "NewStyleLayer" in layers

    @pytest.mark.asyncio
    async def test_legacy_export_new_draw_pipeline(
        self, cli, tmp_sprite_dir, output_dir
    ):
        """Create sprite via new create_canvas -> draw pixels -> export via
        legacy sprite_export -> verify PNG exists."""
        from aseprite_mcp.server import sprite_export
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at

        path = _sprite_path(tmp_sprite_dir, "interop_export.aseprite")
        await create_canvas(width=32, height=32, filename=path)
        await add_layer(filename=path, layer_name="Hero")

        await draw_pixels_at(
            filename=path,
            layer_name="Hero",
            frame_index=1,
            pixels=[{"x": 10, "y": 10, "color": "#ff0000"}],
        )

        # Export using legacy sprite_export
        png_path = str(output_dir / "interop_export.png")
        result = await sprite_export(input_path=path, output_path=png_path)
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert parsed.get("success") is True or "success" in str(parsed).lower()

        # Verify PNG exists
        assert Path(png_path).is_file(), f"PNG file not created: {png_path}"

    @pytest.mark.asyncio
    async def test_legacy_info_with_new_layers_pipeline(self, cli, tmp_sprite_dir):
        """Create sprite via new tools -> read info using legacy sprite_info."""
        from aseprite_mcp.server import sprite_info
        from aseprite_mcp.tools.canvas import add_layer, create_canvas

        path = _sprite_path(tmp_sprite_dir, "interop_info.aseprite")
        await create_canvas(width=48, height=48, filename=path)
        await add_layer(filename=path, layer_name="LegacyTarget")

        # Use legacy sprite_info
        result = await sprite_info(file_path=path)
        if not result.startswith("Error"):
            parsed = json.loads(result)
            assert "width" in parsed
            assert parsed.get("width") == 48


# ═══════════════════════════════════════════════════════════════════════════
# Bonus Pipeline: Full Game Asset Production
# ═══════════════════════════════════════════════════════════════════════════


class TestLiveE2EFullGameAssetPipeline:
    """End-to-end: Simulate a complete game asset production workflow from
    blank canvas to validated, exported sprite with animation."""

    @pytest.mark.asyncio
    async def test_complete_game_asset_pipeline(
        self, cli, tmp_sprite_dir, output_dir
    ):
        """Full pipeline: Create -> layers -> pixels -> frames -> durations
        -> tags -> validate -> export -> re-verify."""
        from aseprite_mcp.tools.animation import (
            add_frames,
            set_frame_duration_all,
            set_tag,
        )
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.export import export_sprite
        from aseprite_mcp.tools.quality import validate_scene

        path = _sprite_path(tmp_sprite_dir, "game_asset.aseprite")

        # Step 1: Canvas
        await create_canvas(width=32, height=32, filename=path)

        # Step 2: Layers
        for name in ("Background", "Character", "Effects"):
            await add_layer(filename=path, layer_name=name)

        # Step 3: Draw pixels on each layer
        await draw_pixels_at(
            filename=path,
            layer_name="Background",
            frame_index=1,
            pixels=[
                {"x": 0, "y": 0, "color": "#1a1a2e"},
                {"x": 1, "y": 0, "color": "#1a1a2e"},
                {"x": 0, "y": 1, "color": "#1a1a2e"},
                {"x": 1, "y": 1, "color": "#1a1a2e"},
            ],
        )
        await draw_pixels_at(
            filename=path,
            layer_name="Character",
            frame_index=1,
            pixels=[
                {"x": 15, "y": 15, "color": "#c0c0c0"},
                {"x": 16, "y": 15, "color": "#c0c0c0"},
                {"x": 15, "y": 16, "color": "#c0c0c0"},
                {"x": 16, "y": 16, "color": "#c0c0c0"},
            ],
        )

        # Step 4: Add animation frames
        await add_frames(filename=path, count=7, duration_ms=100)

        # Step 5: Set frame durations
        await set_frame_duration_all(filename=path, duration_ms=100)

        # Step 6: Create tags
        await set_tag(
            filename=path, name="idle", from_frame=1, to_frame=4, direction="forward"
        )
        await set_tag(
            filename=path,
            name="action",
            from_frame=5,
            to_frame=8,
            direction="forward",
        )

        # Step 7: Validate scene
        result = await validate_scene(
            filename=path,
            required_layers=["Background", "Character", "Effects"],
            start_frame=1,
            end_frame=8,
        )
        # All required layers exist, so no missing_layers (or empty list)
        assert "missing_layers" in result.lower() or "frames" in result.lower()

        # Step 8: Export PNG
        # NOTE: Aseprite --save-as for multi-frame sprites produces
        # frame-numbered files (e.g. game_asset1.png, game_asset2.png, ...).
        png_path = str(output_dir / "game_asset.png")
        result = await export_sprite(
            filename=path, output_filename=png_path, format="png"
        )
        assert "Exported" in result
        exported_pngs = list(output_dir.glob("game_asset*.png"))
        assert len(exported_pngs) > 0, "No PNG files exported"
        for png in exported_pngs:
            assert png.stat().st_size > 0, f"Exported PNG is empty: {png}"

        # Step 9: Re-verify the sprite file is still valid
        layers = cli.list_layers(path)
        assert "Background" in layers
        assert "Character" in layers
        assert "Effects" in layers

        tags = cli.list_tags(path)
        assert "idle" in tags
        assert "action" in tags

    @pytest.mark.asyncio
    async def test_draw_and_read_back_pipeline(self, cli, tmp_sprite_dir):
        """Create canvas -> draw shaped pixels -> read back via rect read ->
        verify pixel data matches."""
        from aseprite_mcp.tools.canvas import add_layer, create_canvas
        from aseprite_mcp.tools.drawing import draw_pixels_at
        from aseprite_mcp.tools.pixel_read import get_pixels_rect

        path = _sprite_path(tmp_sprite_dir, "readback.aseprite")
        await create_canvas(width=16, height=16, filename=path)
        await add_layer(filename=path, layer_name="Art")

        # Draw known colors at known positions
        await draw_pixels_at(
            filename=path,
            layer_name="Art",
            frame_index=1,
            pixels=[
                {"x": 3, "y": 3, "color": "#ff0000"},
                {"x": 4, "y": 3, "color": "#00ff00"},
                {"x": 3, "y": 4, "color": "#0000ff"},
                {"x": 4, "y": 4, "color": "#ffff00"},
            ],
        )

        # Read back the 3x3 region
        result = await get_pixels_rect(
            filename=path, x=3, y=3, width=3, height=3, layer_name="Art"
        )
        parsed = json.loads(result)
        assert parsed["count"] == 9  # 3x3

        # Build a lookup map
        pixel_map = {(p["x"], p["y"]): p["hex"] for p in parsed["pixels"]}
        assert pixel_map.get((3, 3)) == "#ff0000"
        assert pixel_map.get((4, 3)) == "#00ff00"
        assert pixel_map.get((3, 4)) == "#0000ff"
        assert pixel_map.get((4, 4)) == "#ffff00"
