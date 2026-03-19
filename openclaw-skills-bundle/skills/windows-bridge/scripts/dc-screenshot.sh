#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"
OUT="${2:-C:\Users\w\Desktop\openclaw_capture.png}"
if [ $# -ge 1 ] && [ -n "$1" ]; then
  "$PS" -ExecutionPolicy Bypass -File "$BASE/screen-info.ps1" -Action screenshot -Target "$1" -OutputPath "$OUT"
else
  "$PS" -ExecutionPolicy Bypass -File "$BASE/screen-info.ps1" -Action screenshot -OutputPath "$OUT"
fi
