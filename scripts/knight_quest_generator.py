#!/usr/bin/env python3
"""Knight Quest RPG Asset Generator

Generates a complete set of pixel art game assets for a platforming RPG
where a knight must save a princess from a dragon, battling goblins,
skeletons, and slimes along the way.

Usage:
    uv run python scripts/knight_quest_generator.py

Output:
    generated_assets/knight_quest/
    ├── hero/
    │   ├── knight_idle.aseprite
    │   ├── knight_idle.png
    │   ├── knight_walk.aseprite
    │   ├── knight_walk.png
    │   ├── knight_melee_attack.aseprite
    │   ├── knight_melee_attack.png
    │   ├── knight_ranged_attack.aseprite
    │   ├── knight_ranged_attack.png
    │   └── knight_spritesheet.png
    ├── monsters/
    │   ├── goblin.aseprite
    │   ├── goblin.png
    │   ├── skeleton.aseprite
    │   ├── skeleton.png
    │   ├── slime.aseprite
    │   ├── slime.png
    │   ├── dragon_boss.aseprite
    │   └── dragon_boss.png
    ├── environment/
    │   ├── dungeon_tiles.aseprite
    │   ├── dungeon_tiles.png
    │   ├── castle_tower.aseprite
    │   └── castle_tower.png
    ├── effects/
    │   ├── melee_slash.aseprite
    │   ├── melee_slash.png
    │   ├── magic_bolt.aseprite
    │   ├── magic_bolt.png
    │   ├── fireball_spell.aseprite
    │   └── fireball_spell.gif
    └── cutscene/
        ├── princess_rescue.aseprite
        └── princess_rescue.png
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Aseprite binary discovery
# ---------------------------------------------------------------------------
ASEPRITE_PATH = os.environ.get("ASEPRITE_PATH", shutil.which("aseprite") or "")
if not ASEPRITE_PATH:
    for p in [
        r"E:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe",
        r"C:\Program Files\Aseprite\aseprite.exe",
        r"C:\Program Files (x86)\Aseprite\aseprite.exe",
        "/usr/bin/aseprite",
        "/usr/local/bin/aseprite",
        "/usr/lib/aseprite/aseprite",
        "/snap/bin/aseprite",
        str(Path.home() / "aseprite" / "build" / "bin" / "aseprite"),
    ]:
        if Path(p).is_file():
            ASEPRITE_PATH = p
            break

if not ASEPRITE_PATH or not Path(ASEPRITE_PATH).is_file():
    print("ERROR: Aseprite binary not found.")
    print("Set ASEPRITE_PATH environment variable or install Aseprite.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CLI setup
# ---------------------------------------------------------------------------
from aseprite_mcp.aseprite_cli import AsepriteCLI  # noqa: E402
from aseprite_mcp.config import AsepriteConfig  # noqa: E402

BASE_DIR = Path("generated_assets/knight_quest")
BASE_DIR.mkdir(parents=True, exist_ok=True)

config = AsepriteConfig(
    aseprite_path=ASEPRITE_PATH,
    tmp_dir=BASE_DIR / ".tmp_scripts",
    output_dir=BASE_DIR,
)
config.ensure_tmp_dir()
config.ensure_output_dir()

cli = AsepriteCLI(config)


def lua_path(path: str | Path) -> str:
    """Normalize a path for Lua string literals (forward slashes)."""
    return str(path).replace("\\", "/")


def _export_spritesheet_png(aseprite_path: str | Path, png_path: str | Path) -> None:
    """Export a sprite as a single horizontal spritesheet PNG."""
    cli.run_batch([
        str(aseprite_path),
        "--sheet", lua_path(png_path),
        "--sheet-type", "horizontal",
    ])


def _export_gif(aseprite_path: str | Path, gif_path: str | Path) -> None:
    """Export a sprite as an animated GIF."""
    cli.run_batch([str(aseprite_path), "--save-as", lua_path(gif_path)])


# =====================================================================
# PIXEL ART DATA
# =====================================================================
# Each entry: (x, y, r, g, b) — alpha is always 255 unless noted.

# ---- Knight body (32x32) ----
# Helmet: silver (192,192,192) — 6x5 block centred at x=13..18, y=4..8
# Visor slit: black (0,0,0) — two pixels for eyes
# Torso (blue shirt): (0,0,180) area at y=10..17
# Armor plate over torso: silver (192,192,192) centre 4x4
# Arms: (0,0,180) 2px wide each side
# Legs: (0,0,180) + brown boots (139,69,19)
# Sword: silver blade + brown hilt (held at right side)
# Cape: red (204,0,0) trailing from left shoulder

_KNIGHT_BODY = [
    # Helmet top row
    (13,4,192,192,192),(14,4,192,192,192),(15,4,192,192,192),(16,4,192,192,192),(17,4,192,192,192),(18,4,192,192,192),
    (13,5,192,192,192),(14,5,192,192,192),(15,5,192,192,192),(16,5,192,192,192),(17,5,192,192,192),(18,5,192,192,192),
    # Visor slit (eyes)
    (13,6,192,192,192),(14,6,0,0,0),(15,6,192,192,192),(16,6,192,192,192),(17,6,0,0,0),(18,6,192,192,192),
    # Helmet lower
    (13,7,192,192,192),(14,7,192,192,192),(15,7,192,192,192),(16,7,192,192,192),(17,7,192,192,192),(18,7,192,192,192),
    (14,8,192,192,192),(15,8,192,192,192),(16,8,192,192,192),(17,8,192,192,192),
    # Neck
    (15,9,0,0,180),(16,9,0,0,180),
    # Torso (blue shirt)
    *[(x,10,0,0,180) for x in range(12,20)],
    *[(x,11,0,0,180) for x in range(11,21)],
    *[(x,12,0,0,180) for x in range(11,21)],
    *[(x,13,0,0,180) for x in range(11,21)],
    *[(x,14,0,0,180) for x in range(11,21)],
    *[(x,15,0,0,180) for x in range(11,21)],
    *[(x,16,0,0,180) for x in range(12,20)],
    *[(x,17,0,0,180) for x in range(12,20)],
]

_KNIGHT_ARMOR = [
    # Armor plate (silver) over centre of torso
] + [(x,y,192,192,192) for x in range(13,19) for y in range(11,15)]

_KNIGHT_SWORD_REST = [
    # Vertical blade at right side
    (23,8,192,192,192),(23,9,192,192,192),(23,10,192,192,192),
    (23,11,192,192,192),(23,12,192,192,192),(23,13,192,192,192),
    (23,14,192,192,192),(23,15,192,192,192),(23,16,192,192,192),
    (23,17,192,192,192),(23,18,192,192,192),
    # Cross-guard
    (22,13,192,192,192),(24,13,192,192,192),
    # Hilt (brown)
    (22,14,139,69,19),(22,15,139,69,19),(23,14,139,69,19),(23,15,139,69,19),(24,14,139,69,19),(24,15,139,69,19),
]

_KNIGHT_CAPE = [
    # Red cape from left shoulder
    *[(9,y,204,0,0) for y in range(10,18)],
    *[(10,y,204,0,0) for y in range(10,17)],
    # Cape flowing edge
    (8,11,204,0,0),(8,12,204,0,0),
]

_KNIGHT_LEGS = [
    # Left leg
    (13,18,0,0,180),(14,18,0,0,180),
    (13,19,0,0,180),(14,19,0,0,180),
    (13,20,0,0,180),(14,20,0,0,180),
    (13,21,0,0,180),(14,21,0,0,180),
    (13,22,0,0,180),(14,22,0,0,180),
    (13,23,0,0,180),(14,23,0,0,180),
    (13,24,0,0,180),(14,24,0,0,180),
    (13,25,139,69,19),(14,25,139,69,19),
    (13,26,139,69,19),(14,26,139,69,19),
    # Right leg
    (17,18,0,0,180),(18,18,0,0,180),
    (17,19,0,0,180),(18,19,0,0,180),
    (17,20,0,0,180),(18,20,0,0,180),
    (17,21,0,0,180),(18,21,0,0,180),
    (17,22,0,0,180),(18,22,0,0,180),
    (17,23,0,0,180),(18,23,0,0,180),
    (17,24,0,0,180),(18,24,0,0,180),
    (17,25,139,69,19),(18,25,139,69,19),
    (17,26,139,69,19),(18,26,139,69,19),
]

# ---- Goblin (16x16) ----
_GOBLIN_BODY = [
    # Small green head
    (6,3,0,170,0),(7,3,0,170,0),(8,3,0,170,0),(9,3,0,170,0),
    (5,4,0,170,0),(6,4,0,170,0),(7,4,255,255,0),(8,4,255,255,0),(9,4,0,170,0),(10,4,0,170,0),
    (6,5,0,170,0),(7,5,0,0,0),(8,5,0,0,0),(9,5,0,170,0),
    (5,6,0,170,0),(6,6,0,170,0),(7,6,0,102,0),(8,6,0,102,0),(9,6,0,170,0),(10,6,0,170,0),
    # Hunched body
    (4,7,0,170,0),(5,7,0,170,0),(6,7,0,170,0),(7,7,0,170,0),(8,7,0,170,0),(9,7,0,170,0),(10,7,0,170,0),(11,7,0,170,0),
    (4,8,0,170,0),(5,8,0,170,0),(6,8,0,170,0),(7,8,0,102,0),(8,8,0,102,0),(9,8,0,170,0),(10,8,0,170,0),(11,8,0,170,0),
    (5,9,0,170,0),(6,9,0,170,0),(7,9,0,170,0),(8,9,0,170,0),(9,9,0,170,0),(10,9,0,170,0),
    # Legs
    (5,10,0,170,0),(6,10,0,170,0),(9,10,0,170,0),(10,10,0,170,0),
    (5,11,0,170,0),(6,11,0,170,0),(9,11,0,170,0),(10,11,0,170,0),
    (5,12,139,69,19),(6,12,139,69,19),(9,12,139,69,19),(10,12,139,69,19),
]

_GOBLIN_AXE = [
    # Brown handle
    (12,4,139,69,19),(12,5,139,69,19),(12,6,139,69,19),(12,7,139,69,19),(12,8,139,69,19),
    # Axe head (dark grey)
    (13,4,80,80,80),(14,4,80,80,80),(15,4,80,80,80),
    (13,5,80,80,80),(14,5,80,80,80),(15,5,80,80,80),
    (13,6,80,80,80),(14,6,80,80,80),
]

# ---- Skeleton (16x24) ----
_SKELETON_BODY = [
    # Skull
    (6,1,204,204,204),(7,1,204,204,204),(8,1,204,204,204),(9,1,204,204,204),
    (5,2,204,204,204),(6,2,204,204,204),(7,2,0,0,0),(8,2,0,0,0),(9,2,204,204,204),(10,2,204,204,204),
    (6,3,204,204,204),(7,3,0,0,0),(8,3,0,0,0),(9,3,204,204,204),
    (6,4,204,204,204),(7,4,204,204,204),(8,4,204,204,204),(9,4,204,204,204),
    (7,5,204,204,204),(8,5,204,204,204),
    # Spine
    (7,6,204,204,204),(8,6,204,204,204),
    (7,7,136,136,136),(8,7,136,136,136),
    (7,8,204,204,204),(8,8,204,204,204),
    (7,9,136,136,136),(8,9,136,136,136),
    (7,10,204,204,204),(8,10,204,204,204),
    # Ribcage
    (5,7,204,204,204),(6,7,204,204,204),(9,7,204,204,204),(10,7,204,204,204),
    (5,8,204,204,204),(6,8,204,204,204),(9,8,204,204,204),(10,8,204,204,204),
    (5,9,204,204,204),(6,9,204,204,204),(9,9,204,204,204),(10,9,204,204,204),
    # Arms (bone sticks)
    (4,7,204,204,204),(4,8,204,204,204),(4,9,204,204,204),
    (11,7,204,204,204),(11,8,204,204,204),(11,9,204,204,204),
    # Pelvis
    (6,11,204,204,204),(7,11,204,204,204),(8,11,204,204,204),(9,11,204,204,204),
    # Legs
    (6,12,204,204,204),(7,12,136,136,136),
    (6,13,204,204,204),(7,13,136,136,136),
    (6,14,204,204,204),(7,14,136,136,136),
    (6,15,204,204,204),(7,15,204,204,204),
    (8,12,204,204,204),(9,12,136,136,136),
    (8,13,204,204,204),(9,13,136,136,136),
    (8,14,204,204,204),(9,14,136,136,136),
    (8,15,204,204,204),(9,15,204,204,204),
    # Feet
    (5,16,204,204,204),(6,16,204,204,204),
    (9,16,204,204,204),(10,16,204,204,204),
]

_SKELETON_SHIELD = [
    # Bone rectangle shield on left arm
    (2,7,136,136,136),(3,7,136,136,136),
    (1,8,136,136,136),(2,8,204,204,204),(3,8,204,204,204),
    (1,9,136,136,136),(2,9,204,204,204),(3,9,204,204,204),
    (1,10,136,136,136),(2,10,204,204,204),(3,10,204,204,204),
    (2,11,136,136,136),(3,11,136,136,136),
]

# ---- Slime (16x12) ----
_SLIME_BODY_FRAME1 = [
    # Top curve
    (6,3,68,68,255),(7,3,68,68,255),(8,3,68,68,255),(9,3,68,68,255),
    # Upper body
    (5,4,68,68,255),(6,4,68,68,255),(7,4,255,255,255),(8,4,255,255,255),(9,4,68,68,255),(10,4,68,68,255),
    (4,5,68,68,255),(5,5,68,68,255),(6,5,68,68,255),(7,5,0,0,0),(8,5,0,0,0),(9,5,68,68,255),(10,5,68,68,255),(11,5,68,68,255),
    # Mid body
    (4,6,68,68,255),(5,6,68,68,255),(6,6,68,68,255),(7,6,68,68,255),(8,6,68,68,255),(9,6,68,68,255),(10,6,68,68,255),(11,6,68,68,255),
    (4,7,68,68,255),(5,7,68,68,255),(6,7,68,68,255),(7,7,68,68,255),(8,7,68,68,255),(9,7,68,68,255),(10,7,68,68,255),(11,7,68,68,255),
    # Lower body (darker shading)
    (4,8,34,34,170),(5,8,34,34,170),(6,8,34,34,170),(7,8,34,34,170),(8,8,34,34,170),(9,8,34,34,170),(10,8,34,34,170),(11,8,34,34,170),
    (5,9,34,34,170),(6,9,34,34,170),(7,9,34,34,170),(8,9,34,34,170),(9,9,34,34,170),(10,9,34,34,170),
    # Bottom
    (6,10,34,34,170),(7,10,34,34,170),(8,10,34,34,170),(9,10,34,34,170),
]

# ---- Dragon boss (64x48) ----
_DRAGON_BODY = [
    # Head
    *[(x,5,204,0,0) for x in range(20,30)],
    *[(x,6,204,0,0) for x in range(18,32)],
    # Eyes
    (21,5,255,255,0),(28,5,255,255,0),
    # Mouth
    *[(x,7,204,0,0) for x in range(18,32)],
    (19,8,204,0,0),
    # Neck
    *[(x,8,204,0,0) for x in range(20,30)],
    *[(x,9,204,0,0) for x in range(20,30)],
    # Body (large rectangle)
    *[(x,y,204,0,0) for x in range(10,40) for y in range(10,28)],
    # Belly (lighter red)
    *[(x,y,230,80,40) for x in range(15,35) for y in range(15,27)],
    # Tail start
    *[(x,28,204,0,0) for x in range(12,38)],
    *[(x,29,204,0,0) for x in range(8,42)],
    *[(x,30,180,0,0) for x in range(6,44)],
    *[(x,31,180,0,0) for x in range(4,46)],
    *[(x,32,180,0,0) for x in range(2,48)],
    # Tail taper
    *[(x,33,160,0,0) for x in range(0,50)],
    *[(x,34,160,0,0) for x in range(0,44)],
    *[(x,35,140,0,0) for x in range(0,38)],
    *[(x,36,140,0,0) for x in range(0,30)],
    *[(x,37,120,0,0) for x in range(0,22)],
    *[(x,38,120,0,0) for x in range(2,16)],
    (4,39,100,0,0),(5,39,100,0,0),(6,39,100,0,0),
    # Legs (stubby)
    *[(x,y,204,0,0) for x in range(12,18) for y in range(28,36)],
    *[(x,y,204,0,0) for x in range(32,38) for y in range(28,36)],
    # Foot claws
    (10,36,180,0,0),(11,36,180,0,0),(12,36,180,0,0),
    (17,36,180,0,0),(18,36,180,0,0),
    (32,36,180,0,0),(37,36,180,0,0),(38,36,180,0,0),
]

_DRAGON_WINGS = [
    # Left wing (dark red, large polygon)
    *[(x,2,136,0,0) for x in range(0,14)],
    *[(x,3,136,0,0) for x in range(0,12)],
    *[(x,4,136,0,0) for x in range(0,10)],
    *[(x,5,136,0,0) for x in range(0,10)],
    *[(x,6,136,0,0) for x in range(0,9)],
    *[(x,7,136,0,0) for x in range(0,9)],
    *[(x,8,136,0,0) for x in range(0,11)],
    *[(x,9,136,0,0) for x in range(0,12)],
    *[(x,10,136,0,0) for x in range(2,13)],
    # Right wing
    *[(x,2,136,0,0) for x in range(50,64)],
    *[(x,3,136,0,0) for x in range(52,64)],
    *[(x,4,136,0,0) for x in range(54,64)],
    *[(x,5,136,0,0) for x in range(54,64)],
    *[(x,6,136,0,0) for x in range(55,64)],
    *[(x,7,136,0,0) for x in range(55,64)],
    *[(x,8,136,0,0) for x in range(53,64)],
    *[(x,9,136,0,0) for x in range(52,64)],
    *[(x,10,136,0,0) for x in range(51,62)],
]

_DRAGON_FIRE = [
    # Fire breath (orange/red) on frames 5-6
    *[(x,6,255,102,0) for x in range(30,40)],
    *[(x,7,255,102,0) for x in range(32,42)],
    *[(x,6,255,200,0) for x in range(34,38)],
    *[(x,7,255,200,0) for x in range(36,40)],
    *[(x,8,255,102,0) for x in range(34,44)],
    *[(x,9,255,51,0) for x in range(38,48)],
    *[(x,8,255,51,0) for x in range(40,50)],
    *[(x,7,255,51,0) for x in range(42,52)],
    *[(x,6,255,102,0) for x in range(44,54)],
]


# =====================================================================
# Helper: pixel list → Lua putPixel lines
# =====================================================================

def _pixels_to_lua(pixels: list[tuple], var: str = "img") -> str:
    """Convert a list of (x, y, r, g, b) tuples to Lua putPixel calls."""
    lines: list[str] = []
    for x, y, r, g, b in pixels:
        lines.append(f"{var}:putPixel({x}, {y}, Color({r}, {g}, {b}, 255))")
    return "\n    ".join(lines)



# =====================================================================
# GENERATION FUNCTIONS
# =====================================================================


def generate_hero_sprites() -> None:
    """Generate all hero (knight) sprite assets."""
    hero_dir = BASE_DIR / "hero"
    hero_dir.mkdir(parents=True, exist_ok=True)

    _generate_knight_idle(hero_dir)
    _generate_knight_walk(hero_dir)
    _generate_knight_melee_attack(hero_dir)
    _generate_knight_ranged_attack(hero_dir)
    _generate_knight_spritesheet(hero_dir)


def _generate_knight_idle(hero_dir: Path) -> None:
    """Generate the knight idle animation (32x32, 4 frames)."""
    path = hero_dir / "knight_idle.aseprite"
    lp = lua_path(path)
    print("  Creating knight_idle.aseprite...")

    body_lua = _pixels_to_lua(_KNIGHT_BODY + _KNIGHT_LEGS)
    armor_lua = _pixels_to_lua(_KNIGHT_ARMOR)
    sword_lua = _pixels_to_lua(_KNIGHT_SWORD_REST)
    cape_lua = _pixels_to_lua(_KNIGHT_CAPE)

    script = f"""
local spr = Sprite(32, 32)
spr.layers[1].name = "Body"

local armor_layer = spr:newLayer()
armor_layer.name = "Armor"

local sword_layer = spr:newLayer()
sword_layer.name = "Sword"

local cape_layer = spr:newLayer()
cape_layer.name = "Cape"

-- Draw frame 1
app.transaction(function()
    -- Body layer (default cel)
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    -- Armor layer
    local armor_cel = spr:newCel(armor_layer, 1)
    local aimg = armor_cel.image
    {armor_lua}

    -- Sword layer
    local sword_cel = spr:newCel(sword_layer, 1)
    local simg = sword_cel.image
    {sword_lua}

    -- Cape layer
    local cape_cel = spr:newCel(cape_layer, 1)
    local cimg = cape_cel.image
    {cape_lua}
end)

-- Add frames 2-4 for breathing animation
for i = 2, 4 do
    spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local src = layer:cel(1)
        if src and src.image then
            local nc = spr:newCel(layer, i)
            nc.image = src.image:clone()
        end
    end
end

-- Breathing: offset body position on frames 2 and 4 (bob 1px up)
app.transaction(function()
    for _, frame_idx in ipairs({{2, 4}}) do
        for _, layer in ipairs(spr.layers) do
            local cel = layer:cel(frame_idx)
            if cel and cel.image then
                cel.position = Point(cel.position.x, cel.position.y - 1)
            end
        end
    end
end)

-- Set durations
for i = 1, 4 do
    spr.frames[i].duration = 0.15
end

-- Add idle tag
local t = spr:newTag(spr.frames[1], spr.frames[4])
t.name = "idle"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  knight_idle.aseprite ({size:,} bytes)")
        # Export spritesheet PNG
        png_path = hero_dir / "knight_idle.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  knight_idle.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_knight_walk(hero_dir: Path) -> None:
    """Generate the knight walk cycle (32x32, 8 frames)."""
    path = hero_dir / "knight_walk.aseprite"
    lp = lua_path(path)
    print("  Creating knight_walk.aseprite...")

    body_lua = _pixels_to_lua(_KNIGHT_BODY + _KNIGHT_LEGS)
    armor_lua = _pixels_to_lua(_KNIGHT_ARMOR)
    sword_lua = _pixels_to_lua(_KNIGHT_SWORD_REST)
    cape_lua = _pixels_to_lua(_KNIGHT_CAPE)

    # Walk cycle: legs alternate positions, cape sways
    # Frame 1: left leg forward, right back
    # Frame 3: legs neutral
    # Frame 5: right leg forward, left back
    # Frame 7: legs neutral
    _leg_offsets = [
        # (left_leg_dx, left_leg_dy, right_leg_dx, right_leg_dy)
        (0, 0, 0, 0),   # frame 1: neutral
        (-1, 0, 1, 0),   # frame 2: left forward
        (-2, 0, 2, -1),   # frame 3: stride
        (-1, 0, 1, 0),   # frame 4: passing
        (0, 0, 0, 0),   # frame 5: neutral
        (1, 0, -1, 0),   # frame 6: right forward
        (2, -1, -2, 0),   # frame 7: stride
        (1, 0, -1, 0),   # frame 8: passing
    ]
    _cape_sway = [0, 1, 2, 1, 0, -1, -2, -1]

    script = f"""
local spr = Sprite(32, 32)
spr.layers[1].name = "Body"

local armor_layer = spr:newLayer()
armor_layer.name = "Armor"

local sword_layer = spr:newLayer()
sword_layer.name = "Sword"

local cape_layer = spr:newLayer()
cape_layer.name = "Cape"

-- Draw frame 1 base
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local armor_cel = spr:newCel(armor_layer, 1)
    local aimg = armor_cel.image
    {armor_lua}

    local sword_cel = spr:newCel(sword_layer, 1)
    local simg = sword_cel.image
    {sword_lua}

    local cape_cel = spr:newCel(cape_layer, 1)
    local cimg = cape_cel.image
    {cape_lua}
end)

-- Add frames 2-8 and copy with offsets
local leg_offsets = {{
    {{0, 0, 0, 0}},
    {{-1, 0, 1, 0}},
    {{-2, 0, 2, -1}},
    {{-1, 0, 1, 0}},
    {{0, 0, 0, 0}},
    {{1, 0, -1, 0}},
    {{2, -1, -2, 0}},
    {{1, 0, -1, 0}},
}}
local cape_sway = {{0, 1, 2, 1, 0, -1, -2, -1}}

for i = 2, 8 do
    spr:newEmptyFrame()
    -- Copy all layers from frame 1
    for _, layer in ipairs(spr.layers) do
        local src_cel = layer:cel(1)
        if src_cel and src_cel.image then
            local new_cel = spr:newCel(layer, i)
            new_cel.image = src_cel.image:clone()
        end
    end
    -- Offset body/legs for walk animation
    local body_cel = spr.layers["Body"]:cel(i)
    if body_cel then
        local off = leg_offsets[i]
        -- Slight vertical bob on stride frames
        local bob = 0
        if i == 3 or i == 7 then bob = -1 end
        body_cel.position = Point(off[1], bob)
    end
    -- Cape sway
    local cape_cel = cape_layer:cel(i)
    if cape_cel then
        cape_cel.position = Point(cape_sway[i], 0)
    end
end

-- Set durations
for i = 1, 8 do
    spr.frames[i].duration = 0.1
end

local wt = spr:newTag(spr.frames[1], spr.frames[8])
wt.name = "walk"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  knight_walk.aseprite ({size:,} bytes)")
        png_path = hero_dir / "knight_walk.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  knight_walk.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_knight_melee_attack(hero_dir: Path) -> None:
    """Generate knight melee attack animation (48x32, 6 frames)."""
    path = hero_dir / "knight_melee_attack.aseprite"
    lp = lua_path(path)
    print("  Creating knight_melee_attack.aseprite...")

    # Knight body (same as idle but positioned for 48x32 canvas)
    body_lua = _pixels_to_lua(_KNIGHT_BODY + _KNIGHT_LEGS)
    armor_lua = _pixels_to_lua(_KNIGHT_ARMOR)
    cape_lua = _pixels_to_lua(_KNIGHT_CAPE)

    # Sword at rest (initial position)
    sword_rest_lua = _pixels_to_lua(_KNIGHT_SWORD_REST)

    # Slash effect pixels for frames 3-5
    slash_pixels = [
        # Arc of slash (white pixels)
        (30,8,255,255,255),(31,7,255,255,255),(32,6,255,255,255),
        (33,5,255,255,255),(34,4,255,255,255),(35,3,255,255,255),
        (30,9,255,255,255),(31,8,255,255,255),(32,7,255,255,255),
        (33,6,255,255,255),(34,5,255,255,255),
        # Dimmer trail
        (29,10,200,200,255),(30,9,200,200,255),(31,8,200,200,255),
    ]
    slash_lua = _pixels_to_lua(slash_pixels)

    script = f"""
local spr = Sprite(48, 32)
spr.layers[1].name = "Body"

local sword_layer = spr:newLayer()
sword_layer.name = "Sword"

local armor_layer = spr:newLayer()
armor_layer.name = "Armor"

local cape_layer = spr:newLayer()
cape_layer.name = "Cape"

local effects_layer = spr:newLayer()
effects_layer.name = "Effects"

-- Draw frame 1 base
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local sword_cel = spr:newCel(sword_layer, 1)
    local simg = sword_cel.image
    {sword_rest_lua}

    local armor_cel = spr:newCel(armor_layer, 1)
    local aimg = armor_cel.image
    {armor_lua}

    local cape_cel = spr:newCel(cape_layer, 1)
    local cimg = cape_cel.image
    {cape_lua}
end)

-- Add frames 2-6
for i = 2, 6 do
    spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local src_cel = layer:cel(1)
        if src_cel and src_cel.image then
            local new_cel = spr:newCel(layer, i)
            new_cel.image = src_cel.image:clone()
        end
    end
end

-- Sword swing: tween position from rest to extended
app.transaction(function()
    -- Frame 2: sword starts moving (slight rotation implied by position)
    local s2 = sword_layer:cel(2)
    if s2 then s2.position = Point(2, -1) end
    -- Frame 3: sword at peak
    local s3 = sword_layer:cel(3)
    if s3 then s3.position = Point(4, -3) end
    -- Frame 4: sword extended
    local s4 = sword_layer:cel(4)
    if s4 then s4.position = Point(6, -4) end
    -- Frame 5: sword returning
    local s5 = sword_layer:cel(5)
    if s5 then s5.position = Point(3, -2) end
    -- Frame 6: back to rest
    local s6 = sword_layer:cel(6)
    if s6 then s6.position = Point(1, 0) end
end)

-- Add slash effect pixels on frames 3-5
app.transaction(function()
    for fi = 3, 5 do
        local cel = effects_layer:cel(fi)
        if cel then
            local img = cel.image
            {slash_lua}
        end
    end
    -- Fade effects: reduce opacity on later frames
    local e4 = effects_layer:cel(4)
    if e4 then effects_layer.opacity = 180 end
    local e5 = effects_layer:cel(5)
    -- frame 5 more transparent (we just reduce the effect layer opacity for that frame)
end)

-- Set durations (fast attack)
for i = 1, 6 do
    spr.frames[i].duration = 0.06
end

local mt = spr:newTag(spr.frames[1], spr.frames[6])
mt.name = "melee_attack"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  knight_melee_attack.aseprite ({size:,} bytes)")
        png_path = hero_dir / "knight_melee_attack.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  knight_melee_attack.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_knight_ranged_attack(hero_dir: Path) -> None:
    """Generate knight ranged attack animation (48x32, 6 frames)."""
    path = hero_dir / "knight_ranged_attack.aseprite"
    lp = lua_path(path)
    print("  Creating knight_ranged_attack.aseprite...")

    body_lua = _pixels_to_lua(_KNIGHT_BODY + _KNIGHT_LEGS)
    armor_lua = _pixels_to_lua(_KNIGHT_ARMOR)
    cape_lua = _pixels_to_lua(_KNIGHT_CAPE)

    # Spell glow pixels (cyan) — drawn inline in the Lua script

    script = f"""
local spr = Sprite(48, 32)
spr.layers[1].name = "Body"

local spell_layer = spr:newLayer()
spell_layer.name = "Spell"

local armor_layer = spr:newLayer()
armor_layer.name = "Armor"

local cape_layer = spr:newLayer()
cape_layer.name = "Cape"

local effects_layer = spr:newLayer()
effects_layer.name = "Effects"

-- Draw frame 1 base
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local spell_cel = spr:newCel(spell_layer, 1)
    -- Magic bolt starts near hand
    local simg = spell_cel.image
    simg:putPixel(25, 12, Color(0, 200, 255, 255))
    simg:putPixel(26, 12, Color(0, 200, 255, 255))
    simg:putPixel(26, 11, Color(0, 255, 255, 255))
    simg:putPixel(26, 13, Color(0, 255, 255, 255))
    simg:putPixel(27, 12, Color(100, 200, 255, 255))

    local armor_cel = spr:newCel(armor_layer, 1)
    local aimg = armor_cel.image
    {armor_lua}

    local cape_cel = spr:newCel(cape_layer, 1)
    local cimg = cape_cel.image
    {cape_lua}
end)

-- Add frames 2-6 with bolt moving right
app.transaction(function()
    for i = 2, 6 do
        spr:newEmptyFrame()
        -- Copy body, armor, cape from frame 1
        for _, layer in ipairs({{
            spr.layers["Body"],
            spr.layers["Armor"],
            spr.layers["Cape"],
        }}) do
            if layer then
                local src = layer:cel(1)
                if src and src.image then
                    local nc = spr:newCel(layer, i)
                    nc.image = src.image:clone()
                end
            end
        end
        -- Spell bolt moves across
        local spell_cel = spr:newCel(spell_layer, i)
        local si = spell_cel.image
        -- Bolt position advances each frame
        local bx = 25 + (i - 1) * 5
        si:putPixel(bx, 12, Color(0, 200, 255, 255))
        si:putPixel(bx+1, 12, Color(0, 200, 255, 255))
        si:putPixel(bx, 11, Color(0, 255, 255, 255))
        si:putPixel(bx, 13, Color(0, 255, 255, 255))
        si:putPixel(bx+2, 12, Color(100, 200, 255, 255))
        -- Glow trail
        if bx - 2 >= 0 then
            si:putPixel(bx-2, 12, Color(0, 100, 200, 150))
            si:putPixel(bx-1, 12, Color(0, 150, 255, 200))
        end
        -- Effect glow around bolt
        local ecel = spr:newCel(effects_layer, i)
        local ei = ecel.image
        ei:putPixel(bx-1, 11, Color(0, 100, 200, 100))
        ei:putPixel(bx-1, 13, Color(0, 100, 200, 100))
        ei:putPixel(bx+2, 11, Color(0, 100, 200, 100))
        ei:putPixel(bx+2, 13, Color(0, 100, 200, 100))
    end
end)

-- Set durations
for i = 1, 6 do
    spr.frames[i].duration = 0.08
end

local rt = spr:newTag(spr.frames[1], spr.frames[6])
rt.name = "ranged_attack"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  knight_ranged_attack.aseprite ({size:,} bytes)")
        png_path = hero_dir / "knight_ranged_attack.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  knight_ranged_attack.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_knight_spritesheet(hero_dir: Path) -> None:
    """Export all knight animations as a horizontal spritesheet PNG."""
    print("  Creating knight_spritesheet.png...")
    idle_path = hero_dir / "knight_idle.aseprite"
    walk_path = hero_dir / "knight_walk.aseprite"
    melee_path = hero_dir / "knight_melee_attack.aseprite"
    ranged_path = hero_dir / "knight_ranged_attack.aseprite"

    out_path = hero_dir / "knight_spritesheet.png"

    # Export each animation as a horizontal spritesheet, then combine using Lua
    if not all(p.exists() for p in [idle_path, walk_path, melee_path, ranged_path]):
        print("  Skipped - not all source sprites available")
        return

    script = f"""
local sources = {{
    "{lua_path(idle_path)}",
    "{lua_path(walk_path)}",
    "{lua_path(melee_path)}",
    "{lua_path(ranged_path)}",
}}

local total_w = 0
local max_h = 0
local all_rows = {{}}

for _, src_path in ipairs(sources) do
    local s = app.open(src_path)
    if s then
        -- Calculate this sprite's row width
        local row_w = s.width * #s.frames
        total_w = total_w + row_w
        if s.height > max_h then max_h = s.height end
        table.insert(all_rows, {{sprite=s, width=row_w}})
    end
end

local out = Sprite(total_w, max_h)
out.layers[1].name = "Spritesheet"

-- Place pixels from each source sprite side by side
local x_off = 0
for _, entry in ipairs(all_rows) do
    local s = entry.sprite
    for fi = 1, #s.frames do
        local out_cel = out.layers["Spritesheet"]:cel(1)
        if out_cel then
            local out_img = out_cel.image
            for _, layer in ipairs(s.layers) do
                local cel = layer:cel(fi)
                if cel and cel.image then
                    for px = 0, cel.image.width - 1 do
                        for py = 0, cel.image.height - 1 do
                            local c = Color(cel.image:getPixel(px, py))
                            if c.alpha > 0 then
                                local tx = x_off + (fi-1)*s.width + px + cel.position.x
                                local ty = py + cel.position.y
                                if tx >= 0 and tx < total_w
                                and ty >= 0 and ty < max_h then
                                    out_img:putPixel(tx, ty, c)
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    x_off = x_off + s.width * #s.frames
    s:close()
end

out:saveAs("{lua_path(out_path)}")
out:close()
"""
    success, _output = cli.execute_lua_script(script)
    if success and out_path.exists():
        size = out_path.stat().st_size
        print(f"  knight_spritesheet.png ({size:,} bytes)")
    else:
        # Fallback: export idle as spritesheet
        print("  knight_spritesheet.png (fallback from idle)")
        _export_spritesheet_png(idle_path, out_path)


def generate_monster_sprites() -> None:
    """Generate all monster sprite assets."""
    monsters_dir = BASE_DIR / "monsters"
    monsters_dir.mkdir(parents=True, exist_ok=True)

    _generate_goblin(monsters_dir)
    _generate_skeleton(monsters_dir)
    _generate_slime(monsters_dir)
    _generate_dragon_boss(monsters_dir)


def _generate_goblin(monsters_dir: Path) -> None:
    """Generate the goblin sprite (16x16, 4 frames)."""
    path = monsters_dir / "goblin.aseprite"
    lp = lua_path(path)
    print("  Creating goblin.aseprite...")

    body_lua = _pixels_to_lua(_GOBLIN_BODY)
    axe_lua = _pixels_to_lua(_GOBLIN_AXE)

    script = f"""
local spr = Sprite(16, 16)
spr.layers[1].name = "Body"

local axe_layer = spr:newLayer()
axe_layer.name = "Axe"

-- Draw frame 1
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local axe_cel = spr:newCel(axe_layer, 1)
    local aimg = axe_cel.image
    {axe_lua}
end)

-- Add frames 2-4 (idle bob)
for i = 2, 4 do
    spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local src = layer:cel(1)
        if src and src.image then
            local nc = spr:newCel(layer, i)
            nc.image = src.image:clone()
        end
    end
end

-- Breathing bob
app.transaction(function()
    local bob_frames = {{2, 4}}
    local bob_dy = -1
    for _, fi in ipairs(bob_frames) do
        for _, layer in ipairs(spr.layers) do
            local cel = layer:cel(fi)
            if cel then
                cel.position = Point(0, bob_dy)
            end
        end
    end
end)

-- Set durations
for i = 1, 4 do
    spr.frames[i].duration = 0.2
end

-- Tags
local idle_tag = spr:newTag(spr.frames[1], spr.frames[4])
idle_tag.name = "idle"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  goblin.aseprite ({size:,} bytes)")
        png_path = monsters_dir / "goblin.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  goblin.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_skeleton(monsters_dir: Path) -> None:
    """Generate the skeleton sprite (16x24, 4 frames)."""
    path = monsters_dir / "skeleton.aseprite"
    lp = lua_path(path)
    print("  Creating skeleton.aseprite...")

    body_lua = _pixels_to_lua(_SKELETON_BODY)
    shield_lua = _pixels_to_lua(_SKELETON_SHIELD)

    script = f"""
local spr = Sprite(16, 24)
spr.layers[1].name = "Body"

local shield_layer = spr:newLayer()
shield_layer.name = "Shield"

-- Draw frame 1
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local shield_cel = spr:newCel(shield_layer, 1)
    local simg = shield_cel.image
    {shield_lua}
end)

-- Add frames 2-4
for i = 2, 4 do
    spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local src = layer:cel(1)
        if src and src.image then
            local nc = spr:newCel(layer, i)
            nc.image = src.image:clone()
        end
    end
end

-- Idle sway
app.transaction(function()
    local sway_x = {{0, -1, 0, 1}}
    local sway_y = {{0, 0, -1, 0}}
    for i = 2, 4 do
        for _, layer in ipairs(spr.layers) do
            local cel = layer:cel(i)
            if cel then
                cel.position = Point(sway_x[i], sway_y[i])
            end
        end
    end
end)

-- Set durations
for i = 1, 4 do
    spr.frames[i].duration = 0.2
end

local t = spr:newTag(spr.frames[1], spr.frames[4])
t.name = "idle"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  skeleton.aseprite ({size:,} bytes)")
        png_path = monsters_dir / "skeleton.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  skeleton.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_slime(monsters_dir: Path) -> None:
    """Generate the slime sprite (16x12, 4 frames)."""
    path = monsters_dir / "slime.aseprite"
    lp = lua_path(path)
    print("  Creating slime.aseprite...")

    body_lua = _pixels_to_lua(_SLIME_BODY_FRAME1)

    script = f"""
local spr = Sprite(16, 12)
spr.layers[1].name = "Body"

-- Frame 1: normal shape
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}
end)

-- Frame 2: squish (wider, shorter) — offset cel horizontally and draw wider shape
spr:newEmptyFrame()
app.transaction(function()
    local cel2 = spr:newCel(spr.layers[1], 2)
    local img2 = cel2.image
    -- Wider slime (squished down)
    for x = 3, 12 do
        img2:putPixel(x, 5, Color(68, 68, 255, 255))
    end
    for x = 2, 13 do
        img2:putPixel(x, 6, Color(68, 68, 255, 255))
    end
    for x = 2, 13 do
        img2:putPixel(x, 7, Color(68, 68, 255, 255))
        img2:putPixel(x, 8, Color(68, 68, 255, 255))
        img2:putPixel(x, 9, Color(34, 34, 170, 255))
    end
    for x = 3, 12 do
        img2:putPixel(x, 10, Color(34, 34, 170, 255))
    end
    -- Eyes
    img2:putPixel(6, 6, Color(255, 255, 255, 255))
    img2:putPixel(9, 6, Color(255, 255, 255, 255))
    img2:putPixel(7, 7, Color(0, 0, 0, 255))
    img2:putPixel(8, 7, Color(0, 0, 0, 255))
end)

-- Frame 3: tall (stretched up)
spr:newEmptyFrame()
app.transaction(function()
    local cel3 = spr:newCel(spr.layers[1], 3)
    local img3 = cel3.image
    -- Taller slime
    for x = 5, 10 do
        img3:putPixel(x, 1, Color(68, 68, 255, 255))
    end
    for x = 5, 10 do
        img3:putPixel(x, 2, Color(68, 68, 255, 255))
    end
    for x = 4, 11 do
        img3:putPixel(x, 3, Color(68, 68, 255, 255))
    end
    for x = 4, 11 do
        img3:putPixel(x, 4, Color(68, 68, 255, 255))
        img3:putPixel(x, 5, Color(68, 68, 255, 255))
        img3:putPixel(x, 6, Color(68, 68, 255, 255))
        img3:putPixel(x, 7, Color(68, 68, 255, 255))
    end
    for x = 4, 11 do
        img3:putPixel(x, 8, Color(34, 34, 170, 255))
        img3:putPixel(x, 9, Color(34, 34, 170, 255))
    end
    for x = 5, 10 do
        img3:putPixel(x, 10, Color(34, 34, 170, 255))
    end
    -- Eyes
    img3:putPixel(6, 3, Color(255, 255, 255, 255))
    img3:putPixel(9, 3, Color(255, 255, 255, 255))
    img3:putPixel(7, 4, Color(0, 0, 0, 255))
    img3:putPixel(8, 4, Color(0, 0, 0, 255))
end)

-- Frame 4: back to normal (copy frame 1)
spr:newEmptyFrame()
app.transaction(function()
    local cel4 = spr:newCel(spr.layers[1], 4)
    local src = spr.layers[1]:cel(1)
    if src and src.image then
        cel4.image = src.image:clone()
    end
end)

-- Set durations
for i = 1, 4 do
    spr.frames[i].duration = 0.15
end

local t = spr:newTag(spr.frames[1], spr.frames[4])
t.name = "idle"

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  slime.aseprite ({size:,} bytes)")
        png_path = monsters_dir / "slime.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  slime.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_dragon_boss(monsters_dir: Path) -> None:
    """Generate the dragon boss sprite (64x48, 6 frames)."""
    path = monsters_dir / "dragon_boss.aseprite"
    lp = lua_path(path)
    print("  Creating dragon_boss.aseprite...")

    body_lua = _pixels_to_lua(_DRAGON_BODY)
    wings_lua = _pixels_to_lua(_DRAGON_WINGS)
    fire_lua = _pixels_to_lua(_DRAGON_FIRE)

    script = f"""
local spr = Sprite(64, 48)
spr.layers[1].name = "Body"

local wings_layer = spr:newLayer()
wings_layer.name = "Wings"

local eyes_layer = spr:newLayer()
eyes_layer.name = "Eyes"

local fire_layer = spr:newLayer()
fire_layer.name = "Fire"

-- Draw frame 1 (idle, no fire)
app.transaction(function()
    local body_cel = spr.cels[1]
    local img = body_cel.image
    {body_lua}

    local wings_cel = spr:newCel(wings_layer, 1)
    local wimg = wings_cel.image
    {wings_lua}

    -- Eyes
    local eyes_cel = spr:newCel(eyes_layer, 1)
    local eimg = eyes_cel.image
    eimg:putPixel(21, 5, Color(255, 255, 0, 255))
    eimg:putPixel(28, 5, Color(255, 255, 0, 255))
    eimg:putPixel(21, 4, Color(0, 0, 0, 255))
    eimg:putPixel(28, 4, Color(0, 0, 0, 255))
end)

-- Add frames 2-6
for i = 2, 6 do
    spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local src = layer:cel(1)
        if src and src.image then
            local nc = spr:newCel(layer, i)
            nc.image = src.image:clone()
        end
    end
end

-- Idle breathing animation on frames 2-4
app.transaction(function()
    -- Slight body bob on frames 2 and 4
    for _, frame_idx in ipairs({{2, 4}}) do
        for _, layer in ipairs({{spr.layers["Body"], spr.layers["Eyes"]}}) do
            if layer then
                local cel = layer:cel(frame_idx)
                if cel then
                    cel.position = Point(0, -1)
                end
            end
        end
    end
    -- Wings flap on frames 2-4
    local wing_cel2 = wings_layer:cel(2)
    if wing_cel2 then wing_cel2.position = Point(0, -2) end
    local wing_cel4 = wings_layer:cel(4)
    if wing_cel4 then wing_cel4.position = Point(0, -1) end
end)

-- Fire breath on frames 5-6
app.transaction(function()
    for fi = 5, 6 do
        local fire_cel = fire_layer:cel(fi)
        if fire_cel then
            local fimg = fire_cel.image
            {fire_lua}
        end
    end
end)

-- Set durations
for i = 1, 6 do
    spr.frames[i].duration = 0.12
end

-- Tags
local idle_tag = spr:newTag(spr.frames[1], spr.frames[4])
idle_tag.name = "idle"
local fire_tag = spr:newTag(spr.frames[5], spr.frames[6])
fire_tag.name = "fire_breath"
fire_tag.fromFrame = 5
fire_tag.toFrame = 6

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  dragon_boss.aseprite ({size:,} bytes)")
        png_path = monsters_dir / "dragon_boss.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  dragon_boss.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def generate_environment_sprites() -> None:
    """Generate environment tile sprites."""
    env_dir = BASE_DIR / "environment"
    env_dir.mkdir(parents=True, exist_ok=True)

    _generate_dungeon_tiles(env_dir)
    _generate_castle_tower(env_dir)


def _generate_dungeon_tiles(env_dir: Path) -> None:
    """Generate dungeon tiles sprite (128x32, 1 frame)."""
    path = env_dir / "dungeon_tiles.aseprite"
    lp = lua_path(path)
    print("  Creating dungeon_tiles.aseprite...")

    script = f"""
local spr = Sprite(128, 32)
spr.layers[1].name = "Walls"

local floor_layer = spr:newLayer()
floor_layer.name = "Floor"

local door_layer = spr:newLayer()
door_layer.name = "Door"

local torch_layer = spr:newLayer()
torch_layer.name = "Torch"

app.transaction(function()
    -- Stone wall blocks with mortar lines
    local wall_cel = spr.cels[1]
    local wimg = wall_cel.image
    for bx = 0, 112, 16 do
        for by = 0, 8, 8 do
            -- Stone block fill (gray)
            for x = bx + 1, bx + 14 do
                for y = by + 1, by + 6 do
                    wimg:putPixel(x, y, Color(136, 136, 136, 255))
                end
            end
            -- Mortar lines (darker)
            for x = bx, bx + 15 do
                wimg:putPixel(x, by, Color(68, 68, 68, 255))
            end
            for y = by, by + 7 do
                wimg:putPixel(bx, y, Color(68, 68, 68, 255))
            end
        end
    end

    -- Floor tiles
    local floor_cel = spr:newCel(floor_layer, 1)
    local fimg = floor_cel.image
    for bx = 0, 112, 16 do
        for x = bx + 1, bx + 14 do
            for y = 17, 31 do
                local shade = 51
                if (bx / 16 + math.floor((y - 17) / 4)) % 2 == 1 then
                    shade = 40
                end
                fimg:putPixel(x, y, Color(shade, shade, shade, 255))
            end
        end
        -- Tile border
        for y = 16, 31 do
            fimg:putPixel(bx, y, Color(30, 30, 30, 255))
        end
    end

    -- Wooden door (at x=48-62, y=0-16)
    local door_cel = spr:newCel(door_layer, 1)
    local dimg = door_cel.image
    for y = 0, 15 do
        dimg:putPixel(47, y, Color(0, 0, 0, 255))
        dimg:putPixel(63, y, Color(0, 0, 0, 255))
    end
    for x = 47, 63 do
        dimg:putPixel(x, 0, Color(0, 0, 0, 255))
    end
    for x = 48, 62 do
        for y = 1, 15 do
            dimg:putPixel(x, y, Color(139, 69, 19, 255))
        end
    end
    dimg:putPixel(58, 8, Color(204, 204, 0, 255))
    dimg:putPixel(59, 8, Color(204, 204, 0, 255))

    -- Torches
    local torch_cel = spr:newCel(torch_layer, 1)
    local timg = torch_cel.image
    -- Left torch
    timg:putPixel(10, 2, Color(139, 69, 19, 255))
    timg:putPixel(10, 3, Color(139, 69, 19, 255))
    timg:putPixel(10, 4, Color(139, 69, 19, 255))
    timg:putPixel(9, 1, Color(255, 170, 0, 255))
    timg:putPixel(10, 1, Color(255, 102, 0, 255))
    timg:putPixel(11, 1, Color(255, 170, 0, 255))
    timg:putPixel(10, 0, Color(255, 255, 0, 255))
    -- Right torch
    timg:putPixel(100, 2, Color(139, 69, 19, 255))
    timg:putPixel(100, 3, Color(139, 69, 19, 255))
    timg:putPixel(100, 4, Color(139, 69, 19, 255))
    timg:putPixel(99, 1, Color(255, 170, 0, 255))
    timg:putPixel(100, 1, Color(255, 102, 0, 255))
    timg:putPixel(101, 1, Color(255, 170, 0, 255))
    timg:putPixel(100, 0, Color(255, 255, 0, 255))
end)

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  dungeon_tiles.aseprite ({size:,} bytes)")
        png_path = env_dir / "dungeon_tiles.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  dungeon_tiles.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_castle_tower(env_dir: Path) -> None:
    """Generate the castle tower sprite (32x48, 1 frame)."""
    path = env_dir / "castle_tower.aseprite"
    lp = lua_path(path)
    print("  Creating castle_tower.aseprite...")

    script = f"""
local spr = Sprite(32, 48)
spr.layers[1].name = "Walls"

local roof_layer = spr:newLayer()
roof_layer.name = "Roof"

local window_layer = spr:newLayer()
window_layer.name = "Window"

local flag_layer = spr:newLayer()
flag_layer.name = "Flag"

app.transaction(function()
    -- Tower walls (gray stone)
    local wall_cel = spr.cels[1]
    local wimg = wall_cel.image
    -- Main tower body
    for x = 8, 23 do
        for y = 14, 47 do
            wimg:putPixel(x, y, Color(136, 136, 136, 255))
        end
    end
    -- Stone block details
    for by = 14, 46, 6 do
        for x = 8, 23 do
            wimg:putPixel(x, by, Color(100, 100, 100, 255))
        end
    end
    for bx = 8, 23, 8 do
        for y = 14, 47 do
            wimg:putPixel(bx, y, Color(100, 100, 100, 255))
        end
    end
    -- Battlements at top
    for x = 6, 25, 4 do
        for y = 10, 13 do
            wimg:putPixel(x, y, Color(136, 136, 136, 255))
            wimg:putPixel(x+1, y, Color(136, 136, 136, 255))
            wimg:putPixel(x+2, y, Color(136, 136, 136, 255))
        end
    end
    -- Door
    for x = 13, 18 do
        for y = 40, 47 do
            wimg:putPixel(x, y, Color(0, 0, 0, 255))
        end
    end
    for x = 14, 17 do
        for y = 41, 47 do
            wimg:putPixel(x, y, Color(139, 69, 19, 255))
        end
    end
    -- Door arch
    wimg:putPixel(13, 40, Color(0, 0, 0, 255))
    wimg:putPixel(18, 40, Color(0, 0, 0, 255))
    wimg:putPixel(14, 39, Color(0, 0, 0, 255))
    wimg:putPixel(17, 39, Color(0, 0, 0, 255))
    wimg:putPixel(15, 38, Color(0, 0, 0, 255))
    wimg:putPixel(16, 38, Color(0, 0, 0, 255))

    -- Roof (red pointed triangle)
    local roof_cel = spr:newCel(roof_layer, 1)
    local rimg = roof_cel.image
    -- Triangle from top center
    for row = 0, 6 do
        local half_w = row + 2
        for x = 16 - half_w, 16 + half_w do
            if x >= 0 and x < 32 then
                rimg:putPixel(x, 7 - row, Color(180, 30, 30, 255))
            end
        end
    end
    -- Roof highlight
    for row = 0, 4 do
        rimg:putPixel(16 - row, 7 - row, Color(200, 60, 60, 255))
    end

    -- Window (blue)
    local win_cel = spr:newCel(window_layer, 1)
    local wimg2 = win_cel.image
    for x = 14, 17 do
        for y = 24, 28 do
            wimg2:putPixel(x, y, Color(100, 150, 255, 255))
        end
    end
    -- Window frame
    for x = 13, 18 do
        wimg2:putPixel(x, 23, Color(80, 80, 80, 255))
        wimg2:putPixel(x, 29, Color(80, 80, 80, 255))
    end
    for y = 23, 29 do
        wimg2:putPixel(13, y, Color(80, 80, 80, 255))
        wimg2:putPixel(18, y, Color(80, 80, 80, 255))
    end
    -- Cross bar
    for y = 23, 29 do
        wimg2:putPixel(15, y, Color(80, 80, 80, 255))
        wimg2:putPixel(16, y, Color(80, 80, 80, 255))
    end
    for x = 13, 18 do
        wimg2:putPixel(x, 26, Color(80, 80, 80, 255))
        wimg2:putPixel(x, 27, Color(80, 80, 80, 255))
    end

    -- Flag at top
    local flag_cel = spr:newCel(flag_layer, 1)
    local fimg = flag_cel.image
    -- Pole
    fimg:putPixel(16, 0, Color(139, 69, 19, 255))
    fimg:putPixel(16, 1, Color(139, 69, 19, 255))
    fimg:putPixel(16, 2, Color(139, 69, 19, 255))
    fimg:putPixel(16, 3, Color(139, 69, 19, 255))
    fimg:putPixel(16, 4, Color(139, 69, 19, 255))
    -- Flag cloth
    fimg:putPixel(17, 0, Color(204, 0, 0, 255))
    fimg:putPixel(18, 0, Color(204, 0, 0, 255))
    fimg:putPixel(19, 0, Color(204, 0, 0, 255))
    fimg:putPixel(20, 0, Color(204, 0, 0, 255))
    fimg:putPixel(17, 1, Color(204, 0, 0, 255))
    fimg:putPixel(18, 1, Color(204, 0, 0, 255))
    fimg:putPixel(19, 1, Color(204, 0, 0, 255))
    fimg:putPixel(17, 2, Color(204, 0, 0, 255))
    fimg:putPixel(18, 2, Color(204, 0, 0, 255))
end)

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  castle_tower.aseprite ({size:,} bytes)")
        png_path = env_dir / "castle_tower.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  castle_tower.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def generate_effects_sprites() -> None:
    """Generate battle effect sprite animations."""
    fx_dir = BASE_DIR / "effects"
    fx_dir.mkdir(parents=True, exist_ok=True)

    _generate_melee_slash(fx_dir)
    _generate_magic_bolt(fx_dir)
    _generate_fireball_spell(fx_dir)


def _generate_melee_slash(fx_dir: Path) -> None:
    """Generate melee slash effect (32x32, 4 frames)."""
    path = fx_dir / "melee_slash.aseprite"
    lp = lua_path(path)
    print("  Creating melee_slash.aseprite...")

    script = f"""
local spr = Sprite(32, 32)
spr.layers[1].name = "Slash"

-- Frame 1: slash starts (small arc)
app.transaction(function()
    local cel1 = spr.cels[1]
    local img = cel1.image
    img:putPixel(20, 12, Color(255, 255, 255, 255))
    img:putPixel(22, 10, Color(255, 255, 255, 255))
    img:putPixel(24, 8, Color(255, 255, 255, 255))
end)

-- Frame 2: slash extends
spr:newEmptyFrame()
app.transaction(function()
    local cel2 = spr:newCel(spr.layers[1], 2)
    local img = cel2.image
    -- Larger arc
    img:putPixel(18, 14, Color(255, 255, 255, 255))
    img:putPixel(20, 12, Color(255, 255, 255, 255))
    img:putPixel(22, 10, Color(255, 255, 255, 255))
    img:putPixel(24, 8, Color(255, 255, 255, 255))
    img:putPixel(26, 6, Color(255, 255, 255, 255))
    -- Add glow
    img:putPixel(19, 13, Color(200, 200, 255, 200))
    img:putPixel(21, 11, Color(200, 200, 255, 200))
    img:putPixel(23, 9, Color(200, 200, 255, 200))
    img:putPixel(25, 7, Color(200, 200, 255, 200))
end)

-- Frame 3: full slash arc
spr:newEmptyFrame()
app.transaction(function()
    local cel3 = spr:newCel(spr.layers[1], 3)
    local img = cel3.image
    -- Full arc
    img:putPixel(16, 16, Color(255, 255, 255, 255))
    img:putPixel(18, 14, Color(255, 255, 255, 255))
    img:putPixel(20, 12, Color(255, 255, 255, 255))
    img:putPixel(22, 10, Color(255, 255, 255, 255))
    img:putPixel(24, 8, Color(255, 255, 255, 255))
    img:putPixel(26, 6, Color(255, 255, 255, 255))
    img:putPixel(28, 5, Color(255, 255, 255, 255))
    img:putPixel(30, 5, Color(255, 255, 255, 255))
    -- Glow trail
    img:putPixel(17, 15, Color(200, 200, 255, 150))
    img:putPixel(19, 13, Color(200, 200, 255, 150))
    img:putPixel(21, 11, Color(200, 200, 255, 150))
    img:putPixel(23, 9, Color(200, 200, 255, 150))
    img:putPixel(25, 7, Color(200, 200, 255, 150))
    img:putPixel(27, 6, Color(200, 200, 255, 150))
    img:putPixel(29, 5, Color(200, 200, 255, 150))
end)

-- Frame 4: slash fading
spr:newEmptyFrame()
app.transaction(function()
    local cel4 = spr:newCel(spr.layers[1], 4)
    local img = cel4.image
    -- Fading arc
    img:putPixel(18, 14, Color(255, 255, 255, 100))
    img:putPixel(20, 12, Color(255, 255, 255, 100))
    img:putPixel(22, 10, Color(255, 255, 255, 100))
    img:putPixel(24, 8, Color(255, 255, 255, 100))
    img:putPixel(26, 6, Color(255, 255, 255, 100))
    img:putPixel(28, 5, Color(255, 255, 255, 100))
end)

-- Set durations (fast)
for i = 1, 4 do
    spr.frames[i].duration = 0.05
end

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  melee_slash.aseprite ({size:,} bytes)")
        png_path = fx_dir / "melee_slash.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  melee_slash.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_magic_bolt(fx_dir: Path) -> None:
    """Generate magic bolt effect (16x8, 4 frames)."""
    path = fx_dir / "magic_bolt.aseprite"
    lp = lua_path(path)
    print("  Creating magic_bolt.aseprite...")

    script = f"""
local spr = Sprite(16, 8)
spr.layers[1].name = "Bolt"

-- Frame 1: bolt at left
app.transaction(function()
    local cel1 = spr.cels[1]
    local img = cel1.image
    -- Main bolt
    img:putPixel(2, 4, Color(0, 200, 255, 255))
    img:putPixel(3, 4, Color(0, 255, 255, 255))
    img:putPixel(4, 4, Color(100, 200, 255, 255))
    -- Glow
    img:putPixel(2, 3, Color(0, 150, 255, 100))
    img:putPixel(3, 3, Color(0, 200, 255, 150))
    img:putPixel(2, 5, Color(0, 150, 255, 100))
    img:putPixel(3, 5, Color(0, 200, 255, 150))
end)

-- Frame 2: bolt moves right
spr:newEmptyFrame()
app.transaction(function()
    local cel2 = spr:newCel(spr.layers[1], 2)
    local img = cel2.image
    img:putPixel(5, 4, Color(0, 200, 255, 255))
    img:putPixel(6, 4, Color(0, 255, 255, 255))
    img:putPixel(7, 4, Color(100, 200, 255, 255))
    -- Glow
    img:putPixel(5, 3, Color(0, 150, 255, 100))
    img:putPixel(6, 3, Color(0, 200, 255, 150))
    img:putPixel(5, 5, Color(0, 150, 255, 100))
    img:putPixel(6, 5, Color(0, 200, 255, 150))
    -- Trail
    img:putPixel(3, 4, Color(0, 100, 200, 80))
    img:putPixel(4, 4, Color(0, 150, 255, 120))
end)

-- Frame 3: bolt moves more right
spr:newEmptyFrame()
app.transaction(function()
    local cel3 = spr:newCel(spr.layers[1], 3)
    local img = cel3.image
    img:putPixel(9, 4, Color(0, 200, 255, 255))
    img:putPixel(10, 4, Color(0, 255, 255, 255))
    img:putPixel(11, 4, Color(100, 200, 255, 255))
    -- Glow
    img:putPixel(9, 3, Color(0, 150, 255, 100))
    img:putPixel(10, 3, Color(0, 200, 255, 150))
    img:putPixel(9, 5, Color(0, 150, 255, 100))
    img:putPixel(10, 5, Color(0, 200, 255, 150))
    -- Trail
    img:putPixel(7, 4, Color(0, 100, 200, 60))
    img:putPixel(8, 4, Color(0, 150, 255, 90))
end)

-- Frame 4: bolt at far right
spr:newEmptyFrame()
app.transaction(function()
    local cel4 = spr:newCel(spr.layers[1], 4)
    local img = cel4.image
    img:putPixel(12, 4, Color(0, 200, 255, 255))
    img:putPixel(13, 4, Color(0, 255, 255, 255))
    img:putPixel(14, 4, Color(100, 200, 255, 255))
    -- Glow
    img:putPixel(12, 3, Color(0, 150, 255, 100))
    img:putPixel(13, 3, Color(0, 200, 255, 150))
    img:putPixel(12, 5, Color(0, 150, 255, 100))
    img:putPixel(13, 5, Color(0, 200, 255, 150))
    -- Trail
    img:putPixel(10, 4, Color(0, 100, 200, 40))
    img:putPixel(11, 4, Color(0, 150, 255, 70))
end)

-- Set durations
for i = 1, 4 do
    spr.frames[i].duration = 0.08
end

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  magic_bolt.aseprite ({size:,} bytes)")
        png_path = fx_dir / "magic_bolt.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  magic_bolt.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def _generate_fireball_spell(fx_dir: Path) -> None:
    """Generate fireball spell effect (16x16, 6 frames). Also export as .gif."""
    path = fx_dir / "fireball_spell.aseprite"
    lp = lua_path(path)
    print("  Creating fireball_spell.aseprite...")

    script = f"""
local spr = Sprite(16, 16)
spr.layers[1].name = "Fire"

local glow_layer = spr:newLayer()
glow_layer.name = "Glow"

-- Frame 1: small fireball
app.transaction(function()
    local cel1 = spr.cels[1]
    local img = cel1.image
    -- Core
    img:putPixel(7, 7, Color(255, 200, 0, 255))
    img:putPixel(8, 7, Color(255, 200, 0, 255))
    img:putPixel(7, 8, Color(255, 200, 0, 255))
    img:putPixel(8, 8, Color(255, 200, 0, 255))
    -- Fire edge
    img:putPixel(6, 7, Color(255, 102, 0, 255))
    img:putPixel(9, 7, Color(255, 102, 0, 255))
    img:putPixel(7, 6, Color(255, 102, 0, 255))
    img:putPixel(8, 6, Color(255, 102, 0, 255))
    img:putPixel(6, 8, Color(255, 102, 0, 255))
    img:putPixel(9, 8, Color(255, 102, 0, 255))
    img:putPixel(7, 9, Color(255, 51, 0, 255))
    img:putPixel(8, 9, Color(255, 51, 0, 255))

    -- Glow
    local gcel1 = spr:newCel(glow_layer, 1)
    local gimg = gcel1.image
    gimg:putPixel(5, 6, Color(255, 200, 0, 60))
    gimg:putPixel(10, 6, Color(255, 200, 0, 60))
    gimg:putPixel(5, 9, Color(255, 200, 0, 60))
    gimg:putPixel(10, 9, Color(255, 200, 0, 60))
    gimg:putPixel(6, 5, Color(255, 200, 0, 40))
    gimg:putPixel(9, 5, Color(255, 200, 0, 40))
    gimg:putPixel(6, 10, Color(255, 200, 0, 40))
    gimg:putPixel(9, 10, Color(255, 200, 0, 40))
end)

-- Frame 2: growing
spr:newEmptyFrame()
app.transaction(function()
    local cel2 = spr:newCel(spr.layers[1], 2)
    local img = cel2.image
    -- Larger core
    img:putPixel(7, 6, Color(255, 200, 0, 255))
    img:putPixel(8, 6, Color(255, 200, 0, 255))
    img:putPixel(6, 7, Color(255, 200, 0, 255))
    img:putPixel(7, 7, Color(255, 255, 100, 255))
    img:putPixel(8, 7, Color(255, 255, 100, 255))
    img:putPixel(9, 7, Color(255, 200, 0, 255))
    img:putPixel(6, 8, Color(255, 200, 0, 255))
    img:putPixel(7, 8, Color(255, 255, 100, 255))
    img:putPixel(8, 8, Color(255, 255, 100, 255))
    img:putPixel(9, 8, Color(255, 200, 0, 255))
    img:putPixel(7, 9, Color(255, 200, 0, 255))
    img:putPixel(8, 9, Color(255, 200, 0, 255))
    -- Fire edge
    img:putPixel(5, 7, Color(255, 102, 0, 255))
    img:putPixel(10, 7, Color(255, 102, 0, 255))
    img:putPixel(5, 8, Color(255, 102, 0, 255))
    img:putPixel(10, 8, Color(255, 102, 0, 255))
    img:putPixel(7, 5, Color(255, 102, 0, 255))
    img:putPixel(8, 5, Color(255, 102, 0, 255))
    img:putPixel(7, 10, Color(255, 51, 0, 255))
    img:putPixel(8, 10, Color(255, 51, 0, 255))

    local gcel2 = spr:newCel(glow_layer, 2)
    local gimg = gcel2.image
    for x = 4, 11 do
        for y = 4, 11 do
            gimg:putPixel(x, y, Color(255, 200, 0, 30))
        end
    end
    gimg:putPixel(7, 6, Color(255, 200, 0, 50))
    gimg:putPixel(8, 6, Color(255, 200, 0, 50))
    gimg:putPixel(7, 9, Color(255, 200, 0, 50))
    gimg:putPixel(8, 9, Color(255, 200, 0, 50))
end)

-- Frame 3: peak fireball
spr:newEmptyFrame()
app.transaction(function()
    local cel3 = spr:newCel(spr.layers[1], 3)
    local img = cel3.image
    -- Biggest core
    for x = 6, 9 do
        for y = 6, 9 do
            img:putPixel(x, y, Color(255, 255, 100, 255))
        end
    end
    -- Fire ring
    img:putPixel(5, 6, Color(255, 102, 0, 255))
    img:putPixel(10, 6, Color(255, 102, 0, 255))
    img:putPixel(5, 7, Color(255, 102, 0, 255))
    img:putPixel(10, 7, Color(255, 102, 0, 255))
    img:putPixel(5, 8, Color(255, 102, 0, 255))
    img:putPixel(10, 8, Color(255, 102, 0, 255))
    img:putPixel(5, 9, Color(255, 102, 0, 255))
    img:putPixel(10, 9, Color(255, 102, 0, 255))
    img:putPixel(6, 5, Color(255, 102, 0, 255))
    img:putPixel(7, 5, Color(255, 102, 0, 255))
    img:putPixel(8, 5, Color(255, 102, 0, 255))
    img:putPixel(9, 5, Color(255, 102, 0, 255))
    img:putPixel(6, 10, Color(255, 51, 0, 255))
    img:putPixel(7, 10, Color(255, 51, 0, 255))
    img:putPixel(8, 10, Color(255, 51, 0, 255))
    img:putPixel(9, 10, Color(255, 51, 0, 255))

    local gcel3 = spr:newCel(glow_layer, 3)
    local gimg = gcel3.image
    for x = 3, 12 do
        for y = 3, 12 do
            gimg:putPixel(x, y, Color(255, 200, 0, 25))
        end
    end
end)

-- Frame 4: starting to shrink
spr:newEmptyFrame()
app.transaction(function()
    local cel4 = spr:newCel(spr.layers[1], 4)
    local img = cel4.image
    -- Similar to frame 2 but shifted left (moving)
    img:putPixel(6, 6, Color(255, 200, 0, 255))
    img:putPixel(7, 6, Color(255, 200, 0, 255))
    img:putPixel(5, 7, Color(255, 200, 0, 255))
    img:putPixel(6, 7, Color(255, 255, 100, 255))
    img:putPixel(7, 7, Color(255, 255, 100, 255))
    img:putPixel(8, 7, Color(255, 200, 0, 255))
    img:putPixel(5, 8, Color(255, 200, 0, 255))
    img:putPixel(6, 8, Color(255, 255, 100, 255))
    img:putPixel(7, 8, Color(255, 255, 100, 255))
    img:putPixel(8, 8, Color(255, 200, 0, 255))
    img:putPixel(6, 9, Color(255, 200, 0, 255))
    img:putPixel(7, 9, Color(255, 200, 0, 255))
    img:putPixel(4, 7, Color(255, 102, 0, 255))
    img:putPixel(9, 7, Color(255, 102, 0, 255))
    img:putPixel(4, 8, Color(255, 102, 0, 255))
    img:putPixel(9, 8, Color(255, 102, 0, 255))
    img:putPixel(6, 5, Color(255, 102, 0, 255))
    img:putPixel(7, 5, Color(255, 102, 0, 255))
    img:putPixel(6, 10, Color(255, 51, 0, 255))
    img:putPixel(7, 10, Color(255, 51, 0, 255))

    local gcel4 = spr:newCel(glow_layer, 4)
    local gimg = gcel4.image
    for x = 3, 10 do
        for y = 4, 11 do
            gimg:putPixel(x, y, Color(255, 200, 0, 20))
        end
    end
end)

-- Frame 5: smaller, moving left
spr:newEmptyFrame()
app.transaction(function()
    local cel5 = spr:newCel(spr.layers[1], 5)
    local img = cel5.image
    img:putPixel(5, 7, Color(255, 200, 0, 255))
    img:putPixel(6, 7, Color(255, 200, 0, 255))
    img:putPixel(5, 8, Color(255, 200, 0, 255))
    img:putPixel(6, 8, Color(255, 200, 0, 255))
    img:putPixel(4, 7, Color(255, 102, 0, 255))
    img:putPixel(7, 7, Color(255, 102, 0, 255))
    img:putPixel(4, 8, Color(255, 102, 0, 255))
    img:putPixel(7, 8, Color(255, 102, 0, 255))
    img:putPixel(5, 6, Color(255, 102, 0, 255))
    img:putPixel(6, 6, Color(255, 102, 0, 255))
    img:putPixel(5, 9, Color(255, 51, 0, 255))
    img:putPixel(6, 9, Color(255, 51, 0, 255))
    -- Smoke trail
    img:putPixel(9, 6, Color(128, 128, 128, 100))
    img:putPixel(10, 5, Color(128, 128, 128, 80))

    local gcel5 = spr:newCel(glow_layer, 5)
    local gimg = gcel5.image
    gimg:putPixel(3, 6, Color(255, 200, 0, 30))
    gimg:putPixel(8, 6, Color(255, 200, 0, 30))
    gimg:putPixel(3, 9, Color(255, 200, 0, 30))
    gimg:putPixel(8, 9, Color(255, 200, 0, 30))
end)

-- Frame 6: dissipating
spr:newEmptyFrame()
app.transaction(function()
    local cel6 = spr:newCel(spr.layers[1], 6)
    local img = cel6.image
    -- Last spark
    img:putPixel(4, 7, Color(255, 102, 0, 200))
    img:putPixel(5, 7, Color(255, 200, 0, 200))
    img:putPixel(4, 8, Color(255, 102, 0, 200))
    img:putPixel(5, 8, Color(255, 200, 0, 200))
    -- Smoke
    img:putPixel(8, 5, Color(128, 128, 128, 80))
    img:putPixel(9, 4, Color(128, 128, 128, 60))
    img:putPixel(7, 6, Color(128, 128, 128, 60))

    local gcel6 = spr:newCel(glow_layer, 6)
    local gimg = gcel6.image
    gimg:putPixel(3, 7, Color(255, 200, 0, 20))
    gimg:putPixel(6, 7, Color(255, 200, 0, 20))
end)

-- Set durations
for i = 1, 6 do
    spr.frames[i].duration = 0.06
end

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  fireball_spell.aseprite ({size:,} bytes)")
        png_path = fx_dir / "fireball_spell.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  fireball_spell.png ({png_path.stat().st_size:,} bytes)")
        # Export as GIF for animated preview
        gif_path = fx_dir / "fireball_spell.gif"
        _export_gif(path, gif_path)
        if gif_path.exists():
            print(f"  fireball_spell.gif ({gif_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


def generate_cutscene_sprites() -> None:
    """Generate cutscene sprite assets."""
    cs_dir = BASE_DIR / "cutscene"
    cs_dir.mkdir(parents=True, exist_ok=True)

    _generate_princess_rescue(cs_dir)


def _generate_princess_rescue(cs_dir: Path) -> None:
    """Generate princess rescue cutscene (64x64, 1 frame)."""
    path = cs_dir / "princess_rescue.aseprite"
    lp = lua_path(path)
    print("  Creating princess_rescue.aseprite...")

    script = f"""
local spr = Sprite(64, 64)
spr.layers[1].name = "Background"

local castle_layer = spr:newLayer()
castle_layer.name = "Castle"

local princess_layer = spr:newLayer()
princess_layer.name = "Princess"

local knight_layer = spr:newLayer()
knight_layer.name = "Knight"

app.transaction(function()
    -- Background: light blue sky, green ground
    local bg_cel = spr.cels[1]
    local bg = bg_cel.image
    -- Sky
    for x = 0, 63 do
        for y = 0, 39 do
            bg:putPixel(x, y, Color(135, 206, 235, 255))
        end
    end
    -- Sun
    for x = 50, 57 do
        for y = 4, 11 do
            bg:putPixel(x, y, Color(255, 255, 100, 255))
        end
    end
    -- Ground
    for x = 0, 63 do
        for y = 40, 63 do
            bg:putPixel(x, y, Color(34, 139, 34, 255))
        end
    end
    -- Grass line
    for x = 0, 63 do
        bg:putPixel(x, 40, Color(0, 100, 0, 255))
        bg:putPixel(x, 41, Color(50, 160, 50, 255))
    end
    -- Clouds
    for x = 10, 18 do
        bg:putPixel(x, 8, Color(255, 255, 255, 255))
        bg:putPixel(x, 9, Color(255, 255, 255, 255))
        bg:putPixel(x-1, 9, Color(255, 255, 255, 255))
        bg:putPixel(x+1, 7, Color(255, 255, 255, 255))
    end

    -- Castle tower (background)
    local castle_cel = spr:newCel(castle_layer, 1)
    local cs = castle_cel.image
    -- Tower body
    for x = 24, 40 do
        for y = 12, 40 do
            cs:putPixel(x, y, Color(136, 136, 136, 255))
        end
    end
    -- Tower top (battlements)
    for x = 22, 42 do
        cs:putPixel(x, 12, Color(136, 136, 136, 255))
        cs:putPixel(x, 11, Color(136, 136, 136, 255))
    end
    for x = 22, 26, 4 do
        for y = 8, 10 do
            cs:putPixel(x, y, Color(136, 136, 136, 255))
            cs:putPixel(x+1, y, Color(136, 136, 136, 255))
            cs:putPixel(x+2, y, Color(136, 136, 136, 255))
        end
    end
    for x = 34, 42, 4 do
        for y = 8, 10 do
            cs:putPixel(x, y, Color(136, 136, 136, 255))
            cs:putPixel(x+1, y, Color(136, 136, 136, 255))
            cs:putPixel(x+2, y, Color(136, 136, 136, 255))
        end
    end
    -- Roof (red triangle)
    for row = 0, 4 do
        for x = 32 - row, 32 + row do
            cs:putPixel(x, 7 - row, Color(180, 30, 30, 255))
        end
    end
    -- Windows
    for x = 28, 31 do
        for y = 18, 22 do
            cs:putPixel(x, y, Color(100, 150, 255, 255))
        end
    end
    for x = 28, 31 do
        for y = 26, 30 do
            cs:putPixel(x, y, Color(100, 150, 255, 255))
        end
    end
    -- Door
    for x = 30, 34 do
        for y = 35, 40 do
            cs:putPixel(x, y, Color(139, 69, 19, 255))
        end
    end
    -- Flag
    cs:putPixel(32, 2, Color(139, 69, 19, 255))
    cs:putPixel(32, 3, Color(139, 69, 19, 255))
    cs:putPixel(33, 2, Color(204, 0, 0, 255))
    cs:putPixel(34, 2, Color(204, 0, 0, 255))
    cs:putPixel(35, 2, Color(204, 0, 0, 255))
    cs:putPixel(33, 3, Color(204, 0, 0, 255))
    cs:putPixel(34, 3, Color(204, 0, 0, 255))

    -- Princess on balcony
    local princess_cel = spr:newCel(princess_layer, 1)
    local pr = princess_cel.image
    -- Princess body (pink dress)
    for x = 36, 39 do
        for y = 22, 30 do
            pr:putPixel(x, y, Color(255, 105, 180, 255))
        end
    end
    -- Princess head
    for x = 37, 38 do
        for y = 19, 21 do
            pr:putPixel(x, y, Color(255, 218, 185, 255))
        end
    end
    -- Hair (blonde)
    pr:putPixel(36, 19, Color(255, 215, 0, 255))
    pr:putPixel(36, 20, Color(255, 215, 0, 255))
    pr:putPixel(36, 21, Color(255, 215, 0, 255))
    pr:putPixel(37, 18, Color(255, 215, 0, 255))
    pr:putPixel(38, 18, Color(255, 215, 0, 255))
    pr:putPixel(39, 19, Color(255, 215, 0, 255))
    -- Crown
    pr:putPixel(37, 17, Color(255, 215, 0, 255))
    pr:putPixel(38, 17, Color(255, 215, 0, 255))
    -- Hand waving
    pr:putPixel(40, 21, Color(255, 218, 185, 255))
    pr:putPixel(41, 20, Color(255, 218, 185, 255))

    -- Knight at bottom
    local knight_cel = spr:newCel(knight_layer, 1)
    local kn = knight_cel.image
    -- Small knight (facing right, at ground level)
    -- Helmet
    kn:putPixel(10, 43, Color(192, 192, 192, 255))
    kn:putPixel(11, 43, Color(192, 192, 192, 255))
    kn:putPixel(12, 43, Color(192, 192, 192, 255))
    kn:putPixel(10, 44, Color(192, 192, 192, 255))
    kn:putPixel(11, 44, Color(0, 0, 0, 255))
    kn:putPixel(12, 44, Color(0, 0, 0, 255))
    kn:putPixel(10, 45, Color(192, 192, 192, 255))
    kn:putPixel(11, 45, Color(192, 192, 192, 255))
    kn:putPixel(12, 45, Color(192, 192, 192, 255))
    -- Body (blue)
    for x = 9, 13 do
        for y = 46, 51 do
            kn:putPixel(x, y, Color(0, 0, 180, 255))
        end
    end
    -- Armor plate
    kn:putPixel(10, 47, Color(192, 192, 192, 255))
    kn:putPixel(11, 47, Color(192, 192, 192, 255))
    kn:putPixel(12, 47, Color(192, 192, 192, 255))
    kn:putPixel(10, 48, Color(192, 192, 192, 255))
    kn:putPixel(11, 48, Color(192, 192, 192, 255))
    kn:putPixel(12, 48, Color(192, 192, 192, 255))
    -- Legs
    for y = 52, 57 do
        kn:putPixel(10, y, Color(0, 0, 180, 255))
        kn:putPixel(11, y, Color(0, 0, 180, 255))
        kn:putPixel(12, y, Color(0, 0, 180, 255))
    end
    -- Boots
    kn:putPixel(10, 58, Color(139, 69, 19, 255))
    kn:putPixel(11, 58, Color(139, 69, 19, 255))
    kn:putPixel(12, 58, Color(139, 69, 19, 255))
    -- Raised sword
    kn:putPixel(14, 40, Color(192, 192, 192, 255))
    kn:putPixel(14, 41, Color(192, 192, 192, 255))
    kn:putPixel(14, 42, Color(192, 192, 192, 255))
    kn:putPixel(14, 43, Color(192, 192, 192, 255))
    kn:putPixel(14, 44, Color(192, 192, 192, 255))
    kn:putPixel(14, 45, Color(192, 192, 192, 255))
    -- Cross guard
    kn:putPixel(13, 45, Color(192, 192, 192, 255))
    kn:putPixel(15, 45, Color(192, 192, 192, 255))
    -- Cape
    kn:putPixel(8, 46, Color(204, 0, 0, 255))
    kn:putPixel(8, 47, Color(204, 0, 0, 255))
    kn:putPixel(8, 48, Color(204, 0, 0, 255))
    kn:putPixel(8, 49, Color(204, 0, 0, 255))
    kn:putPixel(8, 50, Color(204, 0, 0, 255))
end)

spr:saveAs("{lp}")
spr:close()
"""
    success, output = cli.execute_lua_script(script)
    if success:
        size = path.stat().st_size
        print(f"  princess_rescue.aseprite ({size:,} bytes)")
        png_path = cs_dir / "princess_rescue.png"
        _export_spritesheet_png(path, png_path)
        if png_path.exists():
            print(f"  princess_rescue.png ({png_path.stat().st_size:,} bytes)")
    else:
        print(f"  Failed: {output[:200]}")


# =====================================================================
# MAIN
# =====================================================================


def main() -> None:
    print("=" * 60)
    print("  KNIGHT QUEST RPG - Asset Generator")
    print("  A knight's quest to save the princess!")
    print("=" * 60)
    print(f"\nAseprite binary: {ASEPRITE_PATH}")
    print(f"Output directory: {BASE_DIR.resolve()}\n")

    # Create subdirectories
    for subdir in ["hero", "monsters", "environment", "effects", "cutscene"]:
        (BASE_DIR / subdir).mkdir(parents=True, exist_ok=True)

    generate_hero_sprites()
    generate_monster_sprites()
    generate_environment_sprites()
    generate_effects_sprites()
    generate_cutscene_sprites()

    print("\n" + "=" * 60)
    print("  All Knight Quest assets generated!")
    print(f"  Output: {BASE_DIR.resolve()}")
    print("=" * 60)

    # List all generated files
    for f in sorted(BASE_DIR.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            size = f.stat().st_size
            print(f"  {f.relative_to(BASE_DIR)} ({size:,} bytes)")


if __name__ == "__main__":
    main()
