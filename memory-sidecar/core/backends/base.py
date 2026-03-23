from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class BackendStatus:
    name: str
    available: bool
    canonical: bool
    mode: str
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class MemoryBackend(Protocol):
    def status(self) -> BackendStatus: ...

    def get_backend_identity(self) -> dict[str, object]: ...

    def recall_memory(self, *, query: str, scope: dict, limit: int) -> list[dict]: ...

    def store_memory(self, *, text: str, metadata: dict) -> dict: ...

    def update_memory(self, *, memory_id: str, patch: dict) -> dict: ...

    def delete_memory(self, *, memory_id: str) -> dict: ...

    def forget_memory(self, *, memory_id: str) -> dict: ...

    def get_memory_stats(self) -> dict: ...
