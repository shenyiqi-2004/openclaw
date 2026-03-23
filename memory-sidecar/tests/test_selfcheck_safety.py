from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from core.selfcheck_manager import apply_safe_patch_proposals, describe_patch_policy, patch_apply_enabled


class SelfcheckSafetyTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("OPENCLAW_ENABLE_AUTO_PATCH", None)

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
        policy = describe_patch_policy(working)
        self.assertFalse(policy["enabled"])
        self.assertEqual(policy["source"], "disabled")
        self.assertTrue(policy["manual_apply_required"])

    def test_env_flag_can_explicitly_enable_auto_patch(self) -> None:
        os.environ["OPENCLAW_ENABLE_AUTO_PATCH"] = "1"
        working = {"evolution_budget": {"auto_patch_enabled": False, "auto_patch_disabled": True}}
        self.assertTrue(patch_apply_enabled(working))
        policy = describe_patch_policy(working)
        self.assertTrue(policy["enabled"])
        self.assertEqual(policy["source"], "env")

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
            self.assertTrue(result["manual_apply_required"])
            self.assertEqual(result["dangerous_action"], "self-modify-source")
            self.assertIn("5.8", (base_dir / "core" / "retriever.py").read_text(encoding="utf-8"))

    def test_non_allowlisted_patch_is_rejected_even_when_enabled(self) -> None:
        os.environ["OPENCLAW_ENABLE_AUTO_PATCH"] = "1"
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            (base_dir / "core").mkdir(parents=True, exist_ok=True)
            (base_dir / "core" / "custom.py").write_text("SOME_LIMIT = 3\n", encoding="utf-8")
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
                        "target_file": "core/custom.py",
                        "setting": "SOME_LIMIT",
                        "old": 3,
                        "new": 2,
                        "reason": "test",
                    }
                ],
                working=working,
            )
            self.assertFalse(result["applied"])
            self.assertFalse(result["attempted"])
            self.assertEqual(result["reason"], "proposal-not-allowlisted")
            self.assertFalse(result["proposal_allowed"])
            self.assertEqual(result["policy"]["source"], "env")


if __name__ == "__main__":
    unittest.main()
