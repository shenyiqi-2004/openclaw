# openclaw-gui-desktop-control

A practical **Windows desktop GUI control toolkit** for **WSL / OpenClaw** workflows.

> This is **not** just a thin SendKeys wrapper.
> It is a **Windows GUI keyboard/mouse adaptation bridge** built for **OpenClaw running in WSL**.

It bundles a local-first bridge for controlling Windows GUI apps from WSL:
- **Mouse**: move, click, drag
- **Keyboard**: type text, send shortcuts, and handle basic IME-aware input adaptation
- **Screenshots**: full screen or target window
- **Window management**: list, focus, move, resize

## Why this exists

If all you need is plain `SendKeys`, this repo is overkill.
The point here is the **adaptation layer**: making OpenClaw/WSL control a real Windows desktop more reliably across mouse actions, keyboard input, IME switching, screenshots, and window focus.

Controlling Windows desktop apps from WSL is awkward:
- direct WSL -> GUI interaction is inconsistent
- one-off PowerShell scripts are noisy for frequent mouse actions
- different actions have different "most stable" implementations

This repo uses a hybrid design:
- a lightweight **socket bridge** for reliable mouse control
- **PowerShell + Win32** helpers for text input, screenshots, and windows
- an extra **keyboard adaptation layer** for practical Chinese/English input workflows

That split ended up being much more practical than forcing every action through one mechanism.

## Architecture

### 1. Mouse layer: socket bridge
- `windows/mouse_bridge.py`
- `wsl/mouse_client.py`
- `wsl/mouse-socket.sh`

Used for:
- mouse move
- mouse click
- cursor position

Why:
- lower overhead than generating a temporary `.ps1` file per action
- better for frequent tiny operations
- easy to call from agents or shell scripts

### 2. Desktop utility layer: PowerShell + Win32
- `windows/input-sim.ps1`
- `windows/app-control.ps1`
- `windows/screen-info.ps1`
- `windows/drag.ps1`

Used for:
- type text
- send shortcuts
- screenshots
- window listing/focus/move/resize
- drag operations
- practical keyboard adaptation for mixed Chinese/English input

## Repository layout

```text
openclaw-gui-desktop-control/
├─ windows/
│  ├─ mouse_bridge.py
│  ├─ run_mouse_bridge.bat
│  ├─ input-sim.ps1
│  ├─ app-control.ps1
│  ├─ screen-info.ps1
│  └─ drag.ps1
├─ wsl/
│  ├─ mouse_client.py
│  ├─ mouse-bridge.sh
│  ├─ mouse-socket.sh
│  ├─ dc-mouse-move.sh
│  ├─ dc-mouse-click.sh
│  ├─ dc-mouse-drag.sh
│  ├─ dc-type-text.sh
│  ├─ dc-type-text-auto-ime.sh
│  ├─ dc-send-keys.sh
│  ├─ dc-list-windows.sh
│  ├─ dc-focus-window.sh
│  └─ dc-screenshot.sh
├─ tests/
│  ├─ test_socket_ping.sh
│  ├─ test_powershell_help.sh
│  └─ test_smoke.sh
├─ docs/
│  ├─ TUTORIAL_zh-CN.md
│  └─ GITHUB_RELEASE_NOTES.md
├─ ROADMAP.md
└─ LICENSE
```

## Quick start

### 1. Put the repo somewhere Windows can access
Recommended setup:
- keep it in any Windows-accessible path, or directly in WSL and convert paths with `wslpath -w`

Examples:
- `C:\Users\<you>\openclaw-gui-desktop-control`
- `\\wsl.localhost\Ubuntu\home\<you>\...\gui-desktop-control`

You can also keep it in WSL and use `wslpath -w` when calling PowerShell scripts.

### 2. Start the Windows mouse bridge
Double-click:
- `windows/run_mouse_bridge.bat`

Or from cmd:
```bat
cd /d <path-to-repo>\windows
py -3 mouse_bridge.py
```

> Important: run it in the **current logged-in desktop session**. Do **not** run it as a service or in Session 0.

### 3. Test connectivity from WSL
```bash
cd gui-desktop-control
./tests/test_socket_ping.sh
```

### 4. Common commands
```bash
./wsl/mouse-socket.sh move 800 500
./wsl/mouse-socket.sh click 800 500
./wsl/dc-type-text.sh "hello world"
./wsl/dc-send-keys.sh "Ctrl+L"
./wsl/dc-list-windows.sh
./wsl/dc-focus-window.sh "Notepad"
./wsl/dc-screenshot.sh
```

## Example workflows

### Click something in a target app
```bash
./wsl/dc-focus-window.sh "Notepad"
./wsl/mouse-socket.sh move 500 300
./wsl/mouse-socket.sh click
```

### Type into the focused window
```bash
./wsl/dc-type-text.sh "hello from WSL"
./wsl/dc-send-keys.sh "Enter"
```

### Save a screenshot
```bash
./wsl/dc-screenshot.sh
./wsl/dc-screenshot.sh "Notepad"
```

## Tests

### PowerShell script load check
```bash
./tests/test_powershell_help.sh
```

### Socket connectivity check
```bash
./tests/test_socket_ping.sh
```

### Smoke test
```bash
./tests/test_smoke.sh
```

## Limitations

- current socket server only implements `ping / move / click`
- keyboard adaptation includes heuristic IME switching for Chinese/English input, which is practical but not universal
- UAC prompts / elevated windows / lock screen are not guaranteed to be controllable
- screenshots and interaction depend on a real active desktop session

## Good fit for

- OpenClaw running inside WSL
- local-first desktop automation
- Windows app control without pulling in a large RPA stack
- a base layer you want to extend later with OCR or UI Automation

## Not trying to be

- a full visual automation suite
- a polished end-user RPA product
- a replacement for Playwright/Selenium/browser tooling

## Docs

- Chinese tutorial: [`docs/TUTORIAL_zh-CN.md`](docs/TUTORIAL_zh-CN.md)
- Release copy / GitHub metadata: [`docs/GITHUB_RELEASE_NOTES.md`](docs/GITHUB_RELEASE_NOTES.md)
- Project roadmap: [`ROADMAP.md`](ROADMAP.md)

## License

MIT
