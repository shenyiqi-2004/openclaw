from __future__ import annotations

import unittest

from core.orchestration import build_trace_payload


class TraceContractTests(unittest.TestCase):
    def test_orchestration_trace_payload_contains_required_fields(self) -> None:
        payload = build_trace_payload(
            recall_requested=True,
            recall_reason="signal-driven:repeated_steps",
            recall_query="resolve memory conflict",
            recall_limit=3,
            retrieved_items=[{"memory_id": "m-1"}],
            discarded_results=[{"reason": "backend-returned-no-memories", "count": "0"}],
            health_report={"health": 0.8, "pressure": 0.1, "noise": 0.0, "complexity": 0.2},
            current_mode="stability",
            selected_strategy="fallback_simplify",
            reflection_triggered=True,
            reflection_reason="repeated_steps",
            selfcheck_triggered=True,
            selfcheck_reason="low_health",
            cleanup_triggered=False,
            cleanup_reason="backend-owned-cleanup",
            memory_write_allowed=False,
            memory_write_reason="high-noise",
            patch_proposals=[{"type": "threshold_change"}],
            patch_apply_enabled=False,
            patch_apply_attempted=False,
            patch_applied=False,
            patch_failure_reason="auto-patch-disabled",
            outcome="partial",
            failure_reason="",
            active_signals=["repeated_steps", "low_health"],
            memory_backend="memory_lancedb_pro",
            request_id="req-1",
            runtime_step=12,
            replay_attempt=2,
            ack_id="",
        )
        required = {
            "recall_requested",
            "recall_reason",
            "recall_query",
            "returned_memory_count",
            "selected_memory_ids",
            "discarded_results",
            "health",
            "pressure",
            "noise",
            "complexity",
            "current_mode",
            "selected_strategy",
            "reflection_triggered",
            "selfcheck_triggered",
            "cleanup_triggered",
            "memory_write_allowed",
            "patch_proposal_generated",
            "patch_apply_enabled",
            "patch_apply_attempted",
            "patch_applied",
            "patch_failure_reason",
            "outcome",
            "failure_reason",
            "memory_backend",
            "request_id",
            "runtime_step",
            "replay_attempt",
            "ack_id",
        }
        self.assertTrue(required.issubset(payload.keys()))


if __name__ == "__main__":
    unittest.main()
