---
name: gui-desktop-control
description: Use the local gui-desktop-control toolkit for Windows desktop GUI automation from OpenClaw or WSL. Use when the user wants mouse control, keyboard input, screenshots, window focus or listing, or mentions gui-desktop-control, mouse_bridge.py, run_mouse_bridge.bat, dc-screenshot.sh, dc-send-keys.sh, or dc-type-text.sh.
---

# GUI Desktop Control

Use this skill before any Windows desktop GUI control task.

## Workflow

1. Ensure the Windows mouse bridge is available:

```bash
~/.openclaw/workspace/skills/gui-desktop-control/scripts/start_mouse_bridge.sh
```

2. Reuse the existing toolkit scripts under:
   `~/.openclaw/workspace/gui-desktop-control/wsl/`

3. Use the right entrypoint for the task:
   `mouse-socket.sh` or `dc-mouse-*` for mouse actions
   `dc-send-keys.sh`, `dc-type-text.sh`, `dc-type-text-auto-ime.sh` for keyboard input
   `dc-screenshot.sh` for screenshots
   `dc-list-windows.sh` and `dc-focus-window.sh` for window management

4. Treat screenshots as model input. `gui-desktop-control` captures the image; OpenClaw's vision-capable model interprets it.

## Rules

- Never start a second `mouse_bridge.py` process.
- Never stop the bridge just because a task is done.
- The bridge is long-lived and small enough to keep running once started.
- Run the startup script from WSL, not the Python file directly from Linux.
- The Windows bridge must run in the logged-in desktop session.

## Key Commands

```bash
# Start or reuse mouse bridge
~/.openclaw/workspace/skills/gui-desktop-control/scripts/start_mouse_bridge.sh

# Mouse
~/.openclaw/workspace/gui-desktop-control/wsl/mouse-socket.sh move 800 500
~/.openclaw/workspace/gui-desktop-control/wsl/mouse-socket.sh click 800 500
~/.openclaw/workspace/gui-desktop-control/wsl/dc-mouse-drag.sh 200 300 800 300

# Keyboard
~/.openclaw/workspace/gui-desktop-control/wsl/dc-type-text.sh "hello world"
~/.openclaw/workspace/gui-desktop-control/wsl/dc-type-text-auto-ime.sh "你好，world"
~/.openclaw/workspace/gui-desktop-control/wsl/dc-send-keys.sh "Ctrl+L"

# Windows and screenshots
~/.openclaw/workspace/gui-desktop-control/wsl/dc-list-windows.sh
~/.openclaw/workspace/gui-desktop-control/wsl/dc-focus-window.sh "Notepad"
~/.openclaw/workspace/gui-desktop-control/wsl/dc-screenshot.sh
~/.openclaw/workspace/gui-desktop-control/wsl/dc-screenshot.sh "Notepad"
```

## Notes

- Screenshot understanding comes from the configured OpenClaw model, not a separate OCR tool in this skill.
- `run_mouse_bridge.bat` is the Windows-side launcher for `mouse_bridge.py`.
- The toolkit also includes PowerShell helpers such as `input-sim.ps1`, `screen-info.ps1`, and `app-control.ps1`; prefer the WSL wrapper scripts unless there is a specific reason to call the Windows files directly.
