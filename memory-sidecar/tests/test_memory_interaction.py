from __future__ import annotations

import unittest

from core.backends.base import BackendStatus
from core.memory_interaction import (
    get_memory_backend_status,
    recall_memory_via_backend,
    store_memory_via_backend,
)


class FakeBackend:
    def get_backend_identity(self) -> dict[str, object]:
        return {"name": "fake", "kind": "test"}

    def get_memory_stats(self) -> dict[str, object]:
        return {"stats": {"items": 2}}

    def recall_memory(self, *, query: str, scope: dict, limit: int) -> list[dict]:
        return [{"memory_id": "m-1", "query": query, "limit": limit, "scope": scope}]

    def store_memory(self, *, text: str, metadata: dict) -> dict:
        return {"stored": True, "item": {"text": text, "metadata": metadata}}


class MemoryInteractionTests(unittest.TestCase):
    def test_get_memory_backend_status_combines_identity_and_stats(self) -> None:
        backend = FakeBackend()
        status = BackendStatus(
            name="memory_lancedb_pro",
            available=True,
            canonical=True,
            mode="bridge",
            reason="ok",
        )

        snapshot = get_memory_backend_status(backend, status)

        self.assertEqual(snapshot["name"], "memory_lancedb_pro")
        self.assertTrue(snapshot["canonical"])
        self.assertEqual(snapshot["identity"]["name"], "fake")
        self.assertEqual(snapshot["stats"]["items"], 2)

    def test_recall_memory_via_backend_returns_items_and_count(self) -> None:
        result = recall_memory_via_backend(
            FakeBackend(),
            query="hello",
            scope={"session": "s-1"},
            limit=3,
        )

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["memory_id"], "m-1")

    def test_store_memory_via_backend_returns_backend_result(self) -> None:
        result = store_memory_via_backend(
            FakeBackend(),
            text="fact",
            metadata={"kind": "fact"},
        )

        self.assertTrue(result["stored"])
        self.assertEqual(result["item"]["text"], "fact")


if __name__ == "__main__":
    unittest.main()
