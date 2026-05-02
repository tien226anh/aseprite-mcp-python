# Continue Integration

## Setup

```bash
cp -r toolkits/continue/.continue/rules /path/to/your/project/.continue/rules
```

## What You Get

4 rules in `.continue/rules/`:
- `coding-conventions.md` — Error handling, Lua rules, indexing, escaping, testing
- `asset-creation.md` — Pipeline, naming, canvas sizes, layer architecture, animation timing
- `agent-workflows.md` — All 9 specialist workflows as sequential guides
- `tool-reference.md` — Complete tool selection matrix

## Prerequisites
- Aseprite MCP server running
- Continue with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to `~/.continue/config.json`:

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
