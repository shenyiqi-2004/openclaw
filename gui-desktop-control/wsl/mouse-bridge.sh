#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WIN_DIR_WIN="$(wslpath -w "$ROOT_DIR/windows")"
case "${1:-}" in
  start)
    /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'C:\\Windows\\py.exe' -ArgumentList '-3','mouse_bridge.py' -WorkingDirectory '$WIN_DIR_WIN'"
    echo "started: mouse_bridge.py launched from $WIN_DIR_WIN"
    ;;
  status)
    python3 "$SCRIPT_DIR/mouse_client.py" ping
    ;;
  *)
    echo "Usage: mouse-bridge.sh {start|status}"
    exit 1
    ;;
esac
