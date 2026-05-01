"""Lua script generators for Aseprite batch operations."""

from __future__ import annotations


def create_sprite_script(
    width: int,
    height: int,
    color_mode: str = "rgb",
    output_path: str = "",
) -> str:
    mode_map = {"rgb": "RGB", "grayscale": "GRAYSCALE", "indexed": "INDEXED"}
    mode_str = mode_map.get(color_mode.lower(), "RGB")
    save_line = f'\nsprite:saveAs("{_lua_escape(output_path)}")' if output_path else ""
    return f"""local sprite = Sprite({width}, {height}, ColorMode.{mode_str})
{save_line}
print("JSON_START" .. json.encode({{
  width = sprite.width,
  height = sprite.height,
  colorMode = "{color_mode}",
  filename = sprite.filename
}}))
app.exit()
"""


def sprite_info_script(file_path: str) -> str:
    return f"""local sprite = app.open("{_lua_escape(file_path)}")
if not sprite then
  print("Error: Could not open file")
  app.exit(1)
  return
end
local layers = {{}}
for i, layer in ipairs(sprite.layers) do
  layers[i] = layer.name
end
local tags = {{}}
for i = 1, #sprite.tags do
  local tag = sprite.tags[i]
  tags[i] = {{
    name = tag.name,
    from = tag.fromFrame.frameNumber,
    to = tag.toFrame.frameNumber,
  }}
end
local frames = {{}}
for i = 1, #sprite.frames do
  frames[i] = {{ duration = sprite.frames[i].duration }}
end
local palettes = {{}}
for i = 1, #sprite.palettes do
  local pal = sprite.palettes[i]
  local colors = {{}}
  for j = 0, #pal - 1 do
    local c = pal:getColor(j)
    colors[j + 1] = {{ r = c.red, g = c.green, b = c.blue, a = c.alpha }}
  end
  palettes[i] = {{ frame = pal.frame, colors = colors }}
end
local cmNames = {{ [0] = "rgb", "grayscale", "indexed" }}
local cmName = cmNames[sprite.colorMode] or "unknown"
print("JSON_START" .. json.encode({{
  filename = sprite.filename,
  width = sprite.width,
  height = sprite.height,
  colorMode = cmName,
  frames = #sprite.frames,
  layers = layers,
  tags = tags,
  frameData = frames,
  palettes = palettes
}}))
sprite:close()
app.exit()
"""


def export_sprite_script(
    input_path: str,
    output_path: str,
    format: str = "png",
) -> str:
    return f"""local sprite = app.open("{_lua_escape(input_path)}")
if not sprite then
  print("Error: Could not open sprite")
  app.exit(1)
  return
end
sprite:saveAs("{_lua_escape(output_path)}")
print("JSON_START" .. json.encode({{
  output = "{_lua_escape(output_path)}",
  success = true
}}))
sprite:close()
app.exit()
"""


def draw_pixels_script(pixels: list[dict[str, int | str]]) -> str:
    pixel_lines: list[str] = []
    for p in pixels:
        x = int(p["x"])
        y = int(p["y"])
        color = str(p["color"])
        pixel_lines.append(
            f"  image:drawPixel({x}, {y}, app.pixelColor.rgba({color}))"
        )
    pixel_code = "\n".join(pixel_lines)
    return f"""local sprite = app.activeSprite
if not sprite then
  print("Error: No active sprite")
  app.exit(1)
  return
end
local image = sprite.cels[1].image
{pixel_code}
sprite:saveAs(sprite.filename)
print("JSON_START" .. json.encode({{ success = true, pixels = {len(pixels)} }}))
app.exit()
"""


def fill_rect_script(x: int, y: int, w: int, h: int, color: str) -> str:
    return f"""local sprite = app.activeSprite
if not sprite then
  print("Error: No active sprite")
  app.exit(1)
  return
end
local image = sprite.cels[1].image
for py = {y}, {y} + {h} - 1 do
  for px = {x}, {x} + {w} - 1 do
    image:drawPixel(px, py, app.pixelColor.rgba("{color}"))
  end
end
sprite:saveAs(sprite.filename)
print("JSON_START" .. json.encode({{
  success = true,
  x = {x}, y = {y}, width = {w}, height = {h}
}}))
app.exit()
"""


_WS_BRIDGE_TEMPLATE = """local json = require("json") or {
  parse = function(s) return nil end,
  encode = function(t) return "{}" end
}
local ws = WebSocket {
  url = "{ws_url}",
  onreceive = function(msg_type, data, err)
    if msg_type == WebSocketMessageType.TEXT then
      local ok, cmd = pcall(function() return json.parse(data) end)
      if not ok or not cmd then
        ws:sendText('{"status":"error","message":"invalid JSON"}')
        return
      end
      local action = cmd.action
      if action == "ping" then
        ws:sendText('{"status":"pong"}')
      elseif action == "draw_pixels" then
        local sprite = app.activeSprite
        if not sprite then
          ws:sendText('{"status":"error","message":"no active sprite"}')
          return
        end
        local image = sprite.cels[1].image
        local count = 0
        if cmd.pixels then
          for _, p in ipairs(cmd.pixels) do
            image:drawPixel(p.x, p.y, app.pixelColor.rgba(p.color))
            count = count + 1
          end
        end
        sprite:saveAs(sprite.filename)
        ws:sendText('{"status":"ok","drawn":' .. count .. '}')
      elseif action == "fill_rect" then
        local sprite = app.activeSprite
        if not sprite then
          ws:sendText('{"status":"error","message":"no active sprite"}')
          return
        end
        local image = sprite.cels[1].image
        for py = cmd.y, cmd.y + cmd.h - 1 do
          for px = cmd.x, cmd.x + cmd.w - 1 do
            image:drawPixel(px, py, app.pixelColor.rgba(cmd.color))
          end
        end
        sprite:saveAs(sprite.filename)
        ws:sendText('{"status":"ok","x":' .. cmd.x .. ',"y":' .. cmd.y .. '}')
      elseif action == "sprite_info" then
        local sprite = app.activeSprite
        if not sprite then
          ws:sendText('{"status":"error","message":"no active sprite"}')
          return
        end
        ws:sendText(json.encode({
          status = "ok",
          width = sprite.width,
          height = sprite.height,
          frames = #sprite.frames
        }))
      elseif action == "close" then
        ws:close()
        app.exit()
      else
        ws:sendText(
          '{"status":"error","message":"unknown action: "'
            .. ' .. (action or "nil") .. '"}'
        )
      end
    end
  end
}
ws:connect()
"""


def ws_bridge_script(ws_url: str) -> str:
    return _WS_BRIDGE_TEMPLATE.replace("{ws_url}", ws_url)


def _lua_escape(s: str) -> str:
    """Escape a string for safe embedding inside a Lua double-quoted string literal."""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\0", "\\0")
    )
