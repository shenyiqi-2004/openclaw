param([int]$x1, [int]$y1, [int]$x2, [int]$y2)

Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseSim {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint MOUSEEVENTF_MOVE = 0x0001;
}
"@

# Move to start
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x1, $y1)
Start-Sleep -Milliseconds 50

# Left down
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
Start-Sleep -Milliseconds 50

# Move to end
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x2, $y2)
Start-Sleep -Milliseconds 50

# Left up
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
