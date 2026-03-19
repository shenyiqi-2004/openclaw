#!/usr/bin/env bash
set -euo pipefail
if [ $# -eq 0 ]; then
  SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  "$SCRIPT_DIR/mouse-socket.sh" click
elif [ $# -eq 2 ]; then
  SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  "$SCRIPT_DIR/mouse-socket.sh" click "$1" "$2"
else
  echo 'usage: dc-mouse-click.sh [x y]' >&2
  exit 1
fi
