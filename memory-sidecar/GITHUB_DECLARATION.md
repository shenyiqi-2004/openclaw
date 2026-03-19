# GitHub Declaration

This repository is a curated publication snapshot of `OpenClaw Memory Sidecar`.

It is intended to document:

- the Windows-side memory kernel
- the compact operational memory layout
- the startup linkage to `D:\openclaw`
- the focused WSL integration points that connect the real OpenClaw runtime to the sidecar

It is not a full mirror of the upstream OpenClaw monorepo.

## Canonical Runtime Paths

- Windows runtime home: `D:\openclaw`
- WSL runtime path: `/mnt/d/openclaw`

## Publication Scope

Included:

- sidecar source
- compact memory structure
- startup linkage
- integration snapshots
- maintenance documentation

Excluded:

- the full upstream OpenClaw runtime source tree
- unrelated local caches and transient files
- private machine-specific runtime state beyond the documented sidecar snapshot
