#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"
"$PS" -ExecutionPolicy Bypass -File "$BASE/app-control.ps1" -Action list-windows
