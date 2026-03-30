---
name: openclaw-ops-runbook
description: Use when working on the local OpenClaw runtime, path handling, startup behavior, Windows bridge control, or Xiaohongshu MCP troubleshooting. Covers the canonical OpenClaw home, WSL path mapping, startup boundaries, and fixed recovery order for common local operations.
---

# OpenClaw Ops Runbook

Use this skill when the task touches the local OpenClaw install, its home path, startup behavior, Windows bridge behavior, or the Xiaohongshu MCP path.

## Canonical home

- Treat `/home/park/openclaw` as the canonical OpenClaw home.
- Treat `/home/park/openclaw/.openclaw` as the active runtime state root.
- Treat `/home/park/openclaw/memory-sidecar` as the active markdown sidecar root.

## Active memory architecture

- Treat the markdown sidecar as the control plane:
  - working memory
  - summary
  - strategy
  - reflection
  - selfcheck
- Treat `memory-lancedb-pro` as the only active long-term memory backend.
- Do not re-enable legacy `memory-lancedb` unless there is an explicit migration or rollback reason.
- Keep long-term recall compact and filtered; do not dump raw memory into prompts.

## Trigger model

- Sidecar work is triggered by real OpenClaw runtime cycles, not by idle background behavior.
- Treat `chat`, `agent`, and `reply-agent` completions as the normal sidecar trigger path.
- Treat `before_prompt_build` as the long-term recall hook.
- Treat `agent_end` as the long-term persistence hook.

## Path handling

### Windows and WSL path mapping

- When a Windows path must be accessed from OpenClaw, map it through the WSL path form first.
- Do not treat Windows paths as inaccessible by default if a stable WSL mapping exists.

## Startup boundary

- `selfstart` is manual-start only.
- Do not configure tray, mouse bridge, or helper scripts as Windows auto-start without explicit user approval.
- When startup behavior looks wrong, inspect startup sources first:
  - Startup folder
  - Run keys
  - Scheduled tasks

## Runtime checks

### Service health

- When verifying OpenClaw health, check `openclaw status` or `gateway status` first.
- Treat `RPC probe: ok` as the quick confirmation that the gateway is alive.

### Runtime config and restart rule

- Treat `/home/park/openclaw/.openclaw/openclaw.json` as the runtime config source of truth.
- After changing model, plugin, exec, or gateway-related config, restart the gateway before trusting the new state.
- After upgrading or cutting over to a new OpenClaw build, confirm the gateway service points at the current entrypoint under `/home/park/openclaw/dist/entry.js`, not an older hashed build artifact.

### Memory backend checks

- If sidecar behavior is in question, check:
  - `memory-sidecar/memory/working.json`
  - `memory-sidecar/memory/runtime.json`
- If long-term memory behavior is in question, check:
  - `/home/park/.openclaw/memory/lancedb-pro`
  - recent gateway logs for `memory-lancedb-pro`

### Control UI checks

- If the dashboard or WebChat says Control UI assets are missing, rebuild them with `pnpm ui:build`.
- If Control UI loads but the login screen says `origin not allowed`, fix `gateway.controlUi.allowedOrigins`, then restart the gateway.
- If the Control UI repeatedly reopens the wrong chat, clear or override the session restore logic instead of assuming the agent routing is broken.

### Session and channel display checks

- Treat `agent:main:main` as the canonical direct main session.
- Do not expose internal labels such as `heartbeat`, raw WhatsApp phone numbers, `ou_/oc_` Feishu ids, or raw WeChat ids as primary UI titles.
- When the session picker is noisy, distinguish real chats from cron/internal sessions before debugging channel routing.

### Cron and daily briefing checks

- For exact daily delivery, prefer a deterministic script over a free-form agent prompt when the job must always produce the same structure.
- If an OpenClaw cron job keeps drifting in `isolated` mode, move the critical path into a script and let the scheduler only trigger that script.
- For the daily WeChat briefing on this machine, the stable path is:
  - system cron
  - `/home/park/.openclaw/workspace/scripts/daily_briefing_runner.py`
  - `openclaw message send --channel openclaw-weixin ...`
- Do not route the daily briefing through `webchat` delivery.
- Keep the old broken OpenClaw daily briefing job disabled to avoid duplicate sends.

### WeChat delivery checks

- If `openclaw-weixin` outbound fails with `AbortError` or `fetch failed`, verify the plugin API retry path before touching higher-level channel logic.
- Validate WeChat outbound with a direct probe first:
  - `openclaw message send --channel openclaw-weixin --target <wechat-id> --message <text> --json`
- If direct send works but cron announce fails, the problem is the cron delivery path, not the base channel wiring.

### Model and config hygiene

- Keep `openai-codex/gpt-5.4` as the primary default unless there is an explicit local-first override decision.
- Keep local Ollama models role-separated:
  - text fallback for text
  - vision model for vision
  - embedding model for embeddings
- After pruning local models, remove stale config references immediately or subagents will keep pointing at deleted models.

## Mouse bridge rule

- The socket mouse bridge host is `172.18.160.1`.
- The bridge must run in the user desktop session, not Session 0.

## Xiaohongshu MCP runbook

Follow this order before branching out:

1. Check mcporter status.
2. Ensure Docker Desktop is running.
3. Start the container.
4. Verify MCP registration.
5. Only then do deeper debugging.

## Tooling policy

- Prefer dedicated tools and built-in file operations before using `exec`.
- Treat `exec` as the last-resort path, even though it is auto-approved.
- When a task can be solved by read/write/edit/apply_patch, use those first.

## Memory discipline

- Keep long-term memory small.
- Store only reusable operational knowledge.
- Prefer concise conclusions over raw logs or long transcripts.

## Recovery order

Follow this order before deeper debugging:

1. Confirm gateway health.
2. Confirm runtime config source of truth.
3. Confirm sidecar files are still updating.
4. Confirm long-term memory backend is active and writable.
5. Only then inspect agent-specific or tool-specific behavior.

## Boundaries with other skills

- Do not duplicate generic WAL, heartbeat, self-improvement, or broad memory-growth protocols here.
- Leave generic correction logging, learning loops, and proactive memory architectures to `proactive-agent`, `self-improving`, or `self-improving-agent`.
- Use this skill only for OpenClaw-local runtime facts, pathing, startup boundaries, memory backend checks, and fixed operational runbooks.
