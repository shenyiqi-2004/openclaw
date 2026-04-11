#!/usr/bin/env bash
# Mouse click at specific coordinates
# Usage: dc-mouse-click.sh <x> <y> [left|right|middle] [double]
set -euo pipefail

if [ $# -lt 2 ]; then
    echo 'usage: dc-mouse-click.sh <x> <y> [left|right|middle] [double]' >&2
    exit 1
fi

X="$1"
Y="$2"
BUTTON="${3:-left}"
DOUBLE="${4:-}"

# Write PowerShell script to D:\openclaw (required for mouse control to work)
cat > /mnt/d/openclaw/_mouse_click.ps1 << 'EOF'
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
    public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    public const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    public const uint MOUSEEVENTF_MIDDLEUP = 0x0040;
}
"@
param([int]$x, [int]$y, [string]$button="left", [switch]$double)
[MouseSim]::SetCursorPos($x, $y)
Start-Sleep -Milliseconds 50
$down = if ($button -eq "right") { [MouseSim]::MOUSEEVENTF_RIGHTDOWN } elseif ($button -eq "middle") { [MouseSim]::MOUSEEVENTF_MIDDLEDOWN } else { [MouseSim]::MOUSEEVENTF_LEFTDOWN }
$up = if ($button -eq "right") { [MouseSim]::MOUSEEVENTF_RIGHTUP } elseif ($button -eq "middle") { [MouseSim]::MOUSEEVENTF_MIDDLEUP } else { [MouseSim]::MOUSEEVENTF_LEFTUP }
[MouseSim]::mouse_event($down, 0, 0, 0, 0)
if ($double) { Start-Sleep -Milliseconds 50; [MouseSim]::mouse_event($down, 0, 0, 0, 0) }
Start-Sleep -Milliseconds 50
[MouseSim]::mouse_event($up, 0, 0, 0, 0)
Write-Output "Clicked $button at $x,$y"
EOF

# Fix the script - add param at top
cat > /mnt/d/openclaw/_mouse_click.ps1 << EOF
param([int]\$x, [int]\$y, [string]\$button="left", [switch]\$double)
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
    public const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    public const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    public const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
    public const uint MOUSEEVENTF_MIDDLEUP = 0x0040;
}
"@
[MouseSim]::SetCursorPos(\$x, \$y)
Start-Sleep -Milliseconds 50
\$down = if (\$button -eq "right") { [MouseSim]::MOUSEEVENTF_RIGHTDOWN } elseif (\$button -eq "middle") { [MouseSim]::MOUSEEVENTF_MIDDLEDOWN } else { [MouseSim]::MOUSEEVENTF_LEFTDOWN }
\$up = if (\$button -eq "right") { [MouseSim]::MOUSEEVENTF_RIGHTUP } elseif (\$button -eq "middle") { [MouseSim]::MOUSEEVENTF_MIDDLEUP } else { [MouseSim]::MOUSEEVENTF_LEFTUP }
[MouseSim]::mouse_event(\$down, 0, 0, 0, 0)
if (\$double) { Start-Sleep -Milliseconds 50; [MouseSim]::mouse_event(\$down, 0, 0, 0, 0) }
Start-Sleep -Milliseconds 50
[MouseSim]::mouse_event(\$up, 0, 0, 0, 0)
Write-Output "Clicked \$button at \$x,\$y"
EOF

/mnt/c/Windows/System32/cmd.exe /c "cd /d D:\openclaw && powershell.exe -ExecutionPolicy Bypass -File _mouse_click.ps1 -x $X -y $Y -button $BUTTON $DOUBLE"
