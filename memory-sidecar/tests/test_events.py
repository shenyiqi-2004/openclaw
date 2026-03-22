from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.events import EventContext, ack_event, has_ack, runtime_has_event


class EventHelpersTests(unittest.TestCase):
    def test_ack_file_marks_event_as_processed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            event = EventContext(
                event_id="evt-1",
                source="gateway-chat",
                status="success",
                session_key="session-1",
                agent_id="",
                replayed=False,
            )
            self.assertFalse(has_ack(tmpdir, "evt-1"))
            ack_event(tmpdir, event, outcome="applied", details={"step": 1})
            self.assertTrue(has_ack(tmpdir, "evt-1"))

    def test_runtime_record_can_short_circuit_duplicate_replay(self) -> None:
        runtime_data = {
            "records": [
                {"event_id": "evt-0"},
                {"event_id": "evt-1"},
            ]
        }
        self.assertTrue(runtime_has_event(runtime_data, "evt-1"))
        self.assertFalse(runtime_has_event(runtime_data, "evt-x"))


if __name__ == "__main__":
    unittest.main()
