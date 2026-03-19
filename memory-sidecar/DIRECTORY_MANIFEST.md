# Directory Manifest

Root: `OpenClaw-Memory-Sidecar`

## Top Level

- `AGENTS.md`
  Sidecar runtime rules.
- `main.py`
  Memory kernel entry point.
- `core/`
  Python modules that implement routing, retrieval, cleaning, reflection, execution, and selfcheck.
- `memory/`
  Compact operational memory state used by the sidecar.
- `selfstart/`
  Startup linkage for the external memory root.
- `wsl-integration/`
  Real OpenClaw integration snapshots from the WSL runtime.
- `docs/`
  Manual and original implementation spec.
- `README.md`
  Repository overview.
- `GITHUB_DECLARATION.md`
  Publication and provenance statement.

## core

- `cleaner.py`
- `executor.py`
- `memory_manager.py`
- `reflection_manager.py`
- `retriever.py`
- `router.py`
- `selfcheck_manager.py`
- `strategy_manager.py`
- `utils.py`

## memory

- `working.json`
- `summary.json`
- `strategy.json`
- `reflection.json`
- `selfcheck.json`
- `runtime.json`
- `meta.json`
- `knowledge/`

## memory/knowledge

- `programming.json`
- `general.json`
- `science.json`
- `finance.json`

## selfstart

- `Start-OpenClaw-WSL-Interactive.cmd`

## wsl-integration

- `package.json`
- `bin/openclaw`
- `src/infra/external-memory-kernel.ts`
- `src/gateway/server-methods/chat.ts`
- `src/gateway/server-methods/agent.ts`
- `src/auto-reply/reply/agent-runner.ts`
- `src/cli/gateway-cli/run.ts`
- `src/cli/gateway-cli/run-loop.ts`

## docs

- `direct.md`
- `openclaw_full_work_manual.tex`
- `openclaw_full_work_manual.pdf`
