from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.backends import resolve_memory_backend
from core.backends.lancedb_pro import LanceDbProMemoryBackend
from core.memory_manager import MemoryManager


class LanceDbProBackendTests(unittest.TestCase):
    def test_detects_active_plugin_from_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            runtime_dir = Path(tmpdir) / ".openclaw"
            runtime_dir.mkdir(parents=True, exist_ok=True)
            config_path = runtime_dir / "openclaw.json"
            config_path.write_text(
                json.dumps(
                    {
                        "plugins": {
                            "slots": {"memory": "memory-lancedb-pro"},
                            "entries": {
                                "memory-lancedb-pro": {
                                    "enabled": True,
                                    "config": {"dbPath": "/tmp/lancedb-pro"},
                                }
                            },
                        }
                    }
                ),
                encoding="utf-8",
            )

            backend = LanceDbProMemoryBackend(Path(tmpdir), runtime_config_path=config_path)
            status = backend.status()
            self.assertTrue(status.available)
            self.assertTrue(status.canonical)
            self.assertIn(status.mode, {"detect-only", "bridge"})

    def test_resolve_backend_falls_back_to_json_when_plugin_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = MemoryManager(base_dir)
            manager.initialize()
            backend, status = resolve_memory_backend(
                base_dir,
                manager,
                "general",
                runtime_config_path=base_dir / "missing-openclaw.json",
            )
            self.assertEqual(status.name, "json_snapshot")
            self.assertEqual(status.mode, "fallback")
            self.assertEqual(backend.status().name, "json_snapshot")


if __name__ == "__main__":
    unittest.main()
