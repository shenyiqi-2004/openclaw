from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.events import EventContext, ack_event, claim_next_event, get_queue_status, has_ack, runtime_has_event
from core.utils import save_json


class EventHelpersTests(unittest.TestCase):
    def test_ack_file_marks_event_as_processed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            event = EventContext(
                event_id="evt-1",
                request_id="req-1",
                source="gateway-chat",
                status="success",
                session_key="session-1",
                agent_id="",
                replayed=False,
            )
            self.assertFalse(has_ack(tmpdir, "evt-1"))
            ack = ack_event(tmpdir, event, outcome="applied", details={"step": 1})
            self.assertTrue(has_ack(tmpdir, "evt-1"))
            self.assertTrue(str(ack.get("ack_id", "")))

    def test_runtime_record_can_short_circuit_duplicate_replay(self) -> None:
        runtime_data = {
            "records": [
                {"event_id": "evt-0"},
                {"event_id": "evt-1"},
            ]
        }
        self.assertTrue(runtime_has_event(runtime_data, "evt-1"))
        self.assertFalse(runtime_has_event(runtime_data, "evt-x"))

    def test_claim_next_event_marks_queue_item_processing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_dir = Path(tmpdir) / "memory"
            memory_dir.mkdir(parents=True, exist_ok=True)
            recovery = {
                "version": 1,
                "order": ["evt-1"],
                "events": {
                    "evt-1": {
                        "event_id": "evt-1",
                        "request_id": "req-1",
                        "timestamp": "2026-03-23T00:00:00Z",
                        "source": "gateway-chat",
                        "status": "success",
                        "session_key": "session-1",
                        "agent_id": "",
                        "payload_hash": "hash",
                        "payload_summary": "summary",
                        "attempt_count": 0,
                        "processing_state": "queued",
                        "replayable": True,
                        "updated_at": "2026-03-23T00:00:00Z",
                    }
                },
            }
            save_json(memory_dir / "recovery.json", recovery)
            event = claim_next_event(tmpdir)
            self.assertIsNotNone(event)
            self.assertEqual(event.event_id, "evt-1")
            status = get_queue_status(tmpdir)
            self.assertEqual(status["processing"], 1)


if __name__ == "__main__":
    unittest.main()
