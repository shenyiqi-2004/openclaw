from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class HealthSnapshot:
    health: float
    delta: float
    pressure: float
    noise: float
    complexity: float


@dataclass(frozen=True)
class SignalSchema:
    query_present: bool
    repeated_steps: bool
    contradiction: bool
    consecutive_failures: bool
    rapid_health_drop: bool
    interruption_recovery: bool
    low_health: bool
    high_pressure: bool
    high_noise: bool
    abnormal_growth: bool
    low_yield_recall: bool
    has_recent_memory: bool
    canonical_backend: bool
    backend_name: str
    backend_stats: dict[str, Any]
    health: HealthSnapshot

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @property
    def active_reasons(self) -> list[str]:
        return [
            name
            for name, value in asdict(self).items()
            if isinstance(value, bool) and value
        ]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["active_reasons"] = self.active_reasons
        return data
