Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class MouseSim {
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
}
"@
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(300, 300)
Start-Sleep -Milliseconds 100
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
Start-Sleep -Milliseconds 100
[MouseSim]::mouse_event([MouseSim]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
Write-Output "Clicked at 300,300"
