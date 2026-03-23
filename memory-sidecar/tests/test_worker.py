from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.cycle import run_single_cycle
from core.events import claim_next_event, get_queue_status
from core.memory_manager import MemoryManager
from core.utils import save_json
from core.worker import consume_once


class WorkerTests(unittest.TestCase):
    def test_consume_once_handles_empty_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = consume_once(tmpdir)
            self.assertFalse(result["processed"])
            self.assertEqual(result["reason"], "queue-empty")

    def test_consume_once_processes_queued_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            memory_dir = base_dir / "memory"
            knowledge_dir = memory_dir / "knowledge"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            save_json(
                memory_dir / "recovery.json",
                {
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
                },
            )
            result = consume_once(base_dir)
            self.assertTrue(result["processed"])
            self.assertEqual(result["event_id"], "evt-1")
            status = get_queue_status(base_dir)
            self.assertEqual(status["acked"], 1)
            self.assertTrue((memory_dir / "commits.jsonl").exists())

    def test_duplicate_event_id_is_short_circuited(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = MemoryManager(base_dir)
            manager.initialize()
            runtime = manager.load_runtime()
            runtime["records"] = [{"event_id": "evt-dup", "step": 1}]
            manager.save_runtime(runtime)
            save_json(
                base_dir / "memory" / "recovery.json",
                {
                    "version": 1,
                    "order": ["evt-dup"],
                    "events": {
                        "evt-dup": {
                            "event_id": "evt-dup",
                            "request_id": "req-dup",
                            "timestamp": "2026-03-23T00:00:00Z",
                            "source": "gateway-chat",
                            "status": "success",
                            "session_key": "session-dup",
                            "agent_id": "",
                            "payload_hash": "hash",
                            "payload_summary": "dup",
                            "attempt_count": 0,
                            "processing_state": "queued",
                            "replayable": True,
                            "updated_at": "2026-03-23T00:00:00Z",
                        }
                    },
                },
            )
            event = claim_next_event(base_dir)
            self.assertIsNotNone(event)
            result = run_single_cycle(base_dir, event=event, print_output=False)
            self.assertEqual(result["ack_outcome"], "duplicate_noop")
            self.assertEqual(len(manager.load_runtime()["records"]), 1)
