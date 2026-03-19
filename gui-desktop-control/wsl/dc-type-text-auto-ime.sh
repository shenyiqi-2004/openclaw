#!/usr/bin/env bash
set -euo pipefail
[ $# -ge 1 ] || { echo 'usage: dc-type-text-auto-ime.sh <text>' >&2; exit 1; }
TEXT="$1"
contains_chinese() { echo "$1" | grep -qP '[\x{4E00}-\x{9FFF}\x{3400}-\x{4DBF}]'; }
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WIN_PS="$(wslpath -w "$SCRIPT_DIR/../windows/input-sim.ps1")"
if contains_chinese "$TEXT"; then
  "$PS" -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^+'); Start-Sleep -Milliseconds 100" >/dev/null
fi
"$PS" -ExecutionPolicy Bypass -File "$WIN_PS" -Action type-text -Text "$TEXT"
