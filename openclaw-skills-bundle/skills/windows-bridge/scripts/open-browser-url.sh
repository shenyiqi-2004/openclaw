#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "usage: open-browser-url.sh <url>" >&2
  exit 1
fi
"$HOME/.openclaw/workspace/skills/windows-bridge/scripts/winopen.sh" "$1"
