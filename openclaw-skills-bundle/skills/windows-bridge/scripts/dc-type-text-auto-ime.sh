#!/usr/bin/env bash
# Auto-detect language and switch IME before typing text
# Usage: dc-type-text-auto-ime.sh <text>
# If text contains Chinese → switch to Chinese IME first
# Otherwise → switch to English IME first

set -euo pipefail

if [ $# -lt 1 ]; then
    echo 'usage: dc-type-text-auto-ime.sh <text>' >&2
    exit 1
fi

TEXT="$1"

# Detect if text contains Chinese characters
contains_chinese() {
    local text="$1"
    # Check if text contains CJK characters (Chinese, Japanese, Korean)
    if echo "$text" | grep -qP '[\x{4E00}-\x{9FFF}\x{3400}-\x{4DBF}]'; then
        return 0  # contains Chinese
    else
        return 1  # no Chinese
    fi
}

PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
BASE="$HOME/.openclaw/workspace/skills/windows-bridge/scripts/desktop-control"

# Function to switch IME by sending Ctrl+Shift
switch_ime() {
    local target="$1"  # "chinese" or "english"
    # Send Ctrl+Shift to toggle IME
    "$PS" -ExecutionPolicy Bypass -Command "
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait('+^{SHIFT}')
        Start-Sleep -Milliseconds 100
    "
    echo "Switched IME to: $target"
}

# Detect and switch
if contains_chinese "$TEXT"; then
    echo "Detected Chinese text, switching to Chinese IME..."
    switch_ime "chinese"
else
    echo "Detected English text, switching to English IME..."
    switch_ime "english"
fi

# Type the text
"$PS" -ExecutionPolicy Bypass -File "$BASE/input-sim.ps1" -Action type-text -Text "$TEXT"
echo "Typed: \"$TEXT\""
