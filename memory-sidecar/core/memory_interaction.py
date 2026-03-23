from __future__ import annotations

from typing import Any

from core.backends.base import BackendStatus, MemoryBackend


def get_memory_backend_status(
    backend: MemoryBackend,
    backend_status: BackendStatus,
) -> dict[str, Any]:
    stats = backend.get_memory_stats()
    identity = backend.get_backend_identity()
    return {
        "name": backend_status.name,
        "available": backend_status.available,
        "canonical": backend_status.canonical,
        "mode": backend_status.mode,
        "reason": backend_status.reason,
        "identity": identity,
        "stats": stats.get("stats", stats),
        "raw_stats": stats,
    }


def recall_memory_via_backend(
    backend: MemoryBackend,
    *,
    query: str,
    scope: dict[str, Any],
    limit: int,
) -> dict[str, Any]:
    items = backend.recall_memory(query=query, scope=scope, limit=limit)
    return {
        "items": items if isinstance(items, list) else [],
        "count": len(items) if isinstance(items, list) else 0,
    }


def store_memory_via_backend(
    backend: MemoryBackend,
    *,
    text: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    result = backend.store_memory(text=text, metadata=metadata)
    return result if isinstance(result, dict) else {"stored": False, "reason": "invalid-backend-response"}


def delete_memory_via_backend(
    backend: MemoryBackend,
    *,
    memory_id: str,
) -> dict[str, Any]:
    result = backend.delete_memory(memory_id=memory_id)
    return result if isinstance(result, dict) else {"deleted": False, "reason": "invalid-backend-response"}
