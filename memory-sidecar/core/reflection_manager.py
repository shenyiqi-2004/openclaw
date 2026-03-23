from __future__ import annotations

from typing import Any


def should_reflect(step_count: int | None = None, signals: dict[str, Any] | None = None) -> bool:
    if signals:
        return any(
            bool(signals.get(name))
            for name in (
                "repeated_steps",
                "contradiction",
                "consecutive_failures",
                "rapid_health_drop",
                "interruption_recovery",
            )
        )
    return bool(step_count and step_count > 0 and step_count % 3 == 0)


def generate_reflection_insight(
    working: dict[str, Any],
    summary: dict[str, Any],
    signals: dict[str, Any] | None = None,
) -> str:
    if signals:
        if signals.get("interruption_recovery"):
            return "Re-anchor on the last stable result before resuming after interruption."
        if signals.get("rapid_health_drop"):
            return "Reduce active context and verify assumptions before continuing."
        if signals.get("consecutive_failures"):
            return "Switch approach now instead of extending the same failing path."
        if signals.get("contradiction"):
            return "Resolve conflicting memory before taking the next action."
        if signals.get("repeated_steps"):
            return "Break the local loop by choosing a materially different next step."
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
