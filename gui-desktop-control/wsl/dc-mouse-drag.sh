#!/usr/bin/env bash
set -euo pipefail
[ $# -eq 4 ] || { echo 'usage: dc-mouse-drag.sh <x1> <y1> <x2> <y2>' >&2; exit 1; }
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WIN_PS="$(wslpath -w "$SCRIPT_DIR/../windows/drag.ps1")"
"$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -x1 "$1" -y1 "$2" -x2 "$3" -y2 "$4"
