#!/usr/bin/env bash
# Mouse move to specific coordinates
# Usage: dc-mouse-move.sh <x> <y>
set -euo pipefail

if [ $# -lt 2 ]; then
    echo 'usage: dc-mouse-move.sh <x> <y>' >&2
    exit 1
fi

X="$1"
Y="$2"

cat > /mnt/d/openclaw/_mouse_move.ps1 << EOF
param([int]\$x, [int]\$y)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseSim {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
}
"@
[MouseSim]::SetCursorPos(\$x, \$y)
Write-Output "Moved to \$x,\$y"
EOF

/mnt/c/Windows/System32/cmd.exe /c "cd /d D:\openclaw && powershell.exe -ExecutionPolicy Bypass -File _mouse_move.ps1 -x $X -y $Y"
