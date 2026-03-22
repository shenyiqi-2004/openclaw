from __future__ import annotations

from core.utils import compact_step_label

REPETITION_WINDOW = 5
REPETITION_LIMIT = 2


def detect_repetition(step_history: list[str], current_step: str, next_action: str) -> bool:
    recent = step_history[-REPETITION_WINDOW:]
    labels = recent + [compact_step_label(current_step), compact_step_label(next_action)]
    target = labels[-2]
    return labels.count(target) >= REPETITION_LIMIT


def build_context(
    working: dict,
    strategy: dict,
    summary: dict,
    reflections: dict,
    retrieved_items: list[dict],
    meta: dict,
) -> dict:
    return {
        "goal": working.get("goal", ""),
        "current_step": working.get("current_step", ""),
        "next_action": working.get("next_action", ""),
        "focus": working.get("focus", ""),
        "strategy": strategy.get("name", "direct_execution"),
        "recent_failures": summary.get("failures", [])[-3:],
        "reflections": reflections.get("insights", [])[-3:],
        "retrieved": [item.get("content", "") for item in retrieved_items[:3]],
        "rules": [rule.get("rule", "") for rule in meta.get("rules", [])[:3]],
    }


def execute_step(context: dict) -> dict:
    current_step = str(context.get("current_step", "")).strip()
    next_action = str(context.get("next_action", "")).strip()

    if not current_step:
        return {
            "success": True,
            "output": "Initialized the minimal memory kernel.",
            "new_fact": "A small deterministic memory loop is easier to keep stable.",
            "decision": "Start from the simplest valid next action.",
            "failure": "",
        }

    return {
        "success": True,
        "output": f"Completed step: {current_step}",
        "new_fact": "",
        "decision": next_action or "Review results and continue with the next minimal improvement",
        "failure": "",
    }
