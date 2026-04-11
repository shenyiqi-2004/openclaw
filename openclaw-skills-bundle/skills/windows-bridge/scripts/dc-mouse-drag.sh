#!/usr/bin/env bash
# Mouse drag from (x1, y1) to (x2, y2)
# Usage: dc-mouse-drag.sh <x1> <y1> <x2> <y2>
set -euo pipefail

if [ $# -lt 4 ]; then
    echo 'usage: dc-mouse-drag.sh <x1> <y1> <x2> <y2>' >&2
    exit 1
fi

X1="$1"
Y1="$2"
X2="$3"
Y2="$4"

cat > /mnt/d/openclaw/_mouse_drag.ps1 << EOF
param([int]\$x1, [int]\$y1, [int]\$x2, [int]\$y2)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseSim {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
}
"@
[MouseSim]::SetCursorPos(\$x1, \$y1)
Start-Sleep -Milliseconds 50
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
Start-Sleep -Milliseconds 100
[MouseSim]::SetCursorPos(\$x2, \$y2)
Start-Sleep -Milliseconds 100
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
Write-Output "Dragged from \$x1,\$y1 to \$x2,\$y2"
EOF

/mnt/c/Windows/System32/cmd.exe /c "cd /d D:\openclaw && powershell.exe -ExecutionPolicy Bypass -File _mouse_drag.ps1 -x1 $X1 -y1 $Y1 -x2 $X2 -y2 $Y2"
