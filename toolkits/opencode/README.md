# OpenCode Integration

## Setup

```bash
# Copy agents
cp -r toolkits/opencode/.opencode/agents /path/to/your/project/.opencode/agents

# Copy skills
cp -r toolkits/opencode/.opencode/skills /path/to/your/project/.opencode/skills
```

OpenCode reads `AGENTS.md` from the repo root natively — no extra config needed.

## What You Get

- **9 sub-agents** in `.opencode/agents/` — Use `@agent-name` to invoke:
  - `@asset-design-orchestrator`, `@character-designer`, `@tile-designer`, `@vfx-designer`, `@background-designer`, `@item-designer`, `@animator`, `@asset-reviewer`, `@asset-exporter`
- **4 skills** in `.opencode/skills/` — `aseprite-pixel-art`, `lua-master`, `lua-debugger`, `pixel-art-designer-master`

## Prerequisites
- Aseprite MCP server running
- OpenCode with MCP configured for Aseprite MCP
- Aseprite installed and accessible
