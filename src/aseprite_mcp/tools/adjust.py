"""Image adjustment and layer compositing tools for Aseprite MCP."""

from __future__ import annotations

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli


def _esc_path(filename: str) -> str:
    """Escape a filename for embedding in a Lua string literal,
    normalizing backslashes."""
    return _lua_escape(filename.replace("\\", "/"))


@mcp.tool()
async def adjust_colors(
    filename: str,
    layer_name: str,
    frame_index: int,
    brightness: int = 0,
    contrast: int = 0,
    hue_shift: int = 0,
    saturation: int = 0,
) -> str:
    """Apply brightness/contrast/hue/saturation adjustments to a cel's image.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to adjust
        frame_index: 1-based frame index (must be >= 1)
        brightness: Brightness adjustment (-255 to 255, 0 = no change)
        contrast: Contrast adjustment (-255 to 255, 0 = no change)
        hue_shift: Hue shift in degrees (-180 to 180, 0 = no change)
        saturation: Saturation adjustment (-255 to 255, 0 = no change)
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"
    if brightness < -255 or brightness > 255:
        return f"Error: brightness must be -255 to 255, got {brightness}"
    if contrast < -255 or contrast > 255:
        return f"Error: contrast must be -255 to 255, got {contrast}"
    if hue_shift < -180 or hue_shift > 180:
        return f"Error: hue_shift must be -180 to 180, got {hue_shift}"
    if saturation < -255 or saturation > 255:
        return f"Error: saturation must be -255 to 255, got {saturation}"

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local cel = target:cel({frame_index})
if not cel then
    return "No cel on layer '" .. "{esc_layer}" .. "' frame {frame_index}"
end

local img = cel.image
local ox = cel.position.x
local oy = cel.position.y

-- HSV helper functions
local function rgbToHsv(r, g, b)
  local rn = r / 255
  local gn = g / 255
  local bn = b / 255
  local max = math.max(rn, gn, bn)
  local min = math.min(rn, gn, bn)
  local d = max - min
  local h = 0
  local s = 0
  local v = max
  if max > 0 then s = d / max end
  if d > 0 then
    if max == rn then h = (gn - bn) / d
    elseif max == gn then h = 2 + (bn - rn) / d
    else h = 4 + (rn - gn) / d
    end
    h = h * 60
    if h < 0 then h = h + 360 end
  end
  return h, s, v
end

local function hsvToRgb(h, s, v)
  if s == 0 then
    local val = v * 255
    return val, val, val
  end
  h = h / 60
  local i = math.floor(h)
  local f = h - i
  local p = v * (1 - s)
  local q = v * (1 - s * f)
  local t = v * (1 - s * (1 - f))
  local rn, gn, bn
  if i == 0 then rn, gn, bn = v, t, p
  elseif i == 1 then rn, gn, bn = q, v, p
  elseif i == 2 then rn, gn, bn = p, v, t
  elseif i == 3 then rn, gn, bn = p, q, v
  elseif i == 4 then rn, gn, bn = t, p, v
  else rn, gn, bn = v, p, q
  end
  return rn * 255, gn * 255, bn * 255
end

app.transaction(function()
  for y = 0, img.height - 1 do
    for x = 0, img.width - 1 do
      local c = img:getPixel(x, y)
      local r = app.pixelColor.rgbaR(c)
      local g = app.pixelColor.rgbaG(c)
      local b = app.pixelColor.rgbaB(c)
      local a = app.pixelColor.rgbaA(c)

      if a > 0 then
        -- Apply brightness
        r = math.max(0, math.min(255, r + {brightness}))
        g = math.max(0, math.min(255, g + {brightness}))
        b = math.max(0, math.min(255, b + {brightness}))

        -- Apply contrast
        if {contrast} ~= 0 then
            local factor = (259 * ({contrast} + 255)) / (255 * (259 - {contrast}))
          r = math.max(0, math.min(255, math.floor(factor * (r - 128) + 128 + 0.5)))
          g = math.max(0, math.min(255, math.floor(factor * (g - 128) + 128 + 0.5)))
          b = math.max(0, math.min(255, math.floor(factor * (b - 128) + 128 + 0.5)))
        end

        -- Apply hue shift and saturation
        if {hue_shift} ~= 0 or {saturation} ~= 0 then
          local h, s, v = rgbToHsv(r, g, b)
          h = h + {hue_shift}
          if h < 0 then h = h + 360 end
          if h >= 360 then h = h - 360 end
          local sat_adj = {saturation} / 255
          s = math.max(0, math.min(1, s + sat_adj))
          local nr, ng, nb = hsvToRgb(h, s, v)
          r = math.max(0, math.min(255, math.floor(nr + 0.5)))
          g = math.max(0, math.min(255, math.floor(ng + 0.5)))
          b = math.max(0, math.min(255, math.floor(nb + 0.5)))
        end

        img:drawPixel(x, y, app.pixelColor.rgba(r, g, b, a))
      end
    end
  end
end)

spr:saveAs("{esc}")
return "Adjusted colors on layer '" .. "{esc_layer}" .. "' frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
          f"Adjusted colors on layer '{layer_name}' frame {frame_index} in {filename}"
        )
    return f"Failed to adjust colors: {output}"


@mcp.tool()
async def invert_colors(
    filename: str,
    layer_name: str,
    frame_index: int,
) -> str:
    """Invert the RGB channels of a cel's image.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to invert
        frame_index: 1-based frame index (must be >= 1)
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local cel = target:cel({frame_index})
if not cel then
    return "No cel on layer '" .. "{esc_layer}" .. "' frame {frame_index}"
end

local img = cel.image

app.transaction(function()
  for y = 0, img.height - 1 do
    for x = 0, img.width - 1 do
      local c = img:getPixel(x, y)
      local r = app.pixelColor.rgbaR(c)
      local g = app.pixelColor.rgbaG(c)
      local b = app.pixelColor.rgbaB(c)
      local a = app.pixelColor.rgbaA(c)
      if a > 0 then
        img:drawPixel(x, y, app.pixelColor.rgba(255 - r, 255 - g, 255 - b, a))
      end
    end
  end
end)

spr:saveAs("{esc}")
return "Inverted colors on layer '" .. "{esc_layer}" .. "' frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
          f"Inverted colors on layer '{layer_name}' frame {frame_index} in {filename}"
        )
    return f"Failed to invert colors: {output}"


@mcp.tool()
async def flatten_layers(
    filename: str,
) -> str:
    """Flatten all visible layers into one.

    Args:
        filename: Path to the Aseprite file
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

app.command.FlattenLayers()

spr:saveAs("{esc}")
return "Flattened all layers"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Flattened all layers in {filename}"
    return f"Failed to flatten layers: {output}"
