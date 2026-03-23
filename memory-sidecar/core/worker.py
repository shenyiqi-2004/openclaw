from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from core.cycle import run_single_cycle
from core.events import append_trace, claim_next_event, get_queue_status, mark_event_failed
from core.runtime_paths import describe_memory_root, resolve_memory_root


def consume_once(base_dir: str | Path | None = None) -> dict[str, Any]:
    memory_root = resolve_memory_root(base_dir)
    event = claim_next_event(memory_root)
    if event is None:
        return {
            "processed": False,
            "memory_root": str(memory_root),
            "reason": "queue-empty",
        }
    try:
        result = run_single_cycle(memory_root, event=event, print_output=False)
        return {
            "processed": True,
            "memory_root": str(memory_root),
            "event_id": event.event_id,
            "request_id": event.request_id,
            "runtime_step": result.get("runtime_step", 0),
            "ack_id": result.get("ack_id", ""),
            "ack_outcome": result.get("ack_outcome", ""),
            "replayed": event.replayed,
        }
    except Exception as exc:
        append_trace(
            memory_root,
            event=event,
            action="worker_event_failed",
            level="warn",
            reason=str(exc),
            replay_attempt=event.attempt_count,
        )
        mark_event_failed(memory_root, event, str(exc))
        raise


def worker_loop(base_dir: str | Path | None = None, poll_interval: float = 1.0) -> None:
    memory_root = resolve_memory_root(base_dir)
    status = describe_memory_root(memory_root)
    print(f"Memory root: {status.memory_root}")
    print(f"Runtime root: {status.runtime_root}")
    print(f"Root source: {status.source}")
    if status.deprecated:
        print("Warning: using deprecated memory root")
    print(f"Polling queue every {poll_interval:.1f}s")
    while True:
        result = consume_once(memory_root)
        if result.get("processed"):
            print(
                "Processed event "
                f"{result.get('event_id')} "
                f"(ack={result.get('ack_outcome')}, step={result.get('runtime_step')})"
            )
        else:
            time.sleep(max(poll_interval, 0.1))


def print_queue_status(base_dir: str | Path | None = None) -> dict[str, Any]:
    memory_root = resolve_memory_root(base_dir)
    root_status = describe_memory_root(memory_root)
    queue_status = get_queue_status(memory_root)
    print(f"Memory root: {root_status.memory_root}")
    print(f"Runtime root: {root_status.runtime_root}")
    print(f"Root source: {root_status.source}")
    print(f"Deprecated root: {root_status.deprecated}")
    print(f"Queue journal: {queue_status['queue_path']}")
    print(f"Queued: {queue_status['queued']}")
    print(f"Processing: {queue_status['processing']}")
    print(f"Acked: {queue_status['acked']}")
    print(f"Failed: {queue_status['failed']}")
    print(f"Replayable: {queue_status['replayable']}")
    print(f"Recent ack event: {queue_status.get('recent_ack_event_id', '')}")
    print(f"Recent failed event: {queue_status.get('recent_failed_event_id', '')}")
    print(f"Recent trace event: {queue_status.get('recent_trace_event_id', '')}")
    return queue_status
