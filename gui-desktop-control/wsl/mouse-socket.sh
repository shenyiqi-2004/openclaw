#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="$SCRIPT_DIR/mouse_client.py"
HOST="${MOUSE_BRIDGE_HOST:-172.18.160.1}"
export MOUSE_BRIDGE_HOST="$HOST"
get_pos() {
    pos=$(python3 "$CLIENT" ping 2>/dev/null)
    if echo "$pos" | grep -q '"ok": true\|"ok":true'; then
        echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"X={d['cursor']['x']} Y={d['cursor']['y']}\")"
    else
        echo "Error: $pos"
        return 1
    fi
}
smooth_move() {
    local target_x=$1 target_y=$2
    pos=$(python3 "$CLIENT" ping 2>/dev/null || true)
    current_x=$(echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['x'])" 2>/dev/null || true)
    current_y=$(echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['y'])" 2>/dev/null || true)
    if [ -z "${current_x:-}" ] || [ -z "${current_y:-}" ]; then
        python3 "$CLIENT" move "$target_x" "$target_y"
        return
    fi
    dx=$((target_x - current_x)); dy=$((target_y - current_y))
    dist=$(((dx*dx + dy*dy) / 10000)); steps=$((dist / 50 + 1))
    [ $steps -lt 1 ] && steps=1
    [ $steps -gt 20 ] && steps=20
    step_x=$((dx / steps)); step_y=$((dy / steps))
    for i in $(seq 1 $steps); do
        new_x=$((current_x + step_x * i)); new_y=$((current_y + step_y * i))
        python3 "$CLIENT" move "$new_x" "$new_y" >/dev/null 2>&1 || true
    done
    python3 "$CLIENT" move "$target_x" "$target_y"
}
case "${1:-}" in
  move) [ $# -eq 3 ] || { echo "Usage: mouse-socket.sh move <x> <y>"; exit 1; }; smooth_move "$2" "$3" ;;
  click) if [ $# -eq 1 ]; then python3 "$CLIENT" click; elif [ $# -eq 3 ]; then smooth_move "$2" "$3"; python3 "$CLIENT" click; else echo "Usage: mouse-socket.sh click [x y]"; exit 1; fi ;;
  getpos|ping) get_pos ;;
  *) echo "Usage: mouse-socket.sh {move|click|getpos|ping} [x] [y]"; exit 1 ;;
esac
