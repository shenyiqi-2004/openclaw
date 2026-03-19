# openclaw

This repository is a curated release bundle for two closely related OpenClaw components:

- `memory-sidecar/`
  The `OpenClaw Memory Sidecar`, a lightweight external memory runtime for OpenClaw.
- `gui-desktop-control/`
  A Windows desktop control toolkit for WSL / OpenClaw workflows.

## Repository Layout

```text
openclaw/
|- README.md
|- DIRECTORY_MANIFEST.md
|- .gitignore
|- memory-sidecar/
\- gui-desktop-control/
```

## Included Modules

### memory-sidecar

Contains the Windows-side memory kernel, compact memory state, startup linkage, focused WSL integration snapshots, and maintenance docs.

### gui-desktop-control

Contains the Windows/WSL desktop GUI control bridge, scripts, tests, and docs for desktop automation from OpenClaw.

## Canonical Runtime Home

For the memory sidecar integration documented here:

- Windows: `D:\openclaw`
- WSL: `/mnt/d/openclaw`

## Notes

- This repository is a curated publishable bundle, not a full upstream OpenClaw monorepo mirror.
- Each subdirectory keeps its own internal structure so it can still be inspected independently.
