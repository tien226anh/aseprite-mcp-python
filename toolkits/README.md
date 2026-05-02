# Toolkits

Integration kits for using the aseprite-mcp-python project conventions, agents, and skills with various AI coding tools.

Each subdirectory contains files adapted to that tool's native format — drop them into your project and the tool will automatically pick them up.

## The Converging Standards

Most AI coding tools now support the same three standards:

| Standard         | Spec                                                        | What It Is                                       |
| ---------------- | ----------------------------------------------------------- | ------------------------------------------------ |
| **AGENTS.md**    | [agents.md](https://agents.md/)                             | Project-level agent instructions in repo root    |
| **Agent Skills** | [agentskills.io](https://agentskills.io/home)               | `SKILL.md` + `references/` in a skills directory |
| **MCP**          | [modelcontextprotocol.io](https://modelcontextprotocol.io/) | Tool server protocol                             |

All 10 tools below support MCP. The differences are in which of the other standards they support and where they look for files.

## Supported Tools

| #   | Tool            |   Reads AGENTS.md?   |  Agents (file-based)  |   Skills (SKILL.md)   | Directory                        |
| --- | --------------- | :------------------: | :-------------------: | :-------------------: | -------------------------------- |
| 1   | **Claude Code** |    ❌ (CLAUDE.md)     |  ✅ `.claude/agents/`  |  ✅ `.claude/skills/`  | [`claude-code/`](./claude-code/) |
| 2   | **Gemini CLI**  |    ❌ (GEMINI.md)     |  ✅ `.gemini/agents/`  |           ❌           | [`gemini-cli/`](./gemini-cli/)   |
| 3   | **OpenCode**    |          ✅           | ✅ `.opencode/agents/` | ✅ `.opencode/skills/` | [`opencode/`](./opencode/)       |
| 4   | **Cline**       |    ❌ (CLAUDE.md)     |    ⚠️ Dynamic only     |  ✅ `.agents/skills/`  | [`cline/`](./cline/)             |
| 5   | **Windsurf**    |          ✅           |           ❌           | ✅ `.windsurf/skills/` | [`windsurf/`](./windsurf/)       |
| 6   | **Kiro**        |          ✅           |     ❌ (steering)      |           ❌           | [`kiro/`](./kiro/)               |
| 7   | **Cursor**      |          ✅           |           ❌           |           ❌           | [`cursor/`](./cursor/)           |
| 8   | **Aider**       |  ❌ (CONVENTIONS.md)  |           ❌           |           ❌           | [`aider/`](./aider/)             |
| 9   | **Continue**    | ❌ (.continue/rules/) |           ❌           |           ❌           | [`continue/`](./continue/)       |
| 10  | **Codex CLI**   |          ✅           |           ❌           |           ❌           | [`codex/`](./codex/)             |

## What's in Each Toolkit

### Tools with Full Agent + Skill Support

| Toolkit         | Config File              | Agents                          | Skills                          |
| --------------- | ------------------------ | ------------------------------- | ------------------------------- |
| **Claude Code** | `CLAUDE.md`              | 9 agents in `.claude/agents/`   | 4 skills in `.claude/skills/`   |
| **OpenCode**    | (reads repo `AGENTS.md`) | 9 agents in `.opencode/agents/` | 4 skills in `.opencode/skills/` |
| **Gemini CLI**  | `GEMINI.md`              | 9 agents in `.gemini/agents/`   | —                               |

### Tools with Skill Support Only

| Toolkit      | Config File              | Skills                          | Extra                      |
| ------------ | ------------------------ | ------------------------------- | -------------------------- |
| **Cline**    | `CLAUDE.md`              | 4 skills in `.agents/skills/`   | 4 `.clinerules/` files     |
| **Windsurf** | (reads repo `AGENTS.md`) | 4 skills in `.windsurf/skills/` | 4 `.windsurf/rules/` files |

### Tools with Rules/Conventions Only

| Toolkit       | Config File                | Content                                                |
| ------------- | -------------------------- | ------------------------------------------------------ |
| **Kiro**      | (reads repo `AGENTS.md`)   | 12 `.kiro/steering/` files with `inclusion:` modes     |
| **Cursor**    | `.cursorrules`             | Supplemental behavioral rules                          |
| **Aider**     | `CONVENTIONS.md`           | Coding conventions + testing patterns                  |
| **Continue**  | 4 `.continue/rules/` files | Conventions, asset creation, workflows, tool reference |
| **Codex CLI** | `AGENTS.md`                | Architecture, conventions, asset pipeline, gotchas     |

## Source → Toolkit Mapping

When source files in `.github/` or `AGENTS.md` change, update the corresponding toolkit files.

### Agents (`.github/agents/*.agent.md`)

| Source            | Claude Code           | Gemini CLI            | OpenCode                |
| ----------------- | --------------------- | --------------------- | ----------------------- |
| All 9 agent files | `.claude/agents/*.md` | `.gemini/agents/*.md` | `.opencode/agents/*.md` |

Agent files are **direct ports** — same YAML+markdown format, adapted frontmatter per tool.

### Skills (`.github/skills/*/`)

| Source           | Claude Code       | OpenCode            | Cline             | Windsurf            |
| ---------------- | ----------------- | ------------------- | ----------------- | ------------------- |
| All 4 skill dirs | `.claude/skills/` | `.opencode/skills/` | `.agents/skills/` | `.windsurf/skills/` |

Skill directories are **direct copies** — no changes needed (same SKILL.md standard).

### AGENTS.md / Conventions

| Source                            | Claude Code | Gemini CLI  | Cline          | Cursor         | Aider            | Continue           | Codex       | Kiro              | Windsurf           |
| --------------------------------- | ----------- | ----------- | -------------- | -------------- | ---------------- | ------------------ | ----------- | ----------------- | ------------------ |
| `AGENTS.md`                       | `CLAUDE.md` | `GEMINI.md` | `CLAUDE.md`    | `.cursorrules` | `CONVENTIONS.md` | `.continue/rules/` | `AGENTS.md` | `.kiro/steering/` | `.windsurf/rules/` |
| `aseprite-mcp.instructions.md`    | `CLAUDE.md` | `GEMINI.md` | `.clinerules/` | `.cursorrules` | `CONVENTIONS.md` | `.continue/rules/` | `AGENTS.md` | `.kiro/steering/` | `.windsurf/rules/` |
| `aseprite-assets.instructions.md` | `CLAUDE.md` | `GEMINI.md` | `.clinerules/` | `.cursorrules` | —                | `.continue/rules/` | `AGENTS.md` | `.kiro/steering/` | `.windsurf/rules/` |

## Keeping Toolkits in Sync

These toolkits are **manually maintained**. When you update a source file:

1. Check the mapping tables above to find affected toolkit files
2. Update each affected file with the corresponding changes
3. For agent/skill files, the changes are usually just path/frontmatter adjustments

## Prerequisites

All toolkits assume:
- The **Aseprite MCP server** is running (stdio or HTTP mode)
- The target tool has **MCP support** configured to connect to the Aseprite MCP server
- Aseprite is installed and accessible
