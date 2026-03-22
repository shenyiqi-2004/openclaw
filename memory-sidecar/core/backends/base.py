from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BackendStatus:
    name: str
    available: bool
    canonical: bool
    mode: str
    reason: str = ""


class MemoryBackend(Protocol):
    def status(self) -> BackendStatus: ...

    def recall_memory(self, *, query: str, scope: dict, limit: int) -> list[dict]: ...

    def store_memory(self, *, text: str, metadata: dict) -> dict: ...

    def update_memory(self, *, memory_id: str, patch: dict) -> dict: ...

    def forget_memory(self, *, memory_id: str) -> dict: ...

    def get_memory_stats(self) -> dict: ...
