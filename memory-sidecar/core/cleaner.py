from __future__ import annotations

import re

from core.retriever import rebuild_index, tokenize
from core.utils import clamp, normalize_text, unique_preserve_order

LOW_IMPORTANCE_THRESHOLD = 0.3
STALE_REMOVE_STEPS = 10
STALE_DECAY_STEPS = 8
SUMMARY_SECTION_CAP = 50
SUMMARY_KEEP_NEWEST = 30
SUMMARY_KEEP_HIGHEST = 20
NEAR_DUPLICATE_OVERLAP = 0.7


def needs_cleaning(partition_data: dict) -> bool:
    items = partition_data.get("items", [])
    if len(items) > 100:
        return True
    if not items:
        return False
    low_ratio = sum(1 for item in items if float(item.get("importance", 0.0)) < LOW_IMPORTANCE_THRESHOLD) / len(items)
    return low_ratio > 0.3 or len(items) > 120


def clean_partition(partition_data: dict, current_step_count: int = 0) -> dict:
    merged_items: list[dict] = []
    for item in partition_data.get("items", []):
        importance = float(item.get("importance", 0.0))
        stale_steps = current_step_count - int(item.get("last_accessed_step", 0))
        if importance < LOW_IMPORTANCE_THRESHOLD and int(item.get("access_count", 0)) == 0:
            continue
        if int(item.get("access_count", 0)) == 0 and stale_steps > STALE_REMOVE_STEPS:
            continue
        if int(item.get("access_count", 0)) >= 3:
            item["importance"] = clamp(importance + 0.05, 0.0, 1.0)
        elif stale_steps > STALE_DECAY_STEPS:
            item["importance"] = clamp(importance - 0.05, 0.0, 1.0)
        if len(item.get("content", "")) > 120:
            item["content"] = f"{item['content'][:117].rstrip()}..."
        item_tokens = set(item.get("tokens", []))

        merged = False
        for existing in merged_items:
            existing_tokens = set(existing.get("tokens", []))
            overlap = len(item_tokens & existing_tokens) / max(1, len(item_tokens | existing_tokens))
            exact_match = normalize_text(existing.get("content", "")) == normalize_text(item.get("content", ""))
            if not exact_match and overlap <= NEAR_DUPLICATE_OVERLAP:
                continue
            if float(item.get("importance", 0.0)) > float(existing.get("importance", 0.0)):
                existing["content"] = item["content"]
                existing["importance"] = item["importance"]
                existing["created_at"] = item.get("created_at", existing.get("created_at", ""))
                existing["key"] = item.get("key", existing.get("key", ""))
                existing["tokens"] = item.get("tokens", existing.get("tokens", []))
            existing["tags"] = unique_preserve_order([*existing.get("tags", []), *item.get("tags", [])])[:5]
            existing["access_count"] = max(int(existing.get("access_count", 0)), int(item.get("access_count", 0)))
            existing["last_accessed_step"] = max(
                int(existing.get("last_accessed_step", 0)),
                int(item.get("last_accessed_step", 0)),
            )
            merged = True
            break
        if not merged:
            merged_items.append(item)

    partition_data["items"] = merged_items[:120]
    rebuild_index(partition_data)
    return partition_data


def light_compress_summary(summary_data: dict, aggressive: bool = False) -> dict:
    keep_newest = 20 if aggressive else SUMMARY_KEEP_NEWEST
    keep_highest = 10 if aggressive else SUMMARY_KEEP_HIGHEST
    for key, value in summary_data.items():
        if isinstance(value, list):
            deduped = unique_preserve_order(str(item).strip() for item in value if str(item).strip())
            if len(deduped) > SUMMARY_SECTION_CAP:
                recent = deduped[-keep_newest:]
                older = deduped[:-keep_newest]
                older_sorted = sorted(
                    older,
                    key=lambda text: (-_summary_value(text), older.index(text)),
                )
                kept = recent + older_sorted[:keep_highest]
                deduped = unique_preserve_order(kept)
            summary_data[key] = deduped
    return summary_data


def _summary_value(text: str) -> int:
    normalized = normalize_text(text)
    tokens = [token for token in tokenize(normalized) if len(token) > 1]
    unique_count = len(set(tokens))
    signal_bonus = 2 if any(char.isdigit() for char in text) else 0
    signal_bonus += 1 if "\\" in text or "/" in text else 0
    signal_bonus += 1 if normalized.startswith("do not") else 0
    signal_bonus += 1 if normalized.startswith("不要") else 0
    return min(unique_count, 12) + signal_bonus
