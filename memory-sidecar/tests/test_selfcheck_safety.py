from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.selfcheck_manager import apply_safe_patch_proposals, patch_apply_enabled


class SelfcheckSafetyTests(unittest.TestCase):
    def test_auto_patch_is_disabled_by_default(self) -> None:
        working = {
            "step_count": 25,
            "last_health": 0.9,
            "evolution_budget": {
                "auto_patch_enabled": False,
                "auto_patch_disabled": True,
                "patch_failures": 0,
                "disable_patch_after_failures": 2,
                "last_patch_step": 0,
            },
        }
        self.assertFalse(patch_apply_enabled(working))

    def test_patch_proposals_do_not_auto_apply_without_explicit_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            (base_dir / "core").mkdir(parents=True, exist_ok=True)
            (base_dir / "core" / "retriever.py").write_text("EARLY_RETURN_SCORE = 5.8\n", encoding="utf-8")
            working = {
                "step_count": 25,
                "last_health": 0.9,
                "evolution_budget": {
                    "auto_patch_enabled": False,
                    "auto_patch_disabled": True,
                    "patch_failures": 0,
                    "disable_patch_after_failures": 2,
                    "last_patch_step": 0,
                },
            }
            result = apply_safe_patch_proposals(
                base_dir,
                proposals=[
                    {
                        "target_file": "core/retriever.py",
                        "setting": "EARLY_RETURN_SCORE",
                        "old": 5.8,
                        "new": 5.2,
                        "reason": "test",
                    }
                ],
                working=working,
            )
            self.assertFalse(result["applied"])
            self.assertFalse(result["attempted"])
            self.assertEqual(result["reason"], "auto-patch-disabled")
            self.assertIn("5.8", (base_dir / "core" / "retriever.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
