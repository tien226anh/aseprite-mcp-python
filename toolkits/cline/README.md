# Cline Integration

## Setup

```bash
# Copy CLAUDE.md
cp toolkits/cline/CLAUDE.md /path/to/your/project/

# Copy .clinerules
cp -r toolkits/cline/.clinerules /path/to/your/project/

# Copy skills
cp -r toolkits/cline/.agents/skills /path/to/your/project/.agents/skills
```

## What You Get

- **`CLAUDE.md`** — Project conventions, architecture, coding rules, asset pipeline, gotchas
- **4 `.clinerules/` files** — Coding conventions, asset creation, agent workflows, tool reference
- **4 skills** in `.agents/skills/` — `aseprite-pixel-art`, `lua-master`, `lua-debugger`, `pixel-art-designer-master`

## Prerequisites
- Aseprite MCP server running
- Cline with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

In Cline's MCP settings (via extension UI):

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uvx",
      "args": ["aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/path/to/aseprite"
      }
    }
  }
}
```
