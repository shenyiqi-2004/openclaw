from __future__ import annotations

import unittest

from core.events import EventContext
from core.runtime_work import BACKGROUND_WORK, MANUAL_WORK, RECOVERY_WORK, classify_sidecar_work


class RuntimeWorkTests(unittest.TestCase):
    def test_manual_cycle_classifies_as_manual(self) -> None:
        self.assertEqual(classify_sidecar_work(None, worker_mode=False), MANUAL_WORK)

    def test_worker_event_classifies_as_background(self) -> None:
        event = EventContext(
            event_id="evt-1",
            request_id="req-1",
            source="gateway-chat",
            status="success",
            session_key="session-1",
            agent_id="",
            replayed=False,
        )
        self.assertEqual(classify_sidecar_work(event, worker_mode=True), BACKGROUND_WORK)

    def test_replayed_event_classifies_as_recovery(self) -> None:
        event = EventContext(
            event_id="evt-2",
            request_id="req-2",
            source="gateway-chat",
            status="success",
            session_key="session-2",
            agent_id="",
            replayed=True,
        )
        self.assertEqual(classify_sidecar_work(event, worker_mode=True), RECOVERY_WORK)
