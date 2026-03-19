from __future__ import annotations

import os
from pathlib import Path

from core.cleaner import clean_partition, light_compress_summary, needs_cleaning
from core.executor import build_context, detect_repetition, execute_step
from core.memory_manager import MemoryManager
from core.reflection_manager import generate_reflection_insight, should_reflect, store_reflection
from core.retriever import (
    mark_retrieval_used,
    rebuild_index,
    retrieval_allowed,
    retrieve_top_k,
    reuse_cached_results,
    touch_retrieved_items,
)
from core.router import select_partition
from core.selfcheck_manager import (
    evaluate_health,
    generate_optimization_suggestions,
    generate_patch_proposals,
    apply_safe_patch_proposals,
    run_self_check,
    select_mode,
    store_selfcheck,
    update_no_benefit_patch_state,
)
from core.strategy_manager import select_best_strategy, update_strategy_score
from core.utils import compact_step_label, now_iso


def _append_if_new(manager: MemoryManager, summary: dict, section: str, text: str, recent_window: int = 5) -> bool:
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
    manager.append_summary(section, cleaned)
    summary.setdefault(section, []).append(cleaned)
    return True


def print_summary() -> None:
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
        "core/utils.py",
        "memory/working.json",
        "memory/summary.json",
        "memory/strategy.json",
        "memory/reflection.json",
        "memory/selfcheck.json",
        "memory/runtime.json",
        "memory/meta.json",
        "memory/knowledge/programming.json",
        "memory/knowledge/science.json",
        "memory/knowledge/finance.json",
        "memory/knowledge/general.json",
    ]:
        print(f"- {path}")

    print("\nModule summary:")
    print("- utils.py: JSON helpers, normalization, and compact labels.")
    print("- memory_manager.py: file initialization and persistence.")
    print("- router.py: deterministic partition selection.")
    print("- retriever.py: lexical retrieval capped at 3 items.")
    print("- strategy_manager.py: small strategy selection and scoring.")
    print("- reflection_manager.py: every-3-step reflection handling.")
    print("- cleaner.py: light deduplication and size control.")
    print("- executor.py: builds minimal context and completes one step.")
    print("- selfcheck_manager.py: lightweight numeric health check.")
    print("- main.py: runs one full execution cycle.")

    print("\nHow to run:")
    print("- python main.py")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    manager = MemoryManager(base_dir)
    manager.initialize()

    working = manager.load_working()
    summary = manager.load_summary()
    strategy_data = manager.load_strategy()
    reflection_data = manager.load_reflection()
    selfcheck_data = manager.load_selfcheck()
    runtime_data = manager.load_runtime()
    meta = manager.load_meta()

    query_text = " ".join(
        part for part in [working.get("goal", ""), working.get("focus", ""), working.get("current_step", "")] if part
    )
    partition = select_partition(query_text)
    partition_data = manager.load_partition(partition)
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

    mode = str(working.get("mode", "normal"))
    retrieved_items = []
    retrieval_used = False
    cached_items = reuse_cached_results(partition_data, query_text, working, partition)
    if cached_items:
        retrieved_items = cached_items[:2] if mode == "convergence" else cached_items[:3]
        touch_retrieved_items(retrieved_items, int(working.get("step_count", 0)))
    elif retrieval_allowed(working) and not (mode == "stability" and int(working.get("step_count", 0)) % 2 == 1):
        top_k = 2 if mode in {"stability", "convergence"} else 3
        retrieved_items = retrieve_top_k(partition_data, query_text, k=top_k)
        touch_retrieved_items(retrieved_items, int(working.get("step_count", 0)))
        retrieval_used = True
    working["last_result_keys"] = [item.get("key", "") for item in retrieved_items[:3]]
    working["last_query"] = query_text

    context = build_context(working, strategy, summary, reflection_data, retrieved_items, meta)
    result = execute_step(context)

    old_current_step = working.get("current_step", "")
    next_step = result["decision"] or "Review results and continue with the next minimal improvement"
    working["step_history"] = (working.get("step_history", []) + [compact_step_label(old_current_step or next_step)])[-20:]
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
    allow_knowledge_write = mode != "convergence" and not (mode == "stability" and int(working["step_count"]) % 2 == 0)
    if result.get("new_fact") and allow_knowledge_write:
        _append_if_new(manager, summary, "facts", result["new_fact"])
        added_knowledge = manager.add_knowledge(
            partition,
            result["new_fact"],
            [partition, str(working.get("focus", "")), compact_step_label(next_step)],
            importance=0.6,
            current_step_count=int(working["step_count"]),
            working=working,
        )
        if added_knowledge:
            working = manager.load_working()
            partition_data = manager.load_partition(partition)
    if result.get("failure"):
        manager.append_summary("failures", result["failure"])

    update_strategy_score(strategy_data, working["last_strategy"], bool(result.get("success", False)))

    if should_reflect(int(working["step_count"])):
        insight = generate_reflection_insight(working, manager.load_summary())
        store_reflection(reflection_data, insight)

    latest_summary = manager.load_summary()
    maintenance_due = int(working["step_count"]) % 5 == 0
    should_clean = needs_cleaning(partition_data) or mode in {"stability", "convergence"}
    if should_clean:
        partition_data = clean_partition(partition_data, int(working["step_count"]))
    else:
        rebuild_index(partition_data)
    if maintenance_due:
        latest_summary = light_compress_summary(latest_summary, aggressive=mode == "convergence")

    suggestions: list[str] = []
    proposals: list[dict] = []
    applied_patches: list[dict] = []
    patch_applied = False
    health_report = {
        "health": float(working.get("last_health", 1.0)),
        "delta": 0.0,
        "pressure": 0.0,
        "noise": 0.0,
        "complexity": 0.0,
    }
    if maintenance_due:
        partition_map = {name: manager.load_partition(name) for name in ("programming", "science", "finance", "general")}
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
        proposals = [] if skip_evolution else generate_patch_proposals(check_report, health_report, working, base_dir)
        patch_applied, applied_patches = (False, []) if skip_evolution else apply_safe_patch_proposals(base_dir, proposals, working)
        selfcheck_data = store_selfcheck(selfcheck_data, check_report, health_report, suggestions, proposals, applied_patches)
        working["last_health"] = health_report["health"]
    else:
        working["mode"] = mode


    manager.save_working(working)
    manager.save_summary(latest_summary)
    manager.save_strategy(strategy_data)
    manager.save_reflection(reflection_data)
    manager.save_selfcheck(selfcheck_data)
    total_knowledge_count = sum(
        len(manager.load_partition(name).get("items", []))
        for name in ("programming", "science", "finance", "general")
    )
    total_summary_count = sum(len(value) for value in latest_summary.values() if isinstance(value, list))
    reflection_count = len(reflection_data.get("insights", []))
    runtime_record = {
        "step": int(working["step_count"]),
        "mode": working.get("mode", "normal"),
        "partition": partition,
        "strategy": working.get("last_strategy", ""),
        "health": float(working.get("last_health", 1.0)),
        "knowledge_count": total_knowledge_count,
        "summary_count": total_summary_count,
        "reflection_count": reflection_count,
        "selfcheck_triggered": maintenance_due,
        "cleaner_triggered": should_clean,
        "timestamp": now_iso(),
    }
    records = runtime_data.setdefault("records", [])
    records.append(runtime_record)
    runtime_data["records"] = records[-50:]
    manager.save_runtime(runtime_data)
    manager.save_partition(partition, partition_data)

    print(f"Execution result: {result['output']}")
    print(f"Current step: {working['current_step']}")
    print(f"Step count: {working['step_count']}")
    print(f"Partition: {partition}")
    print(f"Retrieved items: {len(retrieved_items[:3])}")
    print(f"Health: {health_report['health']}")
    print(f"Mode: {working.get('mode', 'normal')}")
    print(f"Suggestions: {suggestions if suggestions else []}")
    print(f"Proposals: {proposals if proposals else []}")
    print(f"Patch applied: {patch_applied}")
    print()
    print_summary()


if __name__ == "__main__":
    main()
