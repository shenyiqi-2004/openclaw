@echo off
setlocal
title OpenClaw (WSL Interactive)

REM Open an interactive Ubuntu shell and keep it open.
REM Runs OpenClaw once, then drops you into a normal bash prompt (Linux side).
REM D:\openclaw is the canonical external memory home exposed to WSL as /mnt/d/openclaw.
wsl.exe -d Ubuntu -- bash --login -i -c "set -e; export OPENCLAW_EXTERNAL_MEMORY_ROOT=/mnt/d/openclaw; /home/park/.local/bin/openclaw gateway start || true; echo; echo 'OpenClaw: try  openclaw gateway status'; echo 'Dashboard: http://127.0.0.1:18789/'; echo; exec bash --login -i"
