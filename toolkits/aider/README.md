# Aider Integration

## Setup

```bash
cp toolkits/aider/CONVENTIONS.md /path/to/your/project/CONVENTIONS.md
```

Run aider with: `aider --conventions CONVENTIONS.md`

## What You Get

`CONVENTIONS.md` — Error handling, Lua rules, indexing, escaping, path traversal, color validation, layer targeting, Python conventions, testing patterns.

## Prerequisites
- Aseprite MCP server running
- Aider with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to your Aider MCP config:

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
