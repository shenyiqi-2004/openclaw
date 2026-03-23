from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.backends import resolve_memory_backend
from core.cleaner import clean_partition, light_compress_summary, needs_cleaning
from core.events import (
    EventContext,
    ack_event,
    append_trace,
    get_recovery_event,
    has_ack,
    load_event_context,
    mark_event_acked,
    runtime_has_event,
    update_recovery_event,
)
from core.executor import build_context, detect_repetition, execute_step
from core.memory_manager import MemoryManager
from core.orchestration import (
    build_recall_plan,
    build_runtime_signals,
    build_trace_payload,
    select_memory_identifiers,
    select_mode_from_signals,
    should_allow_memory_write,
    should_run_cleanup,
    should_run_reflection,
    should_run_selfcheck,
)
from core.reflection_manager import generate_reflection_insight, store_reflection
from core.retriever import (
    mark_retrieval_used,
    rebuild_index,
    retrieval_allowed,
    reuse_cached_results,
    touch_retrieved_items,
)
from core.router import select_partition
from core.runtime_paths import describe_memory_root, resolve_memory_root
from core.selfcheck_manager import (
    apply_safe_patch_proposals,
    evaluate_health,
    generate_optimization_suggestions,
    generate_patch_proposals,
    patch_apply_enabled,
    run_self_check,
    select_mode,
    store_selfcheck,
    update_no_benefit_patch_state,
)
from core.strategy_manager import select_best_strategy, update_strategy_score
from core.utils import compact_step_label, now_iso


def _append_if_new(
    manager: MemoryManager,
    summary: dict,
    section: str,
    text: str,
    recent_window: int = 5,
) -> bool:
    cleaned = str(text).strip()
    if not cleaned:
        return False
    generic_entries = {
        "Review results and continue with the next minimal improvement",
        "Completed step: Review results and continue with the next minimal improvement",
    }
    if cleaned in generic_entries:
        return False
    recent = summary.get(section, [])[-recent_window:]
    if cleaned in recent:
        return False
    summary.setdefault(section, []).append(cleaned)
    return True


def print_summary(base_dir: str | Path | None = None) -> None:
    status = describe_memory_root(base_dir)
    print(f"Memory root: {status.memory_root}")
    print(f"Runtime root: {status.runtime_root}")
    print(f"Root source: {status.source}")
    print(f"Deprecated root: {status.deprecated}")
    print("File tree:")
    for path in [
        "AGENTS.md",
        "main.py",
        "core/memory_manager.py",
        "core/strategy_manager.py",
        "core/router.py",
        "core/retriever.py",
        "core/reflection_manager.py",
        "core/cleaner.py",
        "core/executor.py",
        "core/selfcheck_manager.py",
        "core/events.py",
        "core/cycle.py",
        "core/worker.py",
        "core/signals.py",
        "core/runtime_paths.py",
        "memory/working.json",
        "memory/summary.json",
        "memory/strategy.json",
        "memory/reflection.json",
        "memory/selfcheck.json",
        "memory/runtime.json",
        "memory/events.jsonl",
        "memory/acks.jsonl",
        "memory/commits.jsonl",
        "memory/traces.jsonl",
        "memory/recovery.json",
    ]:
        print(f"- {path}")


def run_single_cycle(
    base_dir: str | Path | None = None,
    *,
    event: EventContext | None = None,
    print_output: bool = True,
) -> dict[str, Any]:
    root = resolve_memory_root(base_dir)
    manager = MemoryManager(root)
    manager.initialize()
    active_event = event or load_event_context()

    working = manager.load_working()
    summary = manager.load_summary()
    strategy_data = manager.load_strategy()
    reflection_data = manager.load_reflection()
    selfcheck_data = manager.load_selfcheck()
    runtime_data = manager.load_runtime()
    meta = manager.load_meta()
    event_attempt_count = active_event.attempt_count if active_event is not None else 0

    if active_event is not None:
        recovery_event = get_recovery_event(root, active_event.event_id) or {}
        event_attempt_count = int(recovery_event.get("attempt_count", active_event.attempt_count or 0))
        append_trace(
            root,
            event=active_event,
            action="sidecar_run_started",
            attempt_count=event_attempt_count,
            replay_attempt=event_attempt_count,
        )
        already_applied = has_ack(root, active_event.event_id) or runtime_has_event(
            runtime_data,
            active_event.event_id,
        )
        if already_applied:
            ack_record = ack_event(
                root,
                active_event,
                outcome="duplicate_noop",
                details={"reason": "event already applied", "attempt_count": event_attempt_count},
            )
            mark_event_acked(
                root,
                active_event,
                ack_id=str(ack_record.get("ack_id", "")),
                runtime_step=int(working.get("step_count", 0)),
                outcome="duplicate_noop",
            )
            append_trace(
                root,
                event=active_event,
                action="sidecar_duplicate_noop",
                attempt_count=event_attempt_count,
                replay_attempt=event_attempt_count,
                ack_id=ack_record.get("ack_id", ""),
            )
            if print_output:
                print(f"Duplicate event noop: {active_event.event_id}")
            return {
                "event_id": active_event.event_id,
                "request_id": active_event.request_id,
                "runtime_step": int(working.get("step_count", 0)),
                "ack_id": str(ack_record.get("ack_id", "")),
                "ack_outcome": "duplicate_noop",
                "memory_root": str(root),
            }

    query_text = " ".join(
        part
        for part in [working.get("goal", ""), working.get("focus", ""), working.get("current_step", "")]
        if part
    )
    initial_partition = select_partition(query_text)
    backend, backend_status = resolve_memory_backend(root, manager, initial_partition)
    backend_stats = backend.get_memory_stats()
    use_local_knowledge = backend_status.name == "json_snapshot"
    partition = initial_partition if use_local_knowledge else "backend-managed"
    partition_data = manager.load_partition(partition) if use_local_knowledge else {"items": [], "index": {}}
    if use_local_knowledge:
        rebuild_index(partition_data)

    repeated = detect_repetition(
        working.get("step_history", []),
        working.get("current_step", ""),
        working.get("next_action", ""),
    )
    strategy = select_best_strategy(
        strategy_data,
        current_step=working.get("current_step", ""),
        last_strategy=working.get("last_strategy"),
        force_new=repeated,
        step_count=int(working.get("step_count", 0)),
    )

    previous_mode = str(working.get("mode", "normal"))
    signals = build_runtime_signals(
        working=working,
        summary=summary,
        runtime_data=runtime_data,
        selfcheck_data=selfcheck_data,
        event=active_event,
        backend_status=backend_status,
        backend_stats=backend_stats,
        query_text=query_text,
    )
    mode = select_mode_from_signals(signals, previous_mode)

    retrieved_items: list[dict] = []
    retrieval_used = False
    recall_requested = False
    recall_reason = "not-requested"
    recall_query = query_text
    discarded_results: list[dict[str, str]] = []
    recall_plan = build_recall_plan(
        query_text=query_text,
        working=working,
        mode=mode,
        signals=signals,
        retrieval_allowed=retrieval_allowed(working),
    )
    if use_local_knowledge:
        cached_items = reuse_cached_results(partition_data, query_text, working, partition)
        if cached_items and not recall_plan["requested"]:
            cache_limit = 1 if mode == "convergence" else min(3, len(cached_items))
            retrieved_items = cached_items[:cache_limit]
            recall_reason = "reused-cached-results"
            if len(cached_items) > cache_limit:
                discarded_results.append(
                    {"reason": "limited-by-signal-plan", "count": str(len(cached_items) - cache_limit)}
                )
            touch_retrieved_items(retrieved_items, int(working.get("step_count", 0)))
        elif recall_plan["requested"]:
            recall_requested = True
            recall_reason = str(recall_plan["reason"])
            retrieved_items = backend.recall_memory(
                query=query_text,
                scope={"step_count": int(working.get("step_count", 0)), "partition": partition},
                limit=int(recall_plan["limit"]),
            )
            retrieval_used = True
        else:
            recall_reason = str(recall_plan["reason"])
    elif recall_plan["requested"]:
        recall_requested = True
        recall_reason = str(recall_plan["reason"])
        retrieved_items = backend.recall_memory(
            query=query_text,
            scope={"step_count": int(working.get("step_count", 0)), "partition": partition},
            limit=int(recall_plan["limit"]),
        )
        if not retrieved_items:
            discarded_results.append({"reason": "backend-returned-no-memories", "count": "0"})
    else:
        recall_reason = str(recall_plan["reason"])

    working["last_result_keys"] = [item.get("key", "") for item in retrieved_items[:5]]
    working["last_query"] = query_text
    working["last_memory_backend"] = backend_status.name
    working["last_memory_backend_mode"] = backend_status.mode
    working["last_memory_backend_reason"] = backend_status.reason
    working["last_recall_requested"] = recall_requested
    working["mode"] = mode

    context = build_context(working, strategy, summary, reflection_data, retrieved_items, meta)
    result = execute_step(context)

    old_current_step = working.get("current_step", "")
    next_step = result["decision"] or "Review results and continue with the next minimal improvement"
    working["step_history"] = (
        working.get("step_history", []) + [compact_step_label(old_current_step or next_step)]
    )[-20:]
    working["step_count"] = int(working.get("step_count", 0)) + 1
    working["last_action"] = old_current_step
    working["current_step"] = next_step
    working["next_action"] = "Review results and continue with the next minimal improvement"
    working["last_partition"] = partition
    working["last_strategy"] = strategy.get("name", "direct_execution")
    if retrieval_used:
        mark_retrieval_used(working)

    _append_if_new(manager, summary, "progress", result["output"])
    _append_if_new(manager, summary, "decisions", result["decision"])
    allow_memory_write, memory_write_reason = should_allow_memory_write(mode=mode, signals=signals)
    write_result = {"stored": False, "reason": "no-new-fact"}
    if result.get("new_fact") and allow_memory_write:
        _append_if_new(manager, summary, "facts", result["new_fact"])
        write_result = backend.store_memory(
            text=result["new_fact"],
            metadata={
                "tags": [initial_partition, str(working.get("focus", "")), compact_step_label(next_step)],
                "importance": 0.6,
                "step_count": int(working["step_count"]),
                "working": working,
            },
        )
        if use_local_knowledge and write_result.get("stored"):
            working = manager.load_working()
            partition_data = manager.load_partition(partition)
    elif result.get("new_fact"):
        write_result = {"stored": False, "reason": memory_write_reason}
    if result.get("failure"):
        latest_failures = summary.setdefault("failures", [])
        latest_failures.append(result["failure"])
        summary["failures"] = latest_failures[-50:]

    update_strategy_score(strategy_data, working["last_strategy"], bool(result.get("success", False)))

    reflection_triggered, reflection_reason = should_run_reflection(signals)
    if reflection_triggered:
        insight = generate_reflection_insight(working, manager.load_summary(), signals=signals.to_dict())
        store_reflection(reflection_data, insight)

    latest_summary = summary
    cleanup_triggered, cleanup_reason = should_run_cleanup(
        use_local_knowledge=use_local_knowledge,
        signals=signals,
        needs_cleaning=needs_cleaning(partition_data) if use_local_knowledge else False,
    )
    if cleanup_triggered:
        partition_data = clean_partition(partition_data, int(working["step_count"]))
    elif use_local_knowledge:
        rebuild_index(partition_data)

    selfcheck_triggered, selfcheck_reason = should_run_selfcheck(signals)
    if selfcheck_triggered:
        latest_summary = light_compress_summary(latest_summary, aggressive=mode == "convergence")

    suggestions: list[str] = []
    proposals: list[dict] = []
    applied_patches: list[dict] = []
    patch_apply_enabled_flag = patch_apply_enabled(working)
    patch_apply_attempted = False
    patch_applied = False
    patch_failure_reason = ""
    health_report = {
        "health": float(signals.health.health),
        "delta": float(signals.health.delta),
        "pressure": float(signals.health.pressure),
        "noise": float(signals.health.noise),
        "complexity": float(signals.health.complexity),
    }
    if selfcheck_triggered:
        partition_map = (
            {name: manager.load_partition(name) for name in ("programming", "science", "finance", "general")}
            if use_local_knowledge
            else {name: {"items": [], "index": {}} for name in ("programming", "science", "finance", "general")}
        )
        check_report = run_self_check(working, latest_summary, strategy_data, reflection_data, partition_map)
        previous_eval = selfcheck_data.get("evaluations", [])[-1] if selfcheck_data.get("evaluations") else None
        health_report = evaluate_health(check_report, previous_eval)
        update_no_benefit_patch_state(working, selfcheck_data, health_report)
        working["mode"] = select_mode(health_report, check_report, mode)
        suggestions = generate_optimization_suggestions(check_report, health_report, working, max_suggestions=2)
        if suggestions:
            working["recent_suggestion_steps"] = (
                working.get("recent_suggestion_steps", []) + [int(working["step_count"])]
            )[-10:]
        skip_evolution = os.environ.get("OPENCLAW_SKIP_EVOLUTION") == "1" or working.get("mode") == "convergence"
        proposals = [] if skip_evolution else generate_patch_proposals(check_report, health_report, working, root)
        if proposals:
            append_trace(
                root,
                event=active_event,
                action="sidecar_patch_proposals",
                proposal_count=len(proposals),
                proposals=proposals,
                replay_attempt=event_attempt_count,
            )
        apply_result = (
            {
                "enabled": patch_apply_enabled_flag,
                "attempted": False,
                "applied": False,
                "applied_patches": [],
                "reason": "patch-apply-skipped" if proposals else "",
            }
            if skip_evolution
            else apply_safe_patch_proposals(root, proposals, working)
        )
        patch_apply_enabled_flag = bool(apply_result.get("enabled", patch_apply_enabled_flag))
        patch_apply_attempted = bool(apply_result.get("attempted", False))
        patch_applied = bool(apply_result.get("applied", False))
        applied_patches = list(apply_result.get("applied_patches", []))
        patch_failure_reason = str(apply_result.get("reason", ""))
        if proposals or patch_apply_attempted or patch_failure_reason:
            append_trace(
                root,
                event=active_event,
                action="sidecar_patch_apply",
                enabled=patch_apply_enabled_flag,
                attempted=patch_apply_attempted,
                applied=patch_applied,
                failure_reason=patch_failure_reason,
                applied_patches=applied_patches,
                replay_attempt=event_attempt_count,
            )
        selfcheck_data = store_selfcheck(
            selfcheck_data,
            check_report,
            health_report,
            suggestions,
            proposals,
            applied_patches,
        )
        working["last_health"] = health_report["health"]
    else:
        working["mode"] = mode
        working["last_health"] = health_report["health"]

    if active_event is not None:
        working["last_event_id"] = active_event.event_id
        working["last_request_id"] = active_event.request_id
    manager.save_working(working)
    manager.save_summary(latest_summary)
    manager.save_strategy(strategy_data)
    manager.save_reflection(reflection_data)
    manager.save_selfcheck(selfcheck_data)

    total_knowledge_count = (
        sum(len(manager.load_partition(name).get("items", [])) for name in ("programming", "science", "finance", "general"))
        if use_local_knowledge
        else 0
    )
    total_summary_count = sum(len(value) for value in latest_summary.values() if isinstance(value, list))
    reflection_count = len(reflection_data.get("insights", []))
    runtime_record = {
        "step": int(working["step_count"]),
        "mode": working.get("mode", "normal"),
        "partition": partition,
        "strategy": working.get("last_strategy", ""),
        "health": float(working.get("last_health", 1.0)),
        "health_delta": float(health_report.get("delta", 0.0)),
        "pressure": float(health_report.get("pressure", 0.0)),
        "noise": float(health_report.get("noise", 0.0)),
        "complexity": float(health_report.get("complexity", 0.0)),
        "knowledge_count": total_knowledge_count,
        "summary_count": total_summary_count,
        "reflection_count": reflection_count,
        "selfcheck_triggered": selfcheck_triggered,
        "reflection_triggered": reflection_triggered,
        "cleaner_triggered": cleanup_triggered,
        "memory_backend": backend_status.name,
        "memory_backend_mode": backend_status.mode,
        "memory_backend_reason": backend_status.reason,
        "memory_backend_available": backend_status.available,
        "memory_backend_canonical": backend_status.canonical,
        "memory_backend_identity": backend.get_backend_identity(),
        "recall_requested": recall_requested,
        "recall_reason": recall_reason,
        "retrieved_count": len(retrieved_items[:5]),
        "selected_memory_ids": select_memory_identifiers(retrieved_items[:5]),
        "memory_write_stored": bool(write_result.get("stored", False)),
        "memory_write_reason": str(write_result.get("reason", "")),
        "result_success": bool(result.get("success", False)),
        "result_failure": str(result.get("failure", "")),
        "backend_stats": backend_stats,
        "event_id": active_event.event_id if active_event is not None else "",
        "request_id": active_event.request_id if active_event is not None else "",
        "replayed": active_event.replayed if active_event is not None else False,
        "replay_attempt": event_attempt_count,
        "event_attempt_count": event_attempt_count,
        "timestamp": now_iso(),
    }
    records = runtime_data.setdefault("records", [])
    records.append(runtime_record)
    runtime_data["records"] = records[-50:]
    manager.save_runtime(runtime_data)
    if use_local_knowledge:
        manager.save_partition(partition, partition_data)

    append_trace(
        root,
        event=active_event,
        action="sidecar_orchestration_trace",
        trigger_source=active_event.source if active_event is not None else "manual",
        replayed=active_event.replayed if active_event is not None else False,
        **build_trace_payload(
            recall_requested=recall_requested,
            recall_reason=recall_reason,
            recall_query=recall_query,
            recall_limit=int(recall_plan.get("limit", 0)),
            retrieved_items=retrieved_items[:5],
            discarded_results=discarded_results
            or (
                [{"reason": "selection-filtering-owned-by-backend", "count": "unknown"}]
                if backend_status.canonical and recall_requested and retrieved_items
                else []
            ),
            health_report=health_report,
            current_mode=working.get("mode", "normal"),
            selected_strategy=working.get("last_strategy", ""),
            reflection_triggered=reflection_triggered,
            reflection_reason=reflection_reason,
            selfcheck_triggered=selfcheck_triggered,
            selfcheck_reason=selfcheck_reason,
            cleanup_triggered=cleanup_triggered,
            cleanup_reason=cleanup_reason,
            memory_write_allowed=allow_memory_write,
            memory_write_reason=str(write_result.get("reason", memory_write_reason)),
            patch_proposals=proposals,
            patch_apply_enabled=patch_apply_enabled_flag,
            patch_apply_attempted=patch_apply_attempted,
            patch_applied=patch_applied,
            patch_failure_reason=patch_failure_reason,
            outcome="success" if bool(result.get("success", False)) else "partial",
            failure_reason=str(result.get("failure", "")),
            active_signals=signals.active_reasons,
            memory_backend=backend_status.name,
            request_id=active_event.request_id if active_event is not None else "",
            runtime_step=int(working["step_count"]),
            replay_attempt=event_attempt_count,
            ack_id="",
        ),
    )

    ack_id = ""
    ack_outcome = ""
    if active_event is not None:
        ack_record = ack_event(
            root,
            active_event,
            outcome="applied",
            details={
                "attempt_count": event_attempt_count,
                "step": int(working["step_count"]),
                "memory_backend": backend_status.name,
                "runtime_step": int(working["step_count"]),
            },
        )
        ack_id = str(ack_record.get("ack_id", ""))
        ack_outcome = str(ack_record.get("outcome", ""))
        mark_event_acked(
            root,
            active_event,
            ack_id=ack_id,
            runtime_step=int(working["step_count"]),
            outcome=ack_outcome,
        )
        update_recovery_event(
            root,
            active_event.event_id,
            sidecar_runtime_step=int(working["step_count"]),
            sidecar_runtime_event_id=active_event.event_id,
        )
        runtime_data["records"][-1]["ack_id"] = ack_id
        runtime_data["records"][-1]["ack_outcome"] = ack_outcome
        manager.save_runtime(runtime_data)
        append_trace(
            root,
            event=active_event,
            action="sidecar_ack_written",
            attempt_count=event_attempt_count,
            replay_attempt=event_attempt_count,
            runtime_step=int(working["step_count"]),
            ack_id=ack_id,
            memory_backend=backend_status.name,
        )

    if print_output:
        print(f"Execution result: {result['output']}")
        print(f"Current step: {working['current_step']}")
        print(f"Step count: {working['step_count']}")
        print(f"Partition: {partition}")
        print(f"Retrieved items: {len(retrieved_items[:5])}")
        print(f"Memory backend: {backend_status.name} ({backend_status.mode})")
        print(f"Health: {health_report['health']}")
        print(f"Mode: {working.get('mode', 'normal')}")
        print(f"Suggestions: {suggestions if suggestions else []}")
        print(f"Proposals: {proposals if proposals else []}")
        print(f"Patch applied: {patch_applied}")
        print()
        print_summary(root)

    return {
        "event_id": active_event.event_id if active_event is not None else "",
        "request_id": active_event.request_id if active_event is not None else "",
        "runtime_step": int(working["step_count"]),
        "ack_id": ack_id,
        "ack_outcome": ack_outcome,
        "memory_root": str(root),
        "memory_backend": backend_status.name,
    }
