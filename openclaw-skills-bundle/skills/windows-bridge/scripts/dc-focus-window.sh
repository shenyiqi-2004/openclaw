#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then echo 'usage: dc-focus-window.sh <partial-window-title>' >&2; exit 1; fi
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"
"$PS" -ExecutionPolicy Bypass -File "$BASE/app-control.ps1" -Action focus -Target "$1"
