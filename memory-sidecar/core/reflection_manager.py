from __future__ import annotations

from typing import Any


def should_reflect(step_count: int) -> bool:
    return step_count > 0 and step_count % 3 == 0


def generate_reflection_insight(working: dict[str, Any], summary: dict[str, Any]) -> str:
    failures = summary.get("failures", [])[-2:]
    if failures:
        return "Simplify sooner after a failure instead of repeating the same approach."
    history = working.get("step_history", [])[-3:]
    if len(history) >= 2 and len(set(history)) < len(history):
        return "Change strategy when recent step labels start repeating."
    if working.get("next_action"):
        return "Prefer direct execution when the next action is already obvious."
    return "Keep the active context small and focused."


def store_reflection(reflection_data: dict[str, Any], insight: str, max_items: int = 20) -> None:
    text = insight.strip()
    if not text:
        return
    insights = reflection_data.setdefault("insights", [])
    if text in insights:
        return
    insights.append(text)
    reflection_data["insights"] = insights[-max_items:]
