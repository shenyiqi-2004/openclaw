#!/usr/bin/env bash
# Control mouse bridge server (socket version)
# Usage: mouse-bridge.sh start|stop|status

PID_FILE="/mnt/d/openclaw/mouse_bridge.pid"

case "$1" in
    start)
        # Check if already running
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            if /mnt/c/Windows/System32/cmd.exe /c "tasklist /FI \"PID eq $pid\" 2>nul" | grep -q "$pid"; then
                echo "Mouse bridge already running (PID: $pid)"
                exit 0
            fi
        fi
        
        # Start mouse_bridge.py on Windows (user session)
        # This opens a CMD window - user must keep it open
        /mnt/c/Windows/System32/cmd.exe /c "start cmd /k cd /d D:\openclaw && python mouse_bridge.py"
        sleep 2
        echo "Mouse bridge started (socket server)"
        echo "Keep the Windows CMD window open!"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            /mnt/c/Windows/System32/cmd.exe /c "taskkill /PID $pid /F 2>nul"
            rm -f "$PID_FILE"
            echo "Mouse bridge stopped"
        else
            # Try to kill by process name
            /mnt/c/Windows/System32/cmd.exe /c "taskkill /F /IM python.exe /FI \"WINDOWTITLE eq *mouse_bridge*\" 2>nul" || true
            echo "Mouse bridge stopped"
        fi
        ;;
    status)
        # Try to connect via socket
        resp=$(python3 "$HOME/.openclaw/workspace/skills/windows-bridge/scripts/mouse_client.py" ping 2>/dev/null)
        if echo "$resp" | grep -q '"ok":true'; then
            pos=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Running, cursor at {d['cursor']['x']},{d['cursor']['y']}\")")
            echo "Running - $pos"
        else
            echo "Not running (or cannot connect)"
        fi
        ;;
    *)
        echo "Usage: mouse-bridge.sh {start|stop|status}"
        echo ""
        echo "Before using mouse-ctrl.sh, run: mouse-bridge.sh start"
        ;;
esac
