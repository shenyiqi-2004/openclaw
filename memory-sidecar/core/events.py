from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.utils import now_iso, save_json


@dataclass(frozen=True)
class EventContext:
    event_id: str
    source: str
    status: str
    session_key: str
    agent_id: str
    replayed: bool


def _memory_dir(base_dir: str | Path) -> Path:
    return Path(base_dir) / "memory"


def _jsonl_path(base_dir: str | Path, name: str) -> Path:
    return _memory_dir(base_dir) / name


def load_event_context() -> EventContext | None:
    event_id = os.environ.get("OPENCLAW_MEMORY_EVENT_ID", "").strip()
    if not event_id:
        return None
    return EventContext(
        event_id=event_id,
        source=os.environ.get("OPENCLAW_MEMORY_SOURCE", "").strip(),
        status=os.environ.get("OPENCLAW_MEMORY_STATUS", "").strip(),
        session_key=os.environ.get("OPENCLAW_MEMORY_SESSION_KEY", "").strip(),
        agent_id=os.environ.get("OPENCLAW_MEMORY_AGENT_ID", "").strip(),
        replayed=os.environ.get("OPENCLAW_MEMORY_REPLAY", "0").strip() == "1",
    )


def append_jsonl(base_dir: str | Path, filename: str, record: dict[str, Any]) -> None:
    path = _jsonl_path(base_dir, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")


def append_trace(
    base_dir: str | Path,
    *,
    event: EventContext | None,
    action: str,
    level: str = "info",
    **extra: Any,
) -> None:
    record = {
        "timestamp": now_iso(),
        "level": level,
        "action": action,
    }
    if event is not None:
        record.update(
            {
                "event_id": event.event_id,
                "source": event.source,
                "status": event.status,
                "session_key": event.session_key,
                "agent_id": event.agent_id,
                "replayed": event.replayed,
            }
        )
    record.update(extra)
    append_jsonl(base_dir, "traces.jsonl", record)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def get_recovery_event(base_dir: str | Path, event_id: str) -> dict[str, Any] | None:
    recovery = _load_json(_memory_dir(base_dir) / "recovery.json", {"events": {}})
    events = recovery.get("events", {})
    if isinstance(events, dict):
        event = events.get(event_id)
        return event if isinstance(event, dict) else None
    return None


def update_recovery_event(base_dir: str | Path, event_id: str, **fields: Any) -> None:
    path = _memory_dir(base_dir) / "recovery.json"
    recovery = _load_json(path, {"version": 1, "order": [], "events": {}})
    events = recovery.setdefault("events", {})
    current = events.get(event_id, {}) if isinstance(events, dict) else {}
    if not isinstance(current, dict):
        current = {}
    current.update(fields)
    current["updated_at"] = now_iso()
    if isinstance(events, dict):
        events[event_id] = current
    save_json(path, recovery)


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
            except Exception:
                continue
            if isinstance(data, dict):
                records.append(data)
    return records


def has_ack(base_dir: str | Path, event_id: str) -> bool:
    for record in reversed(iter_jsonl(_jsonl_path(base_dir, "acks.jsonl"))):
        if record.get("event_id") == event_id and record.get("ack") is True:
            return True
    return False


def runtime_has_event(runtime_data: dict[str, Any], event_id: str) -> bool:
    for record in reversed(runtime_data.get("records", [])):
        if record.get("event_id") == event_id:
            return True
    return False


def ack_event(base_dir: str | Path, event: EventContext, *, outcome: str, details: dict[str, Any] | None = None) -> None:
    append_jsonl(
        base_dir,
        "acks.jsonl",
        {
            "timestamp": now_iso(),
            "event_id": event.event_id,
            "source": event.source,
            "status": event.status,
            "session_key": event.session_key,
            "agent_id": event.agent_id,
            "replayed": event.replayed,
            "ack": True,
            "outcome": outcome,
            "details": details or {},
        },
    )
    update_recovery_event(
        base_dir,
        event.event_id,
        sidecar_ack=True,
        sidecar_ack_at=now_iso(),
        sidecar_ack_outcome=outcome,
    )
