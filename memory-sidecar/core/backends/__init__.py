from __future__ import annotations

from pathlib import Path
from typing import Any

from core.backends.base import BackendStatus
from core.backends.json_snapshot import JsonSnapshotMemoryBackend
from core.backends.lancedb_pro import LanceDbProMemoryBackend


def resolve_memory_backend(
    base_dir: str | Path,
    manager: Any,
    partition: str,
    runtime_config_path: str | Path | None = None,
) -> tuple[Any, BackendStatus]:
    lancedb_backend = LanceDbProMemoryBackend(base_dir, runtime_config_path=runtime_config_path)
    lancedb_status = lancedb_backend.status()
    if lancedb_status.available:
        return lancedb_backend, lancedb_status
    fallback = JsonSnapshotMemoryBackend(manager, partition)
    return fallback, fallback.status()
