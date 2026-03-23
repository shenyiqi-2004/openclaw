from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_RUNTIME_ROOT = Path("/home/park/openclaw")
DEFAULT_MEMORY_ROOT = DEFAULT_RUNTIME_ROOT / "memory-sidecar"
DEPRECATED_MEMORY_ROOTS = (
    Path("/mnt/d/openclaw"),
    Path("D:/openclaw"),
)


@dataclass(frozen=True)
class MemoryRootStatus:
    runtime_root: Path
    memory_root: Path
    source: str
    deprecated: bool


def resolve_runtime_root() -> Path:
    configured = os.environ.get("OPENCLAW_RUNTIME_ROOT", "").strip()
    if configured:
        return Path(configured)
    return DEFAULT_RUNTIME_ROOT


def resolve_memory_root(explicit_base: str | Path | None = None) -> Path:
    if explicit_base is not None:
        return Path(explicit_base).resolve()
    configured = os.environ.get("OPENCLAW_EXTERNAL_MEMORY_ROOT", "").strip()
    if configured:
        return Path(configured).resolve()
    return Path(__file__).resolve().parents[1]


def resolve_runtime_config_path(runtime_root: str | Path | None = None) -> Path:
    root = Path(runtime_root).resolve() if runtime_root is not None else resolve_runtime_root()
    return root / ".openclaw" / "openclaw.json"


def describe_memory_root(explicit_base: str | Path | None = None) -> MemoryRootStatus:
    runtime_root = resolve_runtime_root()
    memory_root = resolve_memory_root(explicit_base)
    configured = os.environ.get("OPENCLAW_EXTERNAL_MEMORY_ROOT", "").strip()
    if explicit_base is not None:
        source = "explicit"
    elif configured:
        source = "env:OPENCLAW_EXTERNAL_MEMORY_ROOT"
    else:
        source = "code-default"
    deprecated = any(memory_root == path.resolve() for path in DEPRECATED_MEMORY_ROOTS)
    return MemoryRootStatus(
        runtime_root=runtime_root,
        memory_root=memory_root,
        source=source,
        deprecated=deprecated,
    )
