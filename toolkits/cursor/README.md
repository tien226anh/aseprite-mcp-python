# Cursor Integration

## Setup

```bash
cp toolkits/cursor/.cursorrules /path/to/your/project/.cursorrules
```

Cursor reads `AGENTS.md` from the repo root natively — `.cursorrules` adds supplemental behavioral rules.

## What You Get

`.cursorrules` — Error handling, Lua rules, indexing, escaping, path traversal, color validation, layer targeting, drawing conventions, naming, directory organization.

## Prerequisites
- Aseprite MCP server running
- Cursor with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to `~/.cursor/mcp.json`:

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
