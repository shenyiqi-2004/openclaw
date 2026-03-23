from __future__ import annotations

from typing import Any

from core.backends.base import BackendStatus
from core.retriever import rebuild_index, retrieve_top_k, touch_retrieved_items


class JsonSnapshotMemoryBackend:
    def __init__(self, manager: Any, partition: str) -> None:
        self.manager = manager
        self.partition = partition

    def status(self) -> BackendStatus:
        return BackendStatus(
            name="json_snapshot",
            available=True,
            canonical=False,
            mode="fallback",
            reason="using local knowledge snapshot files",
        )

    def recall_memory(self, *, query: str, scope: dict, limit: int) -> list[dict]:
        partition_data = self.manager.load_partition(self.partition)
        rebuild_index(partition_data)
        items = retrieve_top_k(partition_data, query, k=max(1, limit))
        touch_retrieved_items(items, int(scope.get("step_count", 0)))
        self.manager.save_partition(self.partition, partition_data)
        return items

    def get_backend_identity(self) -> dict:
        return self.status().to_dict()

    def store_memory(self, *, text: str, metadata: dict) -> dict:
        stored = self.manager.add_knowledge(
            self.partition,
            text,
            list(metadata.get("tags", [])),
            float(metadata.get("importance", 0.6)),
            current_step_count=int(metadata.get("step_count", 0)),
            working=metadata.get("working"),
        )
        return {"stored": stored, "backend": "json_snapshot"}

    def update_memory(self, *, memory_id: str, patch: dict) -> dict:
        return {"updated": False, "backend": "json_snapshot", "reason": "not-supported"}

    def forget_memory(self, *, memory_id: str) -> dict:
        return {"deleted": False, "backend": "json_snapshot", "reason": "not-supported"}

    def delete_memory(self, *, memory_id: str) -> dict:
        return self.forget_memory(memory_id=memory_id)

    def get_memory_stats(self) -> dict:
        total = 0
        for name in ("programming", "science", "finance", "general"):
            total += len(self.manager.load_partition(name).get("items", []))
        return {"backend": "json_snapshot", "items": total}
