#!/usr/bin/env bash
set -euo pipefail
CMD=/mnt/c/Windows/System32/cmd.exe
if [ "$#" -lt 1 ]; then
  echo "usage: winopen.sh <windows-path-or-url>" >&2
  exit 1
fi
"$CMD" /c start "" "$1"
