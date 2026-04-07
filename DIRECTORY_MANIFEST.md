# Directory Manifest

Root: `openclaw`

## Top Level

- `README.md`
  Repository overview.
- `DIRECTORY_MANIFEST.md`
  High-level directory map.
- `.gitignore`
  Ignore rules for generated noise.
- `memory-sidecar/`
  OpenClaw Memory Sidecar release package.
- `evolution-protocol/`
  Evolution Protocol: memory + reflection + pattern system for OpenClaw.
- `gui-desktop-control/`
  OpenClaw GUI desktop control release package.
- `openclaw-security/`
  Security plugin: 15-layer exec security check, permission model, before_tool_call hook.
- `openclaw-orchestration/`
  Orchestration plugin: tool classification, intelligent concurrency scheduling, execution stats.
- `openclaw-governance/`
  Governance plugin: SQLite-based decision log, governance event audit, tool stat aggregation.
- `openclaw-skills-bundle/`
  Skill collection: 10 new skills + 5 enhanced skills for OpenClaw.

## memory-sidecar

Includes:

- `AGENTS.md`
- `main.py`
- `core/`
- `memory/`
- `selfstart/`
- `wsl-integration/`
- `docs/`

## gui-desktop-control

Includes:

- `README.md`
- `LICENSE`
- `ROADMAP.md`
- `docs/`
- `tests/`
- `windows/`
- `wsl/`

## openclaw-security

OpenClaw security plugin providing exec command security validation and permission checking.

Includes:

- `src/tools/` — exec-security-check, permission-check
- `src/plugin/` — plugin entry with before_tool_call hook

## openclaw-orchestration

OpenClaw orchestration plugin providing tool classification and intelligent scheduling.

Includes:

- `src/tools/` — tool-classify, orchestrate-tools, execution-stats
- `src/lib/` — tool registry, concurrency planner

## openclaw-governance

OpenClaw governance plugin providing SQLite-based audit trail for decisions and events.

Includes:

- `src/tools/` — log_decision, query_decisions, log_governance_event, query_governance_events, log_tool_stat, tool_stats_summary
- `src/db/` — SQLite schema initialization

## openclaw-skills-bundle

Skill collection for OpenClaw workspace.

### new/ (10 skills added 2026-04-07)

- `bug-round-system/` — Bug regression tracking with numbered rounds
- `compact-strategies/` — Four context compaction strategies (summarizer/auto/micro/sessionMemory)
- `exec-security-guide/` — 23-layer security checklist for shell commands
- `hook-system/` — Hook event system with four execution models
- `mcp-transport/` — MCP server tool wrapper
- `permission-model/` — Three-layer permission model (whitelist/semantic/sandbox)
- `plugin-lifecycle/` — Plugin discover→validate→load→reconcile→cache lifecycle
- `settings-layered/` — Six-source config merging (managed/local/CLI/env/MDM/drop-in)
- `test-strategies/` — Test strategy matrix for OpenClaw
- `tool-orchestration/` — Read-only concurrency + non-read-only serialization strategy

### enhanced/ (5 skills updated 2026-04-07)

- `code-review/` — Enhanced with MCP/permission/Plugin SDK review
- `context-budget/` — Token four-tier strategy (head/protected/core/compact)
- `security-review/` — Appended exec security checklist
- `tdd-workflow/` — Enhanced with boundary value bombing
- `verification-loop/` — Enhanced with cache break detection
