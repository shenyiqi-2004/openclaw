---
name: wsl-network-doctor
description: WSL2 network connectivity diagnostics and repair. Use when encountering connection failures to Edge CDP (port 9222), Ollama (port 11434), or any WSL2↔Windows portproxy issue. Covers portproxy verification, rebuild, and service connectivity checks.
---

# WSL2 Network Doctor

## Quick Diagnosis (run in order)

### Step 1: Check portproxy alive

```bash
curl -s --connect-timeout 3 http://172.18.160.1:9222/json/version
```

- **Success**: JSON with Chrome version → portproxy OK, skip to Step 3
- **Fail**: Connection refused → Step 2

### Step 2: Rebuild portproxy

Run on **Windows side** (elevated PowerShell):

```powershell
netsh interface portproxy add v4tov4 listenport=9222 listenaddress=172.18.160.1 connectport=9222 connectaddress=127.0.0.1
```

Or trigger the scheduled task if configured:

```bash
# From WSL
schtasks.exe /run /tn EdgePortProxy
sleep 3
# Re-verify
curl -s --connect-timeout 3 http://172.18.160.1:9222/json/version
```

### Step 3: Service connectivity matrix

| Service | Address | Test Command |
|---------|---------|-------------|
| Edge CDP | 172.18.160.1:9222 | `curl -s http://172.18.160.1:9222/json/version` |
| Ollama | 172.18.160.1:11434 | `curl -s http://172.18.160.1:11434/api/tags` |
| Gateway | 0.0.0.0:18789 | `curl -s http://127.0.0.1:18789/health` |

### Step 4: Common post-reboot fixes

WSL2 reboot loses all portproxy rules. After Windows restart:

1. Verify WSL IP hasn't changed: `ip addr show eth0 | grep inet`
2. Re-run portproxy setup for all needed ports
3. Restart Edge with `--remote-debugging-port=9222` if CDP needed

## Environment Reference

- WSL2 gateway IP: `172.18.160.1`
- NAT mode: default (not mirrored)
- Edge CDP: requires `--remote-debugging-port=9222` launch flag
- Ollama: Windows-side service, accessed via gateway IP

## ⚠️ Red Lines

- **Never** modify Windows network topology (routing tables, firewall rules beyond portproxy)
- **Never** run `taskkill /f /im msedge.exe` — kills all Edge tabs
- portproxy is the **only** safe network modification
