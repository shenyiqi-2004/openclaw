#!/usr/bin/env bash
set -euo pipefail
[ $# -ge 1 ] || { echo 'usage: dc-type-text.sh <text>' >&2; exit 1; }
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WIN_PS="$(wslpath -w "$SCRIPT_DIR/../windows/input-sim.ps1")"
"$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -Action type-text -Text "$1"
