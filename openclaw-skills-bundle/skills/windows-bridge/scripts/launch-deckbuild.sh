#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$HOME/.openclaw/workspace/skills/windows-bridge/scripts"
if "$BASE_DIR/wincheck.sh" GuiAppStarter | grep -qi GuiAppStarter; then
  echo "DeckBuild launcher already running"
  exit 0
fi
"$BASE_DIR/winlaunch.sh" "D:\TCAD\etc\GuiAppStarter.exe" "-lib-dir-name deckbuild" "-exe-name deckbuild"
echo "DeckBuild launch sent"
