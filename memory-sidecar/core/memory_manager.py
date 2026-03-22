from __future__ import annotations

from pathlib import Path
from typing import Any

from core.retriever import rebuild_index, tokenize
from core.utils import clamp, ensure_file, load_json, normalize_text, now_iso, save_json, unique_preserve_order


DEFAULT_WORKING = {
    "goal": "Build a stable minimal memory system for OpenClaw using Python and JSON.",
    "current_step": "Initialize memory files and managers",
    "next_action": "Create modular memory components",
    "focus": "stability and simplicity",
    "step_history": [],
    "step_count": 0,
    "last_action": "",
    "retrieval_cooldown_until": 0,
    "knowledge_write_cooldown_until": 0,
    "last_partition": "",
    "last_strategy": "",
    "last_query": "",
    "last_result_keys": [],
    "recent_suggestion_steps": [],
    "mode": "normal",
    "last_health": 1.0,
    "evolution_budget": {
        "max_suggestions_per_10_steps": 2,
        "max_patches_per_20_steps": 1,
        "disable_patch_after_failures": 2,
        "patch_failures": 0,
        "last_patch_step": 0,
        "no_benefit_patch_count": 0,
        "auto_patch_enabled": False,
        "auto_patch_disabled": True,
    },
}

DEFAULT_SUMMARY = {
    "facts": [],
    "decisions": [],
    "failures": [],
    "progress": [],
    "anti_patterns": [],
}

DEFAULT_STRATEGY = {
    "strategies": [
        {
            "name": "direct_execution",
            "description": "Do the simplest valid next action directly",
            "score": 1.0,
            "usage": 0,
            "last_used_step": 0,
        },
        {
            "name": "decompose_task",
            "description": "Break task into smaller steps when needed",
            "score": 0.8,
            "usage": 0,
            "last_used_step": 0,
        },
        {
            "name": "fallback_simplify",
            "description": "Reduce complexity after repetition or failure",
            "score": 0.7,
            "usage": 0,
            "last_used_step": 0,
        },
    ]
}

DEFAULT_REFLECTION = {"insights": []}
DEFAULT_SELFCHECK = {
    "checks": [],
    "evaluations": [],
    "optimizations": [],
    "patch_proposals": [],
    "applied_patches": [],
    "last_run": "",
}
DEFAULT_RUNTIME = {"records": []}
DEFAULT_META = {
    "rules": [
        {"rule": "Only store high-value reusable knowledge", "confidence": 1.0, "last_validated_step": 0},
        {"rule": "Set retrieval depth from runtime signals instead of a fixed top-k", "confidence": 1.0, "last_validated_step": 0},
        {"rule": "Avoid repeated steps", "confidence": 1.0, "last_validated_step": 0},
        {"rule": "Prefer direct execution when next action is obvious", "confidence": 1.0, "last_validated_step": 0},
        {"rule": "Reduce memory growth whenever possible", "confidence": 1.0, "last_validated_step": 0},
    ],
    "patterns": [
        {"pattern": "After repeated failure, switch strategy", "confidence": 1.0, "last_validated_step": 0},
        {"pattern": "Avoid frequent knowledge writes", "confidence": 1.0, "last_validated_step": 0},
        {"pattern": "Use summary instead of knowledge when possible", "confidence": 1.0, "last_validated_step": 0},
    ],
    "constraints": [
        "Keep memory small",
        "Keep retrieval fast",
        "Keep disk usage low",
        "Keep evaluation lightweight",
        "Prefer parameter tuning over code patching",
    ],
    "evaluation_rules": [
        "If duplicate ratio rises, prefer cleaning over new learning",
        "If retrieval effectiveness drops, reduce retrieval frequency and clean the active partition",
        "If a strategy is overused without strong success, diversify",
        "If memory pressure rises, prioritize compression and deletion over storage",
    ],
}
DEFAULT_PARTITION = {"items": [], "index": {}}
VALID_PARTITIONS = ("programming", "science", "finance", "general")


class MemoryManager:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.memory_dir = self.base_dir / "memory"
        self.knowledge_dir = self.memory_dir / "knowledge"

    def initialize(self) -> None:
        ensure_file(self.memory_dir / "working.json", DEFAULT_WORKING)
        ensure_file(self.memory_dir / "summary.json", DEFAULT_SUMMARY)
        ensure_file(self.memory_dir / "strategy.json", DEFAULT_STRATEGY)
        ensure_file(self.memory_dir / "reflection.json", DEFAULT_REFLECTION)
        ensure_file(self.memory_dir / "selfcheck.json", DEFAULT_SELFCHECK)
        ensure_file(self.memory_dir / "runtime.json", DEFAULT_RUNTIME)
        ensure_file(self.memory_dir / "meta.json", DEFAULT_META)
        for partition in VALID_PARTITIONS:
            ensure_file(self.knowledge_dir / f"{partition}.json", DEFAULT_PARTITION)

    def load_working(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "working.json"), DEFAULT_WORKING)

    def save_working(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "working.json", data)

    def load_summary(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "summary.json"), DEFAULT_SUMMARY)

    def save_summary(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "summary.json", data)

    def load_strategy(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "strategy.json"), DEFAULT_STRATEGY)

    def save_strategy(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "strategy.json", data)

    def load_reflection(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "reflection.json"), DEFAULT_REFLECTION)

    def save_reflection(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "reflection.json", data)

    def load_selfcheck(self) -> dict[str, Any]:
        data = self._merge_defaults(load_json(self.memory_dir / "selfcheck.json"), DEFAULT_SELFCHECK)
        for check in data.get("checks", []):
            if "disk_usage_bytes" in check and "disk_usage" not in check:
                check["disk_usage"] = int(check.pop("disk_usage_bytes"))
        return data

    def save_selfcheck(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "selfcheck.json", data)

    def load_runtime(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "runtime.json"), DEFAULT_RUNTIME)

    def save_runtime(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "runtime.json", data)

    def load_meta(self) -> dict[str, Any]:
        return self._merge_defaults(load_json(self.memory_dir / "meta.json"), DEFAULT_META)

    def save_meta(self, data: dict[str, Any]) -> None:
        save_json(self.memory_dir / "meta.json", data)

    def load_partition(self, partition: str) -> dict[str, Any]:
        self._validate_partition(partition)
        return self._merge_defaults(load_json(self.knowledge_dir / f"{partition}.json"), DEFAULT_PARTITION)

    def save_partition(self, partition: str, data: dict[str, Any]) -> None:
        self._validate_partition(partition)
        save_json(self.knowledge_dir / f"{partition}.json", data)

    def append_summary(self, section: str, text: str, max_items: int = 50) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        summary = self.load_summary()
        if section not in summary:
            summary[section] = []
        summary[section].append(cleaned)
        summary[section] = summary[section][-max_items:]
        self.save_summary(summary)

    def add_knowledge(
        self,
        partition: str,
        content: str,
        tags: list[str],
        importance: float,
        current_step_count: int = 0,
        working: dict[str, Any] | None = None,
    ) -> bool:
        self._validate_partition(partition)
        normalized = normalize_text(content)
        tokens = [token for token in tokenize(normalized) if len(token) > 2]
        if len(normalized) < 20 or len(tokens) < 3:
            return False

        active_working = working if working is not None else self.load_working()
        if not self.knowledge_write_allowed(active_working):
            return False

        content_short = content.strip()
        if len(content_short) > 120:
            content_short = f"{content_short[:117].rstrip()}..."
        tag_list = unique_preserve_order(normalize_text(tag) for tag in tags if normalize_text(tag))
        key = "-".join(tokens[:4])

        partition_data = self.load_partition(partition)
        token_set = set(tokens)
        for item in partition_data["items"]:
            existing = normalize_text(item.get("content", ""))
            if existing == normalized:
                return False
            existing_tokens = set(item.get("tokens", []))
            overlap = len(token_set & existing_tokens) / max(1, len(token_set | existing_tokens))
            if overlap > 0.7:
                return False

        entry = {
            "content": content_short,
            "tags": tag_list[:5],
            "importance": clamp(importance, 0.0, 1.0),
            "created_at": now_iso(),
            "last_accessed_step": current_step_count,
            "access_count": 0,
            "tokens": tokens[:8],
            "key": key,
        }
        partition_data["items"].append(entry)
        rebuild_index(partition_data)
        self.save_partition(partition, partition_data)
        self.mark_knowledge_write_used(active_working)
        self.save_working(active_working)
        return True

    def update_working_step(self, current_step: str, next_action: str, focus: str, last_action: str = "") -> None:
        working = self.load_working()
        working["current_step"] = current_step
        working["next_action"] = next_action
        working["focus"] = focus
        working["last_action"] = last_action
        self.save_working(working)

    def knowledge_write_allowed(self, working: dict[str, Any]) -> bool:
        return int(working.get("step_count", 0)) >= int(working.get("knowledge_write_cooldown_until", 0))

    def mark_knowledge_write_used(self, working: dict[str, Any]) -> None:
        working["knowledge_write_cooldown_until"] = int(working.get("step_count", 0)) + 2

    def _validate_partition(self, partition: str) -> None:
        if partition not in VALID_PARTITIONS:
            raise ValueError(f"Invalid partition: {partition}")

    def _merge_defaults(self, data: Any, defaults: Any) -> Any:
        if isinstance(defaults, dict) and isinstance(data, dict):
            merged = {key: self._merge_defaults(data.get(key), value) for key, value in defaults.items()}
            for key, value in data.items():
                if key not in merged:
                    merged[key] = value
            return merged
        if data is None:
            return defaults
        return data
