#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="${HOME}/openclaw/.openclaw/workspace"
WINDOWS_DIR="${WORKSPACE_DIR}/gui-desktop-control/windows"
PY_FILE="${WINDOWS_DIR}/mouse_bridge.py"
BAT_FILE="${WINDOWS_DIR}/run_mouse_bridge.bat"
PS_EXE="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

if [ ! -f "$PY_FILE" ]; then
  echo "mouse_bridge.py not found: $PY_FILE" >&2
  exit 1
fi

if [ ! -f "$BAT_FILE" ]; then
  echo "run_mouse_bridge.bat not found: $BAT_FILE" >&2
  exit 1
fi

ps_check() {
  "$PS_EXE" -NoProfile -Command "\
  \$p = Get-CimInstance Win32_Process | Where-Object { \
    \$_.Name -match '^(python|pythonw|py|pyw)\\.exe$' -and \
    \$_.CommandLine -match 'mouse_bridge\\.py' \
  }; \
  if (\$p) { 'RUNNING ' + (@(\$p).Count) } else { 'STOPPED 0' }" | tr -d '\r' | tail -n 1
}

status="$(ps_check || true)"
state="${status%% *}"
count="${status##* }"

if [ "$state" = "RUNNING" ]; then
  echo "mouse bridge already running ($count process)"
  exit 0
fi

BAT_WIN="$(wslpath -w "$BAT_FILE")"
"$PS_EXE" -NoProfile -Command "Start-Process -FilePath 'C:\\Windows\\System32\\cmd.exe' -ArgumentList '/k', ('\"' + '$BAT_WIN' + '\"')" >/dev/null

sleep 4

status="$(ps_check || true)"
state="${status%% *}"
count="${status##* }"

if [ "$state" != "RUNNING" ]; then
  echo "mouse bridge did not start" >&2
  exit 1
fi

echo "mouse bridge started ($count process)"
