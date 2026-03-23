from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from core.backends.base import BackendStatus
from core.runtime_paths import resolve_runtime_config_path, resolve_runtime_root


class LanceDbProMemoryBackend:
    def __init__(
        self,
        base_dir: str | Path,
        runtime_config_path: str | Path | None = None,
        bridge_script_path: str | Path | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        runtime_root = resolve_runtime_root()
        self.runtime_config_path = (
            Path(runtime_config_path) if runtime_config_path else resolve_runtime_config_path(runtime_root)
        )
        self.bridge_script_path = (
            Path(bridge_script_path)
            if bridge_script_path
            else runtime_root / "src" / "infra" / "memory-lancedb-pro-bridge.ts"
        )
        self.node_bin = shutil.which("node")
        self._status = self._detect_status()

    def _detect_status(self) -> BackendStatus:
        if not self.runtime_config_path.exists():
            return BackendStatus(
                name="memory_lancedb_pro",
                available=False,
                canonical=False,
                mode="unavailable",
                reason="runtime config missing",
            )
        try:
            config = json.loads(self.runtime_config_path.read_text(encoding="utf-8"))
        except Exception:
            return BackendStatus(
                name="memory_lancedb_pro",
                available=False,
                canonical=False,
                mode="unavailable",
                reason="runtime config unreadable",
            )

        plugins = config.get("plugins", {})
        slots = plugins.get("slots", {})
        entries = plugins.get("entries", {})
        if slots.get("memory") != "memory-lancedb-pro":
            return BackendStatus(
                name="memory_lancedb_pro",
                available=False,
                canonical=False,
                mode="unavailable",
                reason="memory slot not assigned to memory-lancedb-pro",
            )
        entry = entries.get("memory-lancedb-pro") or {}
        if not entry.get("enabled", False):
            return BackendStatus(
                name="memory_lancedb_pro",
                available=False,
                canonical=False,
                mode="unavailable",
                reason="plugin disabled",
            )

        db_path = str((entry.get("config") or {}).get("dbPath", "")).strip()
        if not db_path:
            return BackendStatus(
                name="memory_lancedb_pro",
                available=False,
                canonical=False,
                mode="unavailable",
                reason="dbPath missing",
            )

        if not self.bridge_script_path.exists():
            return BackendStatus(
                name="memory_lancedb_pro",
                available=True,
                canonical=True,
                mode="detect-only",
                reason="plugin active; no sidecar bridge script found",
            )
        if not self.node_bin:
            return BackendStatus(
                name="memory_lancedb_pro",
                available=True,
                canonical=True,
                mode="detect-only",
                reason="plugin active; node runtime unavailable for bridge",
            )

        return BackendStatus(
            name="memory_lancedb_pro",
            available=True,
            canonical=True,
            mode="bridge",
            reason="plugin active and bridge available",
        )

    def status(self) -> BackendStatus:
        return self._status

    def get_backend_identity(self) -> dict[str, object]:
        return self._status.to_dict()

    def _run_bridge(self, command: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._status.mode != "bridge" or not self.node_bin:
            return {"ok": False, "reason": "bridge-not-configured"}
        full_payload = dict(payload)
        full_payload["runtime_config_path"] = str(self.runtime_config_path)
        completed = subprocess.run(
            [
                self.node_bin,
                "--import",
                "tsx",
                str(self.bridge_script_path),
                command,
            ],
            input=json.dumps(full_payload),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0 and not completed.stdout.strip():
            return {"ok": False, "reason": completed.stderr.strip() or f"bridge-exit:{completed.returncode}"}
        try:
            response = json.loads(completed.stdout.strip() or "{}")
        except Exception:
            return {"ok": False, "reason": "bridge-invalid-json", "stderr": completed.stderr.strip()}
        return response

    def recall_memory(self, *, query: str, scope: dict, limit: int) -> list[dict]:
        response = self._run_bridge("recall", {"query": query, "limit": limit, "scope": scope})
        if not response.get("ok"):
            return []
        items = response.get("items", [])
        return items if isinstance(items, list) else []

    def store_memory(self, *, text: str, metadata: dict) -> dict:
        kind = str(metadata.get("kind", "")).strip() or None
        response = self._run_bridge(
            "store",
            {
                "text": text,
                "kind": kind,
                "importance": float(metadata.get("importance", 0.6)),
                "tags": metadata.get("tags", []),
            },
        )
        if not response.get("ok"):
            return {"stored": False, "backend": "memory_lancedb_pro", "reason": response.get("reason", "bridge-failed")}
        return {
            "stored": bool(response.get("stored", False)),
            "backend": "memory_lancedb_pro",
            "reason": str(response.get("reason", "")),
            "item": response.get("item"),
            "duplicate_id": response.get("duplicate_id"),
        }

    def update_memory(self, *, memory_id: str, patch: dict) -> dict:
        response = self._run_bridge(
            "update",
            {
                "memory_id": memory_id,
                "text": patch.get("text"),
                "kind": patch.get("kind"),
                "importance": patch.get("importance"),
            },
        )
        if not response.get("ok"):
            return {"updated": False, "backend": "memory_lancedb_pro", "reason": response.get("reason", "bridge-failed")}
        return {
            "updated": bool(response.get("updated", False)),
            "backend": "memory_lancedb_pro",
            "reason": str(response.get("reason", "")),
            "item": response.get("item"),
        }

    def forget_memory(self, *, memory_id: str) -> dict:
        response = self._run_bridge("forget", {"memory_id": memory_id})
        if not response.get("ok"):
            return {"deleted": False, "backend": "memory_lancedb_pro", "reason": response.get("reason", "bridge-failed")}
        return {
            "deleted": bool(response.get("deleted", False)),
            "backend": "memory_lancedb_pro",
            "reason": str(response.get("reason", "")),
        }

    def delete_memory(self, *, memory_id: str) -> dict:
        return self.forget_memory(memory_id=memory_id)

    def get_memory_stats(self) -> dict:
        response = self._run_bridge("stats", {})
        if response.get("ok"):
            return {
                "backend": "memory_lancedb_pro",
                "available": self._status.available,
                "canonical": self._status.canonical,
                "mode": self._status.mode,
                "reason": self._status.reason,
                "stats": response.get("stats", {}),
                "config": response.get("config", {}),
            }
        return {
            "backend": "memory_lancedb_pro",
            "available": self._status.available,
            "canonical": self._status.canonical,
            "mode": self._status.mode,
            "reason": self._status.reason,
        }
