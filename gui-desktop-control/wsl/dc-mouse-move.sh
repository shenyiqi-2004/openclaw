#!/usr/bin/env bash
set -euo pipefail
[ $# -eq 2 ] || { echo 'usage: dc-mouse-move.sh <x> <y>' >&2; exit 1; }
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/mouse-socket.sh" move "$1" "$2"
