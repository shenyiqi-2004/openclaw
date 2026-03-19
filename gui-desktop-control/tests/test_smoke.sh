#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
echo '[1/2] PowerShell scripts help'
"$SCRIPT_DIR/test_powershell_help.sh" >/dev/null
echo '[2/2] Socket ping (requires Windows server running)'
"$SCRIPT_DIR/test_socket_ping.sh"
echo 'smoke test passed'
