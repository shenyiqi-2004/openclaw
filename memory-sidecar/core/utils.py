from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def ensure_file(path: str | Path, default_data: Any) -> None:
    """Create a JSON file with default data when it does not exist."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        save_json(file_path, default_data)


def load_json(path: str | Path) -> Any:
    """Load and parse JSON from a file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str | Path, data: Any) -> None:
    """Write JSON data to a file using UTF-8 and stable formatting."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
    last_error: OSError | None = None
    for _ in range(5):
        try:
            temp_path.replace(file_path)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.05)
    if last_error is not None:
        raise last_error


def now_iso() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value into the given inclusive range."""
    return max(min_value, min(max_value, value))


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    """Deduplicate items while preserving original order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_text(text: str) -> str:
    """Lowercase text, trim it, and collapse internal whitespace."""
    lowered = text.lower().strip()
    return re.sub(r"\s+", " ", lowered)


def compact_step_label(text: str) -> str:
    """Convert a step description into a short repetition-friendly label."""
    cleaned = normalize_text(text)
    cleaned = re.sub(r"[^a-z0-9\u4e00-\u9fff\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if re.search(r"[\u4e00-\u9fff]", cleaned) and " " not in cleaned:
        return cleaned[:12]
    words = [word for word in cleaned.split(" ") if word][:6]
    return " ".join(words)
