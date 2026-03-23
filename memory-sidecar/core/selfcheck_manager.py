from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from core.utils import clamp, now_iso

PATCH_APPLY_ENV_FLAG = "OPENCLAW_ENABLE_AUTO_PATCH"
PATCH_DANGEROUS_ACTION = "self-modify-source"
PATCH_FILE_SETTING_ALLOWLIST = {
    ("core/retriever.py", "EARLY_RETURN_SCORE"),
    ("core/cleaner.py", "STALE_REMOVE_STEPS"),
    ("core/strategy_manager.py", "FORCE_NEW_PENALTY"),
    ("core/executor.py", "REPETITION_LIMIT"),
}


def _read_numeric_setting(base_dir: str | Path, target_file: str, setting: str) -> float | int | None:
    file_path = Path(base_dir) / target_file
    if not file_path.exists():
        return None
    prefix = f"{setting} = "
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith(prefix):
            continue
        raw_value = stripped[len(prefix):].strip()
        try:
            return int(raw_value) if raw_value.isdigit() else float(raw_value)
        except ValueError:
            return None
    return None


def run_self_check(
    working: dict[str, Any],
    summary: dict[str, Any],
    strategy_data: dict[str, Any],
    reflection_data: dict[str, Any],
    partition_data_map: dict[str, dict[str, Any]],
) -> dict[str, float | int]:
    all_items = [item for data in partition_data_map.values() for item in data.get("items", [])]
    item_count = len(all_items)
    unique_contents = len({item.get("content", "") for item in all_items})
    low_importance = sum(1 for item in all_items if float(item.get("importance", 0.0)) < 0.3)
    strategy_usage = [int(strategy.get("usage", 0)) for strategy in strategy_data.get("strategies", [])]
    total_strategy_usage = sum(strategy_usage) or 1
    max_strategy_usage = max(strategy_usage) if strategy_usage else 0
    disk_usage = (
        sum(len(str(data)) for data in partition_data_map.values())
        + len(str(summary))
        + len(str(reflection_data))
        + len(str(strategy_data))
    )
    retrieval_effectiveness = 1.0 if working.get("last_result_keys") else 0.5
    complexity_score = clamp(
        (
            len(summary.get("progress", []))
            + len(summary.get("failures", []))
            + len(reflection_data.get("insights", []))
        ) / 60.0,
        0.0,
        1.0,
    )

    return {
        "memory_pressure": round(min(item_count / 100.0, 1.0), 3),
        "duplicate_ratio": round(0.0 if item_count == 0 else 1 - (unique_contents / item_count), 3),
        "low_importance_ratio": round(0.0 if item_count == 0 else low_importance / item_count, 3),
        "strategy_skew": round(max_strategy_usage / total_strategy_usage, 3),
        "retrieval_effectiveness": round(retrieval_effectiveness, 3),
        "disk_usage": int(disk_usage),
        "complexity_score": round(complexity_score, 3),
    }


def evaluate_health(current_check: dict[str, Any], previous_check: dict[str, Any] | None = None) -> dict[str, float]:
    pressure = float(current_check["memory_pressure"])
    noise = float(current_check["duplicate_ratio"]) + float(current_check["low_importance_ratio"])
    complexity = float(current_check["complexity_score"])
    disk_factor = clamp(float(current_check["disk_usage"]) / 20000.0, 0.0, 1.0)
    health = 1.0
    health -= pressure * 0.25
    health -= noise * 0.25
    health -= float(current_check["strategy_skew"]) * 0.15
    health -= (1.0 - float(current_check["retrieval_effectiveness"])) * 0.1
    health -= complexity * 0.15
    health -= disk_factor * 0.1
    health = round(clamp(health, 0.0, 1.0), 3)
    previous_health = float(previous_check.get("health", health)) if previous_check else health
    return {
        "health": health,
        "delta": round(health - previous_health, 3),
        "pressure": round(pressure, 3),
        "noise": round(noise, 3),
        "complexity": round(complexity, 3),
    }


def select_mode(health_report: dict[str, Any], check_report: dict[str, Any], current_mode: str) -> str:
    if (
        check_report["memory_pressure"] >= 0.3
        or health_report["complexity"] >= 0.45
        or float(check_report.get("disk_usage", 0)) >= 15000
    ):
        return "convergence"
    if current_mode == "convergence" and health_report["health"] >= 0.85 and health_report["complexity"] < 0.35:
        return "normal"
    if health_report["health"] < 0.8 or health_report["delta"] < -0.03 or check_report["memory_pressure"] > 0.35:
        return "stability"
    if current_mode == "stability" and health_report["health"] >= 0.82:
        return "normal"
    return "normal"


def generate_optimization_suggestions(
    check_report: dict[str, Any],
    health_report: dict[str, Any],
    working: dict[str, Any],
    max_suggestions: int = 2,
) -> list[str]:
    budget = working.get("evolution_budget", {})
    recent_count = sum(
        1
        for item in working.get("recent_suggestion_steps", [])
        if int(working.get("step_count", 0)) - int(item) < 10
    )
    allowed = max(0, min(max_suggestions, int(budget.get("max_suggestions_per_10_steps", max_suggestions)) - recent_count))
    suggestions: list[str] = []
    if health_report["pressure"] > 0.2:
        suggestions.append(f"clean {working.get('last_partition', 'general')} earlier")
    if check_report["retrieval_effectiveness"] < 0.75:
        suggestions.append("reduce retrieval frequency")
    if check_report["strategy_skew"] > 0.7:
        suggestions.append("diversify strategy usage")
    return suggestions[:allowed]


def generate_patch_proposals(
    check_report: dict[str, Any],
    health_report: dict[str, Any],
    working: dict[str, Any],
    base_dir: str | Path,
) -> list[dict[str, Any]]:
    budget = working.get("evolution_budget", {})
    if int(budget.get("patch_failures", 0)) >= int(budget.get("disable_patch_after_failures", 2)):
        return []
    if working.get("mode") == "convergence":
        return []
    proposals: list[dict[str, Any]] = []
    if check_report["retrieval_effectiveness"] < 0.75 and working.get("mode") == "stability":
        current = _read_numeric_setting(base_dir, "core/retriever.py", "EARLY_RETURN_SCORE")
        if current is not None and float(current) > 5.2:
            proposals.append(
                {
                    "type": "threshold_change",
                    "target_file": "core/retriever.py",
                    "setting": "EARLY_RETURN_SCORE",
                    "old": float(current),
                    "new": 5.2,
                    "reason": "allow stronger reuse under stability mode",
                }
            )
    elif check_report["strategy_skew"] > 0.72:
        current = _read_numeric_setting(base_dir, "core/strategy_manager.py", "FORCE_NEW_PENALTY")
        if current is not None and float(current) < 0.6:
            proposals.append(
                {
                    "type": "threshold_change",
                    "target_file": "core/strategy_manager.py",
                    "setting": "FORCE_NEW_PENALTY",
                    "old": float(current),
                    "new": 0.6,
                    "reason": "encourage strategy diversification",
                }
            )
    elif health_report["pressure"] > 0.2:
        current = _read_numeric_setting(base_dir, "core/cleaner.py", "STALE_REMOVE_STEPS")
        if current is not None and float(current) > 9:
            proposals.append(
                {
                    "type": "threshold_change",
                    "target_file": "core/cleaner.py",
                    "setting": "STALE_REMOVE_STEPS",
                    "old": int(current),
                    "new": 9,
                    "reason": "shrink stale unused items earlier",
                }
            )
    return proposals[:1]


def describe_patch_policy(working: dict[str, Any]) -> dict[str, Any]:
    budget = working.get("evolution_budget", {})
    env_enabled = os.environ.get(PATCH_APPLY_ENV_FLAG, "").strip() == "1"
    config_enabled = bool(budget.get("auto_patch_enabled", False))
    config_disabled = bool(budget.get("auto_patch_disabled", True))
    enabled = env_enabled or (config_enabled and not config_disabled)
    source = "env" if env_enabled else "config" if enabled else "disabled"
    return {
        "enabled": enabled,
        "source": source,
        "dangerous_action": PATCH_DANGEROUS_ACTION,
        "manual_apply_required": not enabled,
        "allowlisted_targets": sorted(f"{file}:{setting}" for file, setting in PATCH_FILE_SETTING_ALLOWLIST),
    }


def patch_apply_enabled(working: dict[str, Any]) -> bool:
    return bool(describe_patch_policy(working)["enabled"])


def is_patch_target_allowlisted(proposal: dict[str, Any]) -> bool:
    return (proposal.get("target_file"), proposal.get("setting")) in PATCH_FILE_SETTING_ALLOWLIST


def apply_safe_patch_proposals(
    base_dir: str | Path,
    proposals: list[dict[str, Any]],
    working: dict[str, Any],
) -> dict[str, Any]:
    policy = describe_patch_policy(working)
    if not proposals:
        return {
            "enabled": bool(policy["enabled"]),
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "no-proposals",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": bool(policy["manual_apply_required"]),
            "proposal_allowed": False,
        }
    budget = working.get("evolution_budget", {})
    step_count = int(working.get("step_count", 0))
    if not bool(policy["enabled"]):
        return {
            "enabled": False,
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "auto-patch-disabled",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": True,
            "proposal_allowed": True,
        }
    if step_count - int(budget.get("last_patch_step", 0)) < 20:
        return {
            "enabled": True,
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "patch-cooldown",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": False,
            "proposal_allowed": True,
        }
    if int(budget.get("patch_failures", 0)) >= int(budget.get("disable_patch_after_failures", 2)):
        return {
            "enabled": True,
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "patch-failures-exceeded",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": False,
            "proposal_allowed": True,
        }

    proposal = proposals[0]
    if not is_patch_target_allowlisted(proposal):
        return {
            "enabled": True,
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "proposal-not-allowlisted",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": False,
            "proposal_allowed": False,
        }

    file_path = Path(base_dir) / str(proposal["target_file"])
    original = file_path.read_text(encoding="utf-8")
    old_line = f"{proposal['setting']} = {proposal['old']}"
    new_line = f"{proposal['setting']} = {proposal['new']}"
    if old_line not in original:
        return {
            "enabled": True,
            "attempted": False,
            "applied": False,
            "applied_patches": [],
            "reason": "target-setting-not-found",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": False,
            "proposal_allowed": True,
        }

    updated = original.replace(old_line, new_line, 1)
    try:
        compile(updated, str(file_path), "exec")
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        temp_path.write_text(updated, encoding="utf-8")
        temp_path.replace(file_path)
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(file_path)],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            file_path.write_text(original, encoding="utf-8")
            budget["patch_failures"] = int(budget.get("patch_failures", 0)) + 1
            return {
                "enabled": True,
                "attempted": True,
                "applied": False,
                "applied_patches": [],
                "reason": f"py_compile_failed:{result.stderr.strip() or result.stdout.strip() or result.returncode}",
                "policy": policy,
                "dangerous_action": PATCH_DANGEROUS_ACTION,
                "manual_apply_required": False,
                "proposal_allowed": True,
            }
        runtime_env = dict(os.environ)
        runtime_env["OPENCLAW_SKIP_EVOLUTION"] = "1"
        runtime_result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            check=False,
            env=runtime_env,
        )
        if runtime_result.returncode != 0:
            file_path.write_text(original, encoding="utf-8")
            budget["patch_failures"] = int(budget.get("patch_failures", 0)) + 1
            return {
                "enabled": True,
                "attempted": True,
                "applied": False,
                "applied_patches": [],
                "reason": f"runtime_probe_failed:{runtime_result.stderr.strip() or runtime_result.stdout.strip() or runtime_result.returncode}",
                "policy": policy,
                "dangerous_action": PATCH_DANGEROUS_ACTION,
                "manual_apply_required": False,
                "proposal_allowed": True,
            }
    except Exception as exc:
        file_path.write_text(original, encoding="utf-8")
        budget["patch_failures"] = int(budget.get("patch_failures", 0)) + 1
        return {
            "enabled": True,
            "attempted": True,
            "applied": False,
            "applied_patches": [],
            "reason": f"exception:{exc}",
            "policy": policy,
            "dangerous_action": PATCH_DANGEROUS_ACTION,
            "manual_apply_required": False,
            "proposal_allowed": True,
        }

    budget["last_patch_step"] = step_count
    applied = {
        "at": now_iso(),
        "step": step_count,
        "target_file": proposal["target_file"],
        "setting": proposal["setting"],
        "old": proposal["old"],
        "new": proposal["new"],
        "reason": proposal["reason"],
        "baseline_health": float(working.get("last_health", 0.0)),
        "benefit_checked": False,
    }
    return {
        "enabled": True,
        "attempted": True,
        "applied": True,
        "applied_patches": [applied],
        "reason": "",
        "policy": policy,
        "dangerous_action": PATCH_DANGEROUS_ACTION,
        "manual_apply_required": False,
        "proposal_allowed": True,
    }


def update_no_benefit_patch_state(
    working: dict[str, Any],
    selfcheck_data: dict[str, Any],
    health_report: dict[str, Any],
) -> None:
    budget = working.setdefault("evolution_budget", {})
    current_step = int(working.get("step_count", 0))
    no_benefit = int(budget.get("no_benefit_patch_count", 0))
    for patch in selfcheck_data.get("applied_patches", []):
        if patch.get("benefit_checked"):
            continue
        if current_step - int(patch.get("step", current_step)) < 5:
            continue
        baseline = float(patch.get("baseline_health", 0.0))
        improved = float(health_report.get("health", 0.0)) > baseline + 0.01
        patch["benefit_checked"] = True
        patch["benefit_health"] = float(health_report.get("health", 0.0))
        patch["benefit"] = improved
        if improved:
            no_benefit = 0
        else:
            no_benefit += 1
    budget["no_benefit_patch_count"] = no_benefit
    if no_benefit >= 3:
        budget["auto_patch_disabled"] = True


def store_selfcheck(
    selfcheck_data: dict[str, Any],
    report: dict[str, Any],
    health_report: dict[str, Any],
    suggestions: list[str],
    proposals: list[dict[str, Any]],
    applied_patches: list[dict[str, Any]],
    max_items: int = 30,
) -> dict[str, Any]:
    checks = selfcheck_data.setdefault("checks", [])
    evaluations = selfcheck_data.setdefault("evaluations", [])
    optimizations = selfcheck_data.setdefault("optimizations", [])
    patch_proposals = selfcheck_data.setdefault("patch_proposals", [])
    applied = selfcheck_data.setdefault("applied_patches", [])
    checks.append(report)
    evaluations.append(health_report)
    if suggestions:
        optimizations.append({"at": now_iso(), "items": suggestions})
    if proposals:
        patch_proposals.append({"at": now_iso(), "items": proposals})
    if applied_patches:
        applied.extend(applied_patches)
    selfcheck_data["checks"] = checks[-max_items:]
    selfcheck_data["evaluations"] = evaluations[-max_items:]
    selfcheck_data["optimizations"] = optimizations[-max_items:]
    selfcheck_data["patch_proposals"] = patch_proposals[-max_items:]
    selfcheck_data["applied_patches"] = applied[-max_items:]
    selfcheck_data["last_run"] = now_iso()
    return selfcheck_data
