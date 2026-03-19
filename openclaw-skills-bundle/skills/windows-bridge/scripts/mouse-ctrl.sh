#!/usr/bin/env bash
# Mouse Control via Socket Bridge
# Uses mouse_client.py to communicate with Windows mouse_bridge.py

CLIENT="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/mouse_client.py"
HOST="${MOUSE_BRIDGE_HOST:-172.18.160.1}"

# Export for client
export MOUSE_BRIDGE_HOST="$HOST"

get_pos() {
    resp=$(MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" ping 2>/dev/null)
    if echo "$resp" | grep -q '"ok":true'; then
        x=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['x'])")
        y=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['y'])")
        echo "X=$x Y=$y"
    else
        echo "X=? Y=?"
    fi
}

smooth_move() {
    local target_x=$1
    local target_y=$2
    
    # Get current position
    resp=$(MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" ping 2>/dev/null)
    if echo "$resp" | grep -q '"ok":true'; then
        current_x=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['x'])")
        current_y=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['cursor']['y'])")
    else
        current_x=0
        current_y=0
    fi
    
    # Calculate steps (move gradually)
    local dx=$((target_x - current_x))
    local dy=$((target_y - current_y))
    local dist=$(( (dx*dx + dy*dy) / 10000 ))
    local steps=$((dist / 50 + 1))
    if [ $steps -lt 1 ]; then steps=1; fi
    if [ $steps -gt 20 ]; then steps=20; fi
    
    local step_x=$((dx / steps))
    local step_y=$((dy / steps))
    
    for i in $(seq 1 $steps); do
        local new_x=$((current_x + step_x * i))
        local new_y=$((current_y + step_y * i))
        MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" move $new_x $new_y >/dev/null 2>&1
    done
    
    # Final position
    MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" move $target_x $target_y >/dev/null 2>&1
}

case "$1" in
    move)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: mouse-ctrl.sh move <x> <y>"
            exit 1
        fi
        smooth_move $2 $3
        ;;
    click)
        if [ -z "$2" ]; then
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        else
            smooth_move $2 $3
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        fi
        ;;
    rightclick)
        # Rightclick not implemented in current bridge, fall back to move+click
        if [ -z "$2" ]; then
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        else
            smooth_move $2 $3
            MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" click
        fi
        ;;
    getpos)
        get_pos
        ;;
    ping)
        MOUSE_BRIDGE_HOST="$HOST" python3 "$CLIENT" ping
        ;;
    *)
        echo "Usage: mouse-ctrl.sh {move|click|rightclick|getpos|ping} [x] [y]"
        echo ""
        echo "Examples:"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-ctrl.sh move 100 100"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-ctrl.sh click"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-ctrl.sh click 500 300"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-ctrl.sh getpos"
        echo "  MOUSE_BRIDGE_HOST=172.18.160.1 mouse-ctrl.sh ping"
        ;;
esac
