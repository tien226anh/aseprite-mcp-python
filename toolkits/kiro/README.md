# Kiro Integration

## Setup

```bash
cp -r toolkits/kiro/.kiro/steering /path/to/your/project/.kiro/steering
```

Kiro reads `AGENTS.md` from the repo root natively.

## What You Get

12 steering files in `.kiro/steering/`:

| File | Inclusion | When Loaded |
|------|-----------|-------------|
| `project-overview.md` | `always` | Every interaction |
| `coding-conventions.md` | `always` | Every interaction |
| `asset-creation.md` | `fileMatch "generated_assets/**"` | When working with assets |
| `character-design.md` | `auto` | When creating characters |
| `tile-design.md` | `auto` | When creating tiles |
| `vfx-design.md` | `auto` | When creating VFX |
| `background-design.md` | `auto` | When creating backgrounds |
| `item-design.md` | `auto` | When creating items |
| `animation.md` | `auto` | When adding animation |
| `review.md` | `manual` | Type `#review` in chat |
| `export.md` | `manual` | Type `#export` in chat |
| `orchestration.md` | `auto` | When orchestrating sessions |

## Prerequisites
- Aseprite MCP server running
- Kiro with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to your Kiro MCP config:

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
