from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.utils import now_iso, save_json


@dataclass(frozen=True)
class EventContext:
    event_id: str
    request_id: str
    source: str
    status: str
    session_key: str
    agent_id: str
    replayed: bool
    timestamp: str = ""
    payload_hash: str = ""
    attempt_count: int = 0


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
        request_id=os.environ.get("OPENCLAW_MEMORY_REQUEST_ID", "").strip(),
        source=os.environ.get("OPENCLAW_MEMORY_SOURCE", "").strip(),
        status=os.environ.get("OPENCLAW_MEMORY_STATUS", "").strip(),
        session_key=os.environ.get("OPENCLAW_MEMORY_SESSION_KEY", "").strip(),
        agent_id=os.environ.get("OPENCLAW_MEMORY_AGENT_ID", "").strip(),
        replayed=os.environ.get("OPENCLAW_MEMORY_REPLAY", "0").strip() == "1",
        timestamp=os.environ.get("OPENCLAW_MEMORY_TIMESTAMP", "").strip(),
        payload_hash=os.environ.get("OPENCLAW_MEMORY_PAYLOAD_HASH", "").strip(),
        attempt_count=int(os.environ.get("OPENCLAW_MEMORY_ATTEMPT_COUNT", "0") or 0),
    )


def event_context_from_record(record: dict[str, Any], *, replayed: bool) -> EventContext:
    return EventContext(
        event_id=str(record.get("event_id", "")),
        request_id=str(record.get("request_id", "")),
        source=str(record.get("source", "")),
        status=str(record.get("status", "")),
        session_key=str(record.get("session_key", "")),
        agent_id=str(record.get("agent_id", "")),
        replayed=replayed,
        timestamp=str(record.get("timestamp", "")),
        payload_hash=str(record.get("payload_hash", "")),
        attempt_count=int(record.get("attempt_count", 0) or 0),
    )


def build_worker_task_id(event: EventContext | None) -> str:
    if event is None or not event.event_id:
        return ""
    attempt = int(event.attempt_count or 0)
    return f"{event.event_id}:{attempt}" if attempt > 0 else event.event_id


def build_correlation(
    event: EventContext | None,
    *,
    runtime_step: int = 0,
    ack_id: str = "",
    work_class: str = "",
    worker_task_id: str = "",
    replay_attempt: int | None = None,
) -> dict[str, Any]:
    if event is None:
        return {}
    return {
        "request_id": event.request_id,
        "event_id": event.event_id,
        "worker_task_id": worker_task_id or build_worker_task_id(event),
        "runtime_step": int(runtime_step),
        "ack_id": ack_id,
        "replay_attempt": int(event.attempt_count if replay_attempt is None else replay_attempt),
        "work_class": work_class,
    }


def append_jsonl(base_dir: str | Path, filename: str, record: dict[str, Any]) -> None:
    path = _jsonl_path(base_dir, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")


def append_commit_record(
    base_dir: str | Path,
    *,
    event: EventContext,
    outcome: str,
    ack_id: str = "",
    runtime_step: int = 0,
    failure_reason: str = "",
) -> dict[str, Any]:
    record = {
        "timestamp": now_iso(),
        "commit_id": uuid4().hex,
        "event_id": event.event_id,
        "request_id": event.request_id,
        "source": event.source,
        "status": event.status,
        "session_key": event.session_key,
        "agent_id": event.agent_id,
        "replayed": event.replayed,
        "replay_attempt": event.attempt_count,
        "outcome": outcome,
        "ack_id": ack_id,
        "runtime_step": runtime_step,
        "failure_reason": failure_reason,
        "correlation": build_correlation(
            event,
            runtime_step=runtime_step,
            ack_id=ack_id,
            replay_attempt=event.attempt_count,
        ),
    }
    append_jsonl(base_dir, "commits.jsonl", record)
    return record


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
                "request_id": event.request_id,
                "source": event.source,
                "status": event.status,
                "session_key": event.session_key,
                "agent_id": event.agent_id,
                "replayed": event.replayed,
                "replay_attempt": event.attempt_count,
            }
        )
    record.update(extra)
    if event is not None and "correlation" not in record:
        record["correlation"] = build_correlation(
            event,
            runtime_step=int(record.get("runtime_step", 0) or 0),
            ack_id=str(record.get("ack_id", "") or ""),
            work_class=str(record.get("work_class", "") or ""),
            worker_task_id=str(record.get("worker_task_id", "") or ""),
            replay_attempt=int(record.get("replay_attempt", event.attempt_count) or 0),
        )
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


def ack_event(
    base_dir: str | Path,
    event: EventContext,
    *,
    outcome: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "timestamp": now_iso(),
        "ack_id": uuid4().hex,
        "event_id": event.event_id,
        "request_id": event.request_id,
        "source": event.source,
        "status": event.status,
        "session_key": event.session_key,
        "agent_id": event.agent_id,
        "replayed": event.replayed,
        "replay_attempt": event.attempt_count,
        "ack": True,
        "outcome": outcome,
        "details": details or {},
        "correlation": build_correlation(
            event,
            runtime_step=int((details or {}).get("runtime_step", 0) or 0),
            work_class=str((details or {}).get("work_class", "") or ""),
            replay_attempt=event.attempt_count,
        ),
    }
    record["correlation"]["ack_id"] = record["ack_id"]
    append_jsonl(base_dir, "acks.jsonl", record)
    update_recovery_event(
        base_dir,
        event.event_id,
        sidecar_ack=True,
        sidecar_ack_at=record["timestamp"],
        sidecar_ack_outcome=outcome,
        sidecar_ack_id=record["ack_id"],
    )
    return record


def claim_next_event(base_dir: str | Path) -> EventContext | None:
    recovery_path = _memory_dir(base_dir) / "recovery.json"
    recovery = _load_json(recovery_path, {"version": 1, "order": [], "events": {}})
    order = recovery.get("order", [])
    events = recovery.get("events", {})
    if not isinstance(order, list) or not isinstance(events, dict):
        return None
    for event_id in order:
        if not isinstance(event_id, str):
            continue
        record = events.get(event_id)
        if not isinstance(record, dict):
            continue
        processing_state = str(record.get("processing_state", ""))
        if processing_state not in {"queued", "failed"}:
            continue
        if not bool(record.get("replayable", True)):
            continue
        attempt_count = int(record.get("attempt_count", 0)) + 1
        replayed = attempt_count > 1 or processing_state == "failed"
        record["attempt_count"] = attempt_count
        record["processing_state"] = "processing"
        record["updated_at"] = now_iso()
        events[event_id] = record
        save_json(recovery_path, recovery)
        return event_context_from_record(record, replayed=replayed)
    return None


def mark_event_failed(base_dir: str | Path, event: EventContext, reason: str, *, replayable: bool = True) -> None:
    append_commit_record(
        base_dir,
        event=event,
        outcome="failed",
        failure_reason=reason,
    )
    update_recovery_event(
        base_dir,
        event.event_id,
        processing_state="failed",
        failure_reason=reason,
        replayable=replayable,
    )


def mark_event_acked(
    base_dir: str | Path,
    event: EventContext,
    *,
    ack_id: str,
    runtime_step: int,
    outcome: str,
) -> None:
    append_commit_record(
        base_dir,
        event=event,
        outcome="acked",
        ack_id=ack_id,
        runtime_step=runtime_step,
    )
    update_recovery_event(
        base_dir,
        event.event_id,
        processing_state="acked",
        replayable=False,
        ack_id=ack_id,
        ack_outcome=outcome,
        runtime_step=runtime_step,
    )


def _last_matching_record(records: list[dict[str, Any]], key: str, value: Any) -> dict[str, Any] | None:
    for record in reversed(records):
        if record.get(key) == value:
            return record
    return None


def get_queue_status(base_dir: str | Path) -> dict[str, Any]:
    recovery = _load_json(_memory_dir(base_dir) / "recovery.json", {"events": {}})
    events = recovery.get("events", {})
    if not isinstance(events, dict):
        events = {}
    counts = {"queued": 0, "processing": 0, "acked": 0, "failed": 0, "replayable": 0}
    for record in events.values():
        if not isinstance(record, dict):
            continue
        state = str(record.get("processing_state", ""))
        if state in counts:
            counts[state] += 1
        if bool(record.get("replayable", False)):
            counts["replayable"] += 1
    ack_records = iter_jsonl(_jsonl_path(base_dir, "acks.jsonl"))
    trace_records = iter_jsonl(_jsonl_path(base_dir, "traces.jsonl"))
    recent_ack = ack_records[-1] if ack_records else {}
    recent_failed = _last_matching_record(list(events.values()), "processing_state", "failed") or {}
    recent_trace = trace_records[-1] if trace_records else {}
    return {
        "memory_root": str(base_dir),
        "queue_path": str(_jsonl_path(base_dir, "events.jsonl")),
        **counts,
        "recent_ack_event_id": str(recent_ack.get("event_id", "")),
        "recent_failed_event_id": str(recent_failed.get("event_id", "")),
        "recent_trace_event_id": str(recent_trace.get("event_id", "")),
        "recent_worker_task_id": str(
            recent_ack.get("correlation", {}).get("worker_task_id")
            or recent_trace.get("correlation", {}).get("worker_task_id")
            or ""
        ),
    }


def read_recent_correlated_records(base_dir: str | Path, limit: int = 5) -> list[dict[str, Any]]:
    runtime_records = _load_json(_memory_dir(base_dir) / "runtime.json", {}).get("records", [])
    if not isinstance(runtime_records, list):
        runtime_records = []
    traces = iter_jsonl(_jsonl_path(base_dir, "traces.jsonl"))
    acks = iter_jsonl(_jsonl_path(base_dir, "acks.jsonl"))
    commits = iter_jsonl(_jsonl_path(base_dir, "commits.jsonl"))
    recovery = _load_json(_memory_dir(base_dir) / "recovery.json", {"events": {}})
    recovery_events = recovery.get("events", {}) if isinstance(recovery, dict) else {}
    if not isinstance(recovery_events, dict):
        recovery_events = {}

    correlated: list[dict[str, Any]] = []
    for runtime_record in reversed(runtime_records):
        if not isinstance(runtime_record, dict):
            continue
        event_id = str(runtime_record.get("event_id", "")).strip()
        if not event_id:
            continue
        correlated.append(
            {
                "event_id": event_id,
                "request_id": str(runtime_record.get("request_id", "")),
                "runtime_step": int(runtime_record.get("step", 0) or 0),
                "work_class": str(runtime_record.get("work_class", "")),
                "worker_task_id": str(runtime_record.get("worker_task_id", "")),
                "runtime": runtime_record,
                "ack": _last_matching_record(acks, "event_id", event_id) or {},
                "commit": _last_matching_record(commits, "event_id", event_id) or {},
                "trace": _last_matching_record(traces, "event_id", event_id) or {},
                "recovery": recovery_events.get(event_id, {}),
            }
        )
        if len(correlated) >= max(1, limit):
            break
    return correlated
