#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then echo 'usage: dc-type-text-slow.sh <text> [delay_ms]' >&2; exit 1; fi
TEXT="$1"
DELAY="${2:-120}"
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"
python3 - "$TEXT" "$DELAY" <<'PY' | while IFS= read -r ch; do
import sys, time
text=sys.argv[1]
for ch in text:
    print(ch)
PY
  "$PS" -ExecutionPolicy Bypass -File "$BASE/input-sim.ps1" -Action type-text -Text "$ch" >/dev/null
  python3 - <<PY
import time
time.sleep(${DELAY}/1000)
PY
done
echo "Typed slowly: $TEXT"
