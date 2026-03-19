from __future__ import annotations

import re
from typing import Any

from core.utils import normalize_text, unique_preserve_order

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "the", "to", "with", "this", "that", "into", "only",
}
EARLY_RETURN_SCORE = 5.2
MAX_RETRIEVE_K = 3
CACHE_SIMILARITY_THRESHOLD = 0.75


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens: list[str] = []
    for token in re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", normalized):
        if re.fullmatch(r"[a-z0-9]+", token):
            if token not in STOPWORDS:
                tokens.append(token)
            continue
        if len(token) == 1:
            tokens.append(token)
            continue
        tokens.append(token)
        tokens.extend(list(token))
        for idx in range(len(token) - 1):
            tokens.append(token[idx : idx + 2])
    return unique_preserve_order(tokens)


def compute_overlap_score(query_tokens: list[str], item: dict[str, Any]) -> float:
    item_tokens = set(item.get("tokens", []))
    query_set = set(query_tokens)
    token_overlap = len(query_set & item_tokens) / max(1, len(query_set))
    tag_overlap = len(query_set & set(item.get("tags", [])))
    key_tokens = set(str(item.get("key", "")).split("-"))
    key_overlap = len(query_set & key_tokens)
    access_bonus = min(float(item.get("access_count", 0)) * 0.05, 0.3)
    return (
        tag_overlap * 3.0
        + token_overlap * 1.5
        + key_overlap * 2.0
        + float(item.get("importance", 0.0))
        + access_bonus
    )


def retrieve_top_k(partition_data: dict[str, Any], query: str, k: int = 3) -> list[dict[str, Any]]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    index = partition_data.get("index", {})
    candidate_indices: set[int] = set()
    for token in query_tokens:
        candidate_indices.update(index.get(token, []))
    if not candidate_indices:
        candidate_indices = set(range(len(partition_data.get("items", []))))

    scored: list[tuple[float, float, int, dict[str, Any]]] = []
    for index_value in sorted(candidate_indices):
        item = partition_data["items"][index_value]
        score = compute_overlap_score(query_tokens, item)
        if score <= 0:
            continue
        scored.append((score, float(item.get("importance", 0.0)), len(item.get("content", "")), item))

    scored.sort(key=lambda row: (-row[0], -row[1], row[3].get("created_at", ""), row[2]))
    if scored and scored[0][0] >= EARLY_RETURN_SCORE:
        return [scored[0][3]]
    return [row[3] for row in scored[: max(1, min(k, MAX_RETRIEVE_K))]]


def query_similarity(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))


def reuse_cached_results(
    partition_data: dict[str, Any],
    query: str,
    working: dict[str, Any],
    partition: str,
) -> list[dict[str, Any]]:
    if working.get("last_partition") != partition:
        return []
    if query_similarity(query, str(working.get("last_query", ""))) < CACHE_SIMILARITY_THRESHOLD:
        return []

    items_by_key = {
        str(item.get("key", "")): item
        for item in partition_data.get("items", [])
        if item.get("key")
    }
    cached: list[dict[str, Any]] = []
    for key in working.get("last_result_keys", [])[:MAX_RETRIEVE_K]:
        item = items_by_key.get(str(key))
        if item is not None:
            cached.append(item)
    return cached


def retrieval_allowed(working: dict[str, Any]) -> bool:
    return int(working.get("step_count", 0)) >= int(working.get("retrieval_cooldown_until", 0))


def mark_retrieval_used(working: dict[str, Any]) -> None:
    working["retrieval_cooldown_until"] = int(working.get("step_count", 0)) + 2


def touch_retrieved_items(items: list[dict[str, Any]], step_count: int) -> None:
    for item in items:
        item["access_count"] = int(item.get("access_count", 0)) + 1
        item["last_accessed_step"] = step_count


def rebuild_index(partition_data: dict[str, Any]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for idx, item in enumerate(partition_data.get("items", [])):
        useful_tokens = []
        for token in item.get("tokens", []):
            if token in STOPWORDS or token in useful_tokens:
                continue
            useful_tokens.append(token)
            if len(useful_tokens) >= 5:
                break
        for token in useful_tokens:
            index.setdefault(token, []).append(idx)
    partition_data["index"] = index
    return index
