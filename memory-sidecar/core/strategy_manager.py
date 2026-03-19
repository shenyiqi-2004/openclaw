from __future__ import annotations

from typing import Any

from core.utils import clamp

RECENCY_BONUS = 0.03
FORCE_NEW_PENALTY = 0.5


def select_best_strategy(
    strategy_data: dict[str, Any],
    current_step: str = "",
    last_strategy: str | None = None,
    force_new: bool = False,
    step_count: int = 0,
) -> dict[str, Any]:
    strategies = strategy_data.get("strategies", [])
    chosen: dict[str, Any] | None = None
    chosen_score = -1.0
    lowered = current_step.lower()

    for strategy in strategies:
        name = strategy.get("name", "")
        score = float(strategy.get("score", 0.0))
        recency_gap = max(step_count - int(strategy.get("last_used_step", 0)), 0)
        score += min(recency_gap, 3) * RECENCY_BONUS
        if "repeat" in lowered or "failure" in lowered:
            if name == "fallback_simplify":
                score += 0.3
        elif any(word in lowered for word in ("build", "implement", "create")):
            if name == "direct_execution":
                score += 0.2
        else:
            if name == "decompose_task":
                score += 0.1

        if force_new and name == last_strategy:
            score -= FORCE_NEW_PENALTY

        if score > chosen_score:
            chosen = strategy
            chosen_score = score

    if chosen is None and strategies:
        chosen = strategies[0]
    if chosen is None:
        chosen = {"name": "direct_execution", "score": 1.0, "usage": 0, "last_used_step": 0}

    chosen["usage"] = int(chosen.get("usage", 0)) + 1
    chosen["last_used_step"] = step_count
    return chosen


def update_strategy_score(strategy_data: dict[str, Any], strategy_name: str, success: bool) -> None:
    for strategy in strategy_data.get("strategies", []):
        if strategy.get("name") == strategy_name:
            delta = 0.1 if success else -0.2
            strategy["score"] = clamp(float(strategy.get("score", 0.0)) + delta, 0.1, 3.0)
            return
