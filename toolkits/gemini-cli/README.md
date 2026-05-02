# Gemini CLI Integration

## Setup

```bash
# Copy GEMINI.md
cp toolkits/gemini-cli/GEMINI.md /path/to/your/project/

# Copy agents
cp -r toolkits/gemini-cli/.gemini/agents /path/to/your/project/.gemini/agents
```

To also read `AGENTS.md`, add to `~/.gemini/settings.json`:
```json
{ "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
```

## What You Get

- **`GEMINI.md`** — Project conventions, architecture, coding rules, asset pipeline, gotchas
- **9 sub-agents** in `.gemini/agents/` — Use `@agent-name` to invoke:
  - `@asset-design-orchestrator`, `@character-designer`, `@tile-designer`, `@vfx-designer`, `@background-designer`, `@item-designer`, `@animator`, `@asset-reviewer`, `@asset-exporter`

## Prerequisites
- Aseprite MCP server running
- Gemini CLI with MCP configured for Aseprite MCP
- Aseprite installed and accessible
