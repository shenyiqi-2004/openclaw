#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WIN_DIR_WIN='D:\gui-desktop-control\windows'
case "${1:-}" in
  start)
    /mnt/c/Windows/System32/cmd.exe /c "start cmd /k cd /d $WIN_DIR_WIN && python mouse_bridge.py"
    echo "started: keep the Windows CMD window open"
    ;;
  status)
    python3 "$SCRIPT_DIR/mouse_client.py" ping
    ;;
  *)
    echo "Usage: mouse-bridge.sh {start|status}"
    exit 1
    ;;
esac
