from __future__ import annotations

import argparse
import json

from core.cycle import run_single_cycle
from core.events import append_trace, load_event_context, read_recent_correlated_records, update_recovery_event
from core.runtime_paths import describe_memory_root, resolve_memory_root
from core.worker import consume_once, print_queue_status, worker_loop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw memory-sidecar control entrypoint")
    parser.add_argument("--once", action="store_true", help="Consume exactly one queued event")
    parser.add_argument("--worker", action="store_true", help="Continuously poll and consume queued events")
    parser.add_argument("--queue-status", action="store_true", help="Print queue and root status")
    parser.add_argument("--print-root", action="store_true", help="Print the effective memory root")
    parser.add_argument(
        "--trace-view",
        type=int,
        nargs="?",
        const=5,
        help="Print recent correlated event/ack/trace/runtime records",
    )
    parser.add_argument("--poll-interval", type=float, default=1.0, help="Worker polling interval in seconds")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    base_dir = resolve_memory_root()

    if args.print_root:
        status = describe_memory_root(base_dir)
        print(f"Memory root: {status.memory_root}")
        print(f"Runtime root: {status.runtime_root}")
        print(f"Root source: {status.source}")
        print(f"Deprecated root: {status.deprecated}")
        return

    if args.queue_status:
        print_queue_status(base_dir)
        return

    if args.trace_view is not None:
        records = read_recent_correlated_records(base_dir, limit=max(1, int(args.trace_view)))
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return

    if args.once:
        result = consume_once(base_dir)
        if not result.get("processed"):
            print("Queue empty")
        return

    if args.worker:
        try:
            worker_loop(base_dir, poll_interval=args.poll_interval)
        except KeyboardInterrupt:
            print("Worker stopped")
        return

    run_single_cycle(base_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        base_dir = resolve_memory_root()
        event = load_event_context()
        if event is not None:
            append_trace(
                base_dir,
                event=event,
                action="sidecar_run_failed",
                level="warn",
                reason=str(exc),
                replay_attempt=event.attempt_count,
            )
            update_recovery_event(
                base_dir,
                event.event_id,
                sidecar_ack=False,
                sidecar_failure_reason=str(exc),
            )
        raise
