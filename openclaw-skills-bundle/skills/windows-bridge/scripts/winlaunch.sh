#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "usage: winlaunch.sh <windows-exe-path> [args ...]" >&2
  exit 1
fi
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
EXE="$1"
shift || true
if [ "$#" -eq 0 ]; then
  "$PS" -Command "Start-Process '$EXE'"
else
  args=$(printf "'%s'," "$@")
  args=${args%,}
  "$PS" -Command "Start-Process '$EXE' -ArgumentList $args"
fi
