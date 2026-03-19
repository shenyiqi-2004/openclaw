---
name: windows-bridge
description: Bridge from WSL/OpenClaw into Windows programs and files. Use whenever the user wants to launch a Windows .exe, open a file/folder in a Windows app, run a Windows shell command from WSL, or work around 'cmd.exe/powershell not found' / WSL→Windows interop issues. Especially use for OpenClaw running inside WSL where Windows GUI apps (DeckBuild, TonyPlot, Office, Explorer, VS Code, browsers) must be launched from Linux-side tools.
---

# Windows Bridge

Use this skill to reliably launch Windows apps from WSL without assuming `cmd.exe` or `powershell.exe` is on PATH.

## Core rule
Always call Windows executables by **full path**:
- `/mnt/c/Windows/System32/cmd.exe`
- `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`

Do **not** rely on bare `cmd.exe` or `powershell` in WSL.

## Preferred methods

### 1) Launch a GUI app once
Use PowerShell `Start-Process`:
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command \
  "Start-Process 'D:\\Path\\App.exe' -ArgumentList 'arg1','arg2'"
```

### 2) Open file/folder/URL with Windows default handler
```bash
/mnt/c/Windows/System32/cmd.exe /c start "" "C:\\path\\to\\file"
```

### 3) Run a Windows shell command
```bash
/mnt/c/Windows/System32/cmd.exe /c "your command here"
```

## Critical for mouse/keyboard automation
- **PowerShell scripts MUST be saved to `D:\openclaw\`** (not WSL path) for mouse/keyboard to work properly
- Execute via: `cmd.exe /c "cd /d D:\openclaw && powershell.exe -ExecutionPolicy Bypass -File script.ps1"`
- Test mouse with screenshot: use `capture_with_cursor.ps1` in D:\openclaw
- For keyboard input, add delays between keystrokes to prevent character stacking

## Path conversion
Convert paths carefully:
- WSL: `/mnt/c/Users/w/Desktop/test.txt`
- Windows: `C:\Users\w\Desktop\test.txt`

If needed, use the helper script in `scripts/winpath.py`.

## Helpers
- `scripts/winlaunch.sh` — launch a Windows executable safely from WSL
- `scripts/winpath.py` — convert `/mnt/<drive>/...` to `X:\...`


## Extra helpers
- `scripts/wincheck.sh <name>` — check whether a Windows process matching `<name>` is already running
- `scripts/winopen.sh <path-or-url>` — open a Windows path, folder, file, or URL with default handler

## Recommended workflow for GUI apps
1. Convert WSL paths to Windows paths if needed
2. If duplicate launch would be annoying, run `wincheck.sh` first
3. Launch with `winlaunch.sh` / PowerShell `Start-Process`
4. For folders/files/URLs, prefer `winopen.sh`

## Common examples
### Open Explorer to a folder
```bash
~/.openclaw/workspace/skills/windows-bridge/scripts/winopen.sh "C:\Users\w\Desktop\silvaco\实验三"
```

### Launch VS Code on a Windows folder
```bash
~/.openclaw/workspace/skills/windows-bridge/scripts/winlaunch.sh "C:\Users\w\AppData\Local\Programs\Microsoft VS Code\Code.exe" "C:\Users\w\Desktop"
```

### Check if DeckBuild is already open
```bash
~/.openclaw/workspace/skills/windows-bridge/scripts/wincheck.sh deckbuild
```

## Example: Silvaco DeckBuild
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command \
  "Start-Process 'D:\\TCAD\\etc\\GuiAppStarter.exe' -ArgumentList '-lib-dir-name deckbuild','-exe-name deckbuild'"
```

## When the user wants full desktop control
This skill is only a **bridge**. It can launch and invoke Windows-side commands, but it does not provide vision/click automation by itself. For true GUI clicking / screen reading, combine with a desktop automation tool if available.


## Ready-made wrappers
- `scripts/launch-deckbuild.sh` — launch Silvaco DeckBuild with the known local path
- `scripts/open-silvaco-exp3.sh` — open `C:\Users\w\Desktop\silvaco\实验三`
- `scripts/open-browser-url.sh <url>` — open a URL in Windows default browser

Use these wrappers whenever the target matches, instead of rebuilding the command from scratch.


## Mouse control (working solution)

**IMPORTANT**: For mouse control to work, you must first run the bridge server on Windows:

1. On Windows (as Administrator), run:
   ```
   powershell.exe -ExecutionPolicy Bypass -File D:\openclaw\mouse_bridge_server.ps1
   ```
2. Keep that window running

Then use `scripts/mouse-ctrl.sh`:
- `scripts/mouse-ctrl.sh move <x> <y>` — Move mouse to coordinates
- `scripts/mouse-ctrl.sh click [x] [y]` — Click (at optional coordinates)
- `scripts/mouse-ctrl.sh rightclick [x] [y]` — Right click
- `scripts/mouse-ctrl.sh getpos` — Get current position

### Auto language detection & IME switching
- `scripts/dc-type-text-auto-ime.sh <text>` — **Automatically detects language and switches IME before typing**
  - If text contains Chinese → switches to Chinese IME
  - If text is English only → switches to English IME
  - Uses Ctrl+Shift to toggle IME

### Manual keyboard control
- `scripts/dc-send-keys.sh <keys>` — Send keyboard shortcuts (e.g., "Ctrl+Shift", "Ctrl+C", "Alt+F4")
- `scripts/dc-type-text.sh <text>` — Type text (no IME switching)
- `scripts/dc-type-text-slow.sh <text>` — Type text with delays between characters

### Window control
- `scripts/dc-list-windows.sh` — List all open windows
- `scripts/dc-focus-window.sh <partial-title>` — Focus a window by title

### Screenshot
- `scripts/dc-screenshot.sh [partial-title] [output-path]` — Take screenshot

**IMPORTANT**: Use `dc-type-text-auto-ime.sh` for text input — it automatically detects whether the text contains Chinese and switches IME accordingly. Do not assume the input method is already in the correct state.
