from __future__ import annotations

import unittest

from core.backends.base import BackendStatus
from core.orchestration import (
    build_recall_plan,
    build_runtime_signals,
    select_mode_from_signals,
    should_run_reflection,
    should_run_selfcheck,
)


class OrchestrationTests(unittest.TestCase):
    def test_recovery_and_repeat_signals_trigger_reflection_and_selfcheck(self) -> None:
        signals = build_runtime_signals(
            working={
                "step_history": ["plan", "plan", "plan"],
                "last_health": 0.78,
                "last_result_keys": [],
            },
            summary={"failures": []},
            runtime_data={"records": []},
            selfcheck_data={"evaluations": [{"health": 0.78, "delta": -0.06, "pressure": 0.1, "noise": 0.0, "complexity": 0.1}]},
            event=type("Event", (), {"replayed": True})(),
            backend_status=BackendStatus("memory_lancedb_pro", True, True, "bridge", ""),
            backend_stats={},
            query_text="continue previous task",
        )
        self.assertTrue(signals["repeated_steps"])
        self.assertTrue(signals["interruption_recovery"])
        self.assertTrue(should_run_reflection(signals)[0])
        self.assertTrue(should_run_selfcheck(signals)[0])
        self.assertEqual(select_mode_from_signals(signals, "normal"), "stability")

    def test_low_yield_recall_suppresses_default_recall(self) -> None:
        signals = build_runtime_signals(
            working={
                "step_history": ["a", "b"],
                "last_health": 0.92,
                "last_result_keys": ["m1"],
            },
            summary={"failures": []},
            runtime_data={
                "records": [
                    {"recall_requested": True, "retrieved_count": 0, "result_success": True},
                    {"recall_requested": True, "retrieved_count": 0, "result_success": True},
                ]
            },
            selfcheck_data={"evaluations": []},
            event=None,
            backend_status=BackendStatus("memory_lancedb_pro", True, True, "bridge", ""),
            backend_stats={},
            query_text="steady context",
        )
        plan = build_recall_plan(
            query_text="steady context",
            working={"step_count": 4},
            mode="normal",
            signals=signals,
            retrieval_allowed=True,
        )
        self.assertFalse(plan["requested"])
        self.assertEqual(plan["reason"], "recent-low-yield-recall")

    def test_strong_signals_expand_recall_limit(self) -> None:
        signals = {
            "repeated_steps": True,
            "contradiction": True,
            "consecutive_failures": True,
            "rapid_health_drop": False,
            "interruption_recovery": False,
            "low_yield_recall": False,
            "has_recent_memory": False,
        }
        plan = build_recall_plan(
            query_text="resolve conflicting memory state",
            working={"step_count": 9},
            mode="normal",
            signals=signals,
            retrieval_allowed=True,
        )
        self.assertTrue(plan["requested"])
        self.assertGreaterEqual(plan["limit"], 4)


if __name__ == "__main__":
    unittest.main()
