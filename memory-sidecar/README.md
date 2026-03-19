# OpenClaw Memory Sidecar

`OpenClaw Memory Sidecar` is a lightweight external memory layer for OpenClaw.

This repository is intentionally small and readable. It contains:

- the Windows-side memory kernel
- the compact memory file layout
- the startup linkage that points OpenClaw at `D:\openclaw`
- the minimal WSL-side integration snapshots that show where the real OpenClaw runtime calls the sidecar
- the maintenance manual and original implementation spec

## Repository Layout

```text
OpenClaw-Memory-Sidecar/
|- AGENTS.md
|- main.py
|- core/
|- memory/
|- selfstart/
|- wsl-integration/
|- docs/
|- DIRECTORY_MANIFEST.md
|- GITHUB_DECLARATION.md
\- README.md
```

## What Each Area Is For

- `AGENTS.md`
  Runtime rules for the sidecar.
- `main.py`
  Single-cycle entry point for the memory kernel.
- `core/`
  The memory kernel modules.
- `memory/`
  Compact operational memory state.
- `selfstart/`
  Startup linkage from Windows into the WSL OpenClaw runtime.
- `wsl-integration/`
  Focused snapshots of the real OpenClaw integration points in WSL.
- `docs/`
  The original spec and the maintenance manual.

## Canonical Home

- Windows: `D:\openclaw`
- WSL mapping: `/mnt/d/openclaw`

This repository documents and publishes the sidecar system, not the entire OpenClaw monorepo.

## Notes

- The memory files included here are compact operational snapshots.
- This repository keeps the sidecar readable by placing the Windows-side runtime files at the repository root.
- The WSL integration is kept in `wsl-integration/` so the bridge points are easy to inspect without shipping the full upstream runtime.
