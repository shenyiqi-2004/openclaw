#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then echo 'usage: dc-type-text.sh <text>' >&2; exit 1; fi
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"
"$PS" -ExecutionPolicy Bypass -File "$BASE/input-sim.ps1" -Action type-text -Text "$1"
