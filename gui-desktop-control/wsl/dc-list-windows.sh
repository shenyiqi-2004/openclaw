#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WIN_PS="$(wslpath -w "$SCRIPT_DIR/../windows/app-control.ps1")"
"$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -Action list-windows
