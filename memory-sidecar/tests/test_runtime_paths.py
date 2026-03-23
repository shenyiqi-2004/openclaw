from __future__ import annotations

import os
import unittest

from core.runtime_paths import describe_memory_root


class RuntimePathsTests(unittest.TestCase):
    def test_defaults_match_canonical_paths(self) -> None:
        previous_runtime_root = os.environ.pop("OPENCLAW_RUNTIME_ROOT", None)
        previous_memory_root = os.environ.pop("OPENCLAW_EXTERNAL_MEMORY_ROOT", None)
        try:
            status = describe_memory_root()
            self.assertEqual(str(status.runtime_root), "/home/park/openclaw")
            self.assertEqual(str(status.memory_root), "/home/park/openclaw/memory-sidecar")
            self.assertFalse(status.deprecated)
        finally:
            if previous_runtime_root is not None:
                os.environ["OPENCLAW_RUNTIME_ROOT"] = previous_runtime_root
            if previous_memory_root is not None:
                os.environ["OPENCLAW_EXTERNAL_MEMORY_ROOT"] = previous_memory_root

    def test_marks_deprecated_memory_root(self) -> None:
        previous = os.environ.get("OPENCLAW_EXTERNAL_MEMORY_ROOT")
        os.environ["OPENCLAW_EXTERNAL_MEMORY_ROOT"] = "/mnt/d/openclaw"
        try:
            status = describe_memory_root()
            self.assertTrue(status.deprecated)
        finally:
            if previous is None:
                os.environ.pop("OPENCLAW_EXTERNAL_MEMORY_ROOT", None)
            else:
                os.environ["OPENCLAW_EXTERNAL_MEMORY_ROOT"] = previous

    def test_runtime_root_env_expands_to_memory_sidecar(self) -> None:
        previous_runtime_root = os.environ.get("OPENCLAW_RUNTIME_ROOT")
        previous_memory_root = os.environ.pop("OPENCLAW_EXTERNAL_MEMORY_ROOT", None)
        os.environ["OPENCLAW_RUNTIME_ROOT"] = "/tmp/openclaw-runtime"
        try:
            status = describe_memory_root()
            self.assertEqual(str(status.runtime_root), "/tmp/openclaw-runtime")
            self.assertEqual(str(status.memory_root), "/tmp/openclaw-runtime/memory-sidecar")
            self.assertEqual(status.source, "env:OPENCLAW_RUNTIME_ROOT")
        finally:
            if previous_runtime_root is None:
                os.environ.pop("OPENCLAW_RUNTIME_ROOT", None)
            else:
                os.environ["OPENCLAW_RUNTIME_ROOT"] = previous_runtime_root
            if previous_memory_root is not None:
                os.environ["OPENCLAW_EXTERNAL_MEMORY_ROOT"] = previous_memory_root
