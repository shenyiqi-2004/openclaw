#!/usr/bin/env bash
set -euo pipefail
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
if [ "$#" -lt 1 ]; then
  echo "usage: wincheck.sh <process-name-substring>" >&2
  exit 1
fi
name="$1"
"$PS" -Command "Get-Process | Where-Object { \$_.ProcessName -like '*$name*' } | Select-Object -First 20 ProcessName,Id | Format-Table -HideTableHeaders"
