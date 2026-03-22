from __future__ import annotations

from typing import Any


def _recent_records(runtime_data: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    return [record for record in runtime_data.get("records", []) if isinstance(record, dict)][-limit:]


def _recent_health(selfcheck_data: dict[str, Any], working: dict[str, Any]) -> dict[str, float]:
    evaluations = [item for item in selfcheck_data.get("evaluations", []) if isinstance(item, dict)]
    if evaluations:
        latest = evaluations[-1]
        return {
            "health": float(latest.get("health", working.get("last_health", 1.0))),
            "delta": float(latest.get("delta", 0.0)),
            "pressure": float(latest.get("pressure", 0.0)),
            "noise": float(latest.get("noise", 0.0)),
            "complexity": float(latest.get("complexity", 0.0)),
        }
    return {
        "health": float(working.get("last_health", 1.0)),
        "delta": 0.0,
        "pressure": 0.0,
        "noise": 0.0,
        "complexity": 0.0,
    }


def build_runtime_signals(
    *,
    working: dict[str, Any],
    summary: dict[str, Any],
    runtime_data: dict[str, Any],
    selfcheck_data: dict[str, Any],
    event: Any | None,
    backend_status: Any,
    backend_stats: dict[str, Any],
    query_text: str,
) -> dict[str, Any]:
    recent_records = _recent_records(runtime_data, 6)
    recent_history = [str(item) for item in working.get("step_history", [])[-4:] if str(item).strip()]
    recent_failures = [str(item) for item in summary.get("failures", [])[-3:] if str(item).strip()]
    current_health = _recent_health(selfcheck_data, working)

    repeated_steps = len(recent_history) >= 3 and len(set(recent_history[-3:])) <= 2
    contradiction = any(
        token in " ".join(recent_failures[-2:]).lower()
        for token in ("contradict", "conflict", "inconsistent", "undo", "revert")
    )
    consecutive_failures = sum(1 for record in recent_records[-3:] if not bool(record.get("result_success", True))) >= 2
    rapid_health_drop = current_health["delta"] <= -0.05
    interruption_recovery = bool(event.replayed) if event is not None else False

    low_health = current_health["health"] < 0.8
    high_pressure = current_health["pressure"] >= 0.2
    high_noise = current_health["noise"] >= 0.2
    low_yield_recall = sum(
        1
        for record in recent_records[-3:]
        if bool(record.get("recall_requested")) and int(record.get("retrieved_count", 0)) <= 0
    ) >= 2

    abnormal_growth = False
    if len(recent_records) >= 2:
        previous = recent_records[-2]
        latest = recent_records[-1]
        summary_growth = int(latest.get("summary_count", 0)) - int(previous.get("summary_count", 0))
        knowledge_growth = int(latest.get("knowledge_count", 0)) - int(previous.get("knowledge_count", 0))
        abnormal_growth = summary_growth >= 6 or knowledge_growth >= 4

    signals = {
        "query_present": bool(query_text.strip()),
        "repeated_steps": repeated_steps,
        "contradiction": contradiction,
        "consecutive_failures": consecutive_failures,
        "rapid_health_drop": rapid_health_drop,
        "interruption_recovery": interruption_recovery,
        "low_health": low_health,
        "high_pressure": high_pressure,
        "high_noise": high_noise,
        "abnormal_growth": abnormal_growth,
        "low_yield_recall": low_yield_recall,
        "has_recent_memory": bool(working.get("last_result_keys")),
        "canonical_backend": bool(getattr(backend_status, "canonical", False)),
        "backend_name": str(getattr(backend_status, "name", "")),
        "backend_stats": backend_stats,
        "health": current_health,
    }
    reasons = [name for name, value in signals.items() if isinstance(value, bool) and value]
    signals["active_reasons"] = reasons
    return signals


def select_mode_from_signals(signals: dict[str, Any], current_mode: str) -> str:
    if signals["low_health"] and (signals["high_pressure"] or signals["high_noise"] or signals["abnormal_growth"]):
        return "convergence"
    if signals["high_pressure"] and signals["abnormal_growth"]:
        return "convergence"
    if (
        signals["repeated_steps"]
        or signals["consecutive_failures"]
        or signals["rapid_health_drop"]
        or signals["interruption_recovery"]
        or signals["low_health"]
    ):
        return "stability"
    if current_mode == "convergence" and not signals["low_health"]:
        return "normal"
    if current_mode == "stability" and not (
        signals["repeated_steps"] or signals["consecutive_failures"] or signals["rapid_health_drop"]
    ):
        return "normal"
    return "normal"


def build_recall_plan(
    *,
    query_text: str,
    working: dict[str, Any],
    mode: str,
    signals: dict[str, Any],
    retrieval_allowed: bool,
) -> dict[str, Any]:
    if not query_text.strip():
        return {"requested": False, "reason": "empty-query", "limit": 0}
    if not retrieval_allowed:
        return {"requested": False, "reason": "retrieval-cooldown", "limit": 0}

    strong_signals = [
        name
        for name in (
            "repeated_steps",
            "contradiction",
            "consecutive_failures",
            "rapid_health_drop",
            "interruption_recovery",
        )
        if signals.get(name)
    ]
    should_recall = bool(strong_signals) or not signals.get("has_recent_memory") or mode == "normal"
    if signals.get("low_yield_recall") and not strong_signals:
        return {"requested": False, "reason": "recent-low-yield-recall", "limit": 0}
    if mode == "convergence" and not strong_signals and signals.get("has_recent_memory"):
        return {"requested": False, "reason": "convergence-reuse-preferred", "limit": 0}
    if not should_recall:
        return {"requested": False, "reason": "no-recall-signal", "limit": 0}

    dynamic_limit = 2 + len(strong_signals)
    if mode == "stability":
        dynamic_limit = min(dynamic_limit, 3)
    elif mode == "convergence":
        dynamic_limit = min(dynamic_limit, 2)
    else:
        dynamic_limit = min(dynamic_limit, 5)
    return {
        "requested": True,
        "reason": "signal-driven:" + ",".join(strong_signals or ["default-context-refresh"]),
        "limit": max(1, dynamic_limit),
    }


def should_run_reflection(signals: dict[str, Any]) -> tuple[bool, str]:
    for name in (
        "repeated_steps",
        "contradiction",
        "consecutive_failures",
        "rapid_health_drop",
        "interruption_recovery",
    ):
        if signals.get(name):
            return True, name
    return False, "no-reflection-signal"


def should_run_selfcheck(signals: dict[str, Any]) -> tuple[bool, str]:
    for name in (
        "low_health",
        "high_pressure",
        "high_noise",
        "abnormal_growth",
        "low_yield_recall",
        "rapid_health_drop",
        "interruption_recovery",
    ):
        if signals.get(name):
            return True, name
    return False, "no-selfcheck-signal"


def should_run_cleanup(*, use_local_knowledge: bool, signals: dict[str, Any], needs_cleaning: bool) -> tuple[bool, str]:
    if not use_local_knowledge:
        return False, "backend-owned-cleanup"
    if needs_cleaning:
        return True, "local-snapshot-bloat"
    for name in ("abnormal_growth", "high_pressure", "high_noise"):
        if signals.get(name):
            return True, name
    return False, "no-cleanup-signal"


def should_allow_memory_write(*, mode: str, signals: dict[str, Any]) -> tuple[bool, str]:
    if mode == "convergence":
        return False, "convergence-mode"
    if signals.get("high_noise"):
        return False, "high-noise"
    if signals.get("abnormal_growth"):
        return False, "abnormal-growth"
    return True, "write-allowed"


def select_memory_identifiers(items: list[dict[str, Any]]) -> list[str]:
    identifiers: list[str] = []
    for item in items:
        value = str(item.get("id") or item.get("memory_id") or item.get("key") or "").strip()
        if value:
            identifiers.append(value)
    return identifiers


def build_trace_payload(
    *,
    recall_requested: bool,
    recall_reason: str,
    recall_query: str,
    recall_limit: int,
    retrieved_items: list[dict[str, Any]],
    discarded_results: list[dict[str, str]],
    health_report: dict[str, Any],
    current_mode: str,
    selected_strategy: str,
    reflection_triggered: bool,
    reflection_reason: str,
    selfcheck_triggered: bool,
    selfcheck_reason: str,
    cleanup_triggered: bool,
    cleanup_reason: str,
    memory_write_allowed: bool,
    memory_write_reason: str,
    patch_proposals: list[dict[str, Any]],
    patch_apply_enabled: bool,
    patch_apply_attempted: bool,
    patch_applied: bool,
    patch_failure_reason: str,
    outcome: str,
    failure_reason: str,
    active_signals: list[str],
    memory_backend: str,
) -> dict[str, Any]:
    return {
        "recall_requested": recall_requested,
        "recall_reason": recall_reason,
        "recall_query": recall_query,
        "recall_limit": recall_limit,
        "returned_memory_count": len(retrieved_items[:5]),
        "selected_memory_ids": select_memory_identifiers(retrieved_items[:5]),
        "discarded_results": discarded_results,
        "health": float(health_report.get("health", 1.0)),
        "pressure": float(health_report.get("pressure", 0.0)),
        "noise": float(health_report.get("noise", 0.0)),
        "complexity": float(health_report.get("complexity", 0.0)),
        "current_mode": current_mode,
        "selected_strategy": selected_strategy,
        "reflection_triggered": reflection_triggered,
        "reflection_reason": reflection_reason,
        "selfcheck_triggered": selfcheck_triggered,
        "selfcheck_reason": selfcheck_reason,
        "cleanup_triggered": cleanup_triggered,
        "cleanup_reason": cleanup_reason,
        "memory_write_allowed": memory_write_allowed,
        "memory_write_reason": memory_write_reason,
        "patch_proposal_generated": bool(patch_proposals),
        "patch_apply_enabled": patch_apply_enabled,
        "patch_apply_attempted": patch_apply_attempted,
        "patch_applied": patch_applied,
        "patch_failure_reason": patch_failure_reason,
        "outcome": outcome,
        "failure_reason": failure_reason,
        "active_signals": active_signals,
        "memory_backend": memory_backend,
    }
