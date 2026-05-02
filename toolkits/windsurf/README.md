# Windsurf Integration

## Setup

```bash
# Copy rules
cp -r toolkits/windsurf/.windsurf/rules /path/to/your/project/.windsurf/rules

# Copy skills
cp -r toolkits/windsurf/.windsurf/skills /path/to/your/project/.windsurf/skills
```

Windsurf reads `AGENTS.md` from the repo root natively.

## What You Get

- **4 rules** in `.windsurf/rules/`:
  - `coding-conventions.md` (always_on) — Error handling, Lua rules, indexing, escaping
  - `asset-creation.md` (glob: generated_assets/**) — Pipeline, canvas sizes, layer architecture
  - `agent-workflows.md` (model_decision) — All 9 specialist workflows
  - `tool-reference.md` (manual) — Complete tool selection matrix
- **4 skills** in `.windsurf/skills/` — `aseprite-pixel-art`, `lua-master`, `lua-debugger`, `pixel-art-designer-master`

## Prerequisites
- Aseprite MCP server running
- Windsurf with MCP configured for Aseprite MCP
- Aseprite installed and accessible

### MCP Configuration

Add to `~/.codeium/windsurf/mcp_config.json`:

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
