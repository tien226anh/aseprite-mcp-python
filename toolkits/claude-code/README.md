# Claude Code Integration

## Setup

```bash
# Copy CLAUDE.md
cp toolkits/claude-code/CLAUDE.md /path/to/your/project/

# Copy agents
cp -r toolkits/claude-code/.claude/agents /path/to/your/project/.claude/agents

# Copy skills
cp -r toolkits/claude-code/.claude/skills /path/to/your/project/.claude/skills
```

## What You Get

- **`CLAUDE.md`** — Project conventions, architecture, coding rules, asset pipeline, gotchas
- **9 sub-agents** in `.claude/agents/` — Use `@agent-name` to invoke:
  - `@asset-design-orchestrator` — Coordinate multi-asset sessions
  - `@character-designer` — Create character sprites
  - `@tile-designer` — Create tilesets
  - `@vfx-designer` — Create VFX effects
  - `@background-designer` — Create parallax backgrounds
  - `@item-designer` — Create items and pickups
  - `@animator` — Add animation to sprites
  - `@asset-reviewer` — Review and fix quality issues
  - `@asset-exporter` — Export and package assets
- **4 skills** in `.claude/skills/` — `aseprite-pixel-art`, `lua-master`, `lua-debugger`, `pixel-art-designer-master`

## Prerequisites
- Aseprite MCP server running
- Claude Code with MCP configured for Aseprite MCP
- Aseprite installed and accessible
