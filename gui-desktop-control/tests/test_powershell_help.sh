#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$PS" -ExecutionPolicy Bypass -File "$(wslpath -w "$SCRIPT_DIR/../windows/input-sim.ps1")" -Action help
"$PS" -ExecutionPolicy Bypass -File "$(wslpath -w "$SCRIPT_DIR/../windows/app-control.ps1")" -Action help
"$PS" -ExecutionPolicy Bypass -File "$(wslpath -w "$SCRIPT_DIR/../windows/screen-info.ps1")" -Action help
