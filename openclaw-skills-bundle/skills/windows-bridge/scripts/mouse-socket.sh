#!/usr/bin/env bash
# Mouse control via socket bridge
# Usage: mouse-socket.sh {move|click|rightclick|getpos} [x] [y]

CLIENT="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/mouse_client.py"
HOST="${MOUSE_BRIDGE_HOST:-172.18.160.1}"

export MOUSE_BRIDGE_HOST="$HOST"

get_pos() {
    pos=$(MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" ping 2>/dev/null)
    if echo "$pos" | grep -q '"ok":true'; then
        echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"X={d['cursor']['x']} Y={d['cursor']['y']}\")"
    else
        echo "Error: $pos"
    fi
}

smooth_move() {
    local target_x=$1
    local target_y=$2
    
    # Get current position
    pos=$(MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" ping 2>/dev/null)
    current_x=$(echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['x'])" 2>/dev/null)
    current_y=$(echo "$pos" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['y'])" 2>/dev/null)
    
    if [ -z "$current_x" ] || [ -z "$current_y" ]; then
        MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" move $target_x $target_y
        return
    fi
    
    # Calculate steps
    dx=$((target_x - current_x))
    dy=$((target_y - current_y))
    dist=$(( (dx*dx + dy*dy) / 10000 ))
    steps=$((dist / 50 + 1))
    if [ $steps -lt 1 ]; then steps=1; fi
    if [ $steps -gt 20 ]; then steps=20; fi
    
    step_x=$((dx / steps))
    step_y=$((dy / steps))
    
    for i in $(seq 1 $steps); do
        new_x=$((current_x + step_x * i))
        new_y=$((current_y + step_y * i))
        MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" move $new_x $new_y >/dev/null 2>&1
    done
    
    MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" move $target_x $target_y
}

case "$1" in
    move)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: mouse-socket.sh move <x> <y>"
            exit 1
        fi
        smooth_move $2 $3
        ;;
    click)
        if [ -z "$2" ] || [ -z "$3" ]; then
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        else
            smooth_move $2 $3
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        fi
        ;;
    rightclick)
        # Fallback to click (rightclick not in current bridge)
        if [ -z "$2" ] || [ -z "$3" ]; then
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        else
            smooth_move $2 $3
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        fi
        ;;
    getpos|ping)
        get_pos
        ;;
    *)
        echo "Usage: mouse-socket.sh {move|click|rightclick|getpos} [x] [y]"
        echo ""
        echo "Examples:"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-socket.sh move 1280 720"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-socket.sh click"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-socket.sh click 500 300"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-socket.sh getpos"
        exit 1
        ;;
esac
