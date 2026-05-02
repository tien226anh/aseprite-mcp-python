# Codex CLI Integration

## Setup

```bash
cp toolkits/codex/AGENTS.md /path/to/your/project/AGENTS.md
```

## What You Get

`AGENTS.md` — Architecture, commands, coding conventions, asset creation pipeline, canvas sizes, animation timing, key gotchas, testing patterns.

## Prerequisites
- Aseprite MCP server running
- Codex CLI with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to your Codex MCP config:

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
