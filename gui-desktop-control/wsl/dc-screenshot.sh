#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WIN_PS="$(wslpath -w "$SCRIPT_DIR/../windows/screen-info.ps1")"
OUT="${2:-C:\Users\Public\gui_desktop_control_capture.png}"
if [ $# -ge 1 ] && [ -n "$1" ]; then
  "$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -Action screenshot -Target "$1" -OutputPath "$OUT"
else
  "$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -Action screenshot -OutputPath "$OUT"
fi
