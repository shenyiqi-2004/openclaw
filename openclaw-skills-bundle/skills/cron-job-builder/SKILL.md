---
name: cron-job-builder
description: OpenClaw cron job creation best practices. Use when creating, debugging, or modifying cron jobs (scheduled tasks). Covers timeout configuration, lightContext optimization, session bootstrap overhead, and common timeout/failure patterns.
---

# OpenClaw Cron Job Builder

## Job Type Decision Tree

| Task Type | sessionTarget | payload.kind | lightContext | timeoutSeconds |
|-----------|--------------|-------------|-------------|----------------|
| Quick reminder/alert | main | systemEvent | N/A | N/A |
| Script execution (exec commands) | isolated | agentTurn | **true** | 300 |
| Research/analysis (web search, reading) | isolated | agentTurn | false | 300 |
| Report generation (needs workspace context) | isolated | agentTurn | false | 600 |
| Current-session follow-up | current | agentTurn | false | 120 |

## Key Rules

### 1. Always set lightContext for script-only jobs

Isolated sessions load AGENTS.md, SOUL.md, USER.md, MEMORY.md on bootstrap — takes 60-90s. If the job just runs shell commands, this context is wasted time.

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run: ls /tmp && echo done",
    "lightContext": true,
    "timeoutSeconds": 300
  }
}
```

### 2. Timeout = bootstrap + execution + buffer

| Component | Typical Duration |
|-----------|-----------------|
| Session bootstrap (full context) | 60-90s |
| Session bootstrap (lightContext) | 5-15s |
| Model inference | 10-60s |
| Shell command execution | 1-30s |

**Formula**: `timeoutSeconds = bootstrap + inference + execution + 30s buffer`

- Full context job: minimum **180s**
- Light context job: minimum **120s** (but 300s recommended)
- Never use 60s or 120s for full-context isolated jobs

### 3. Delivery configuration

```json
{
  "delivery": {
    "mode": "announce",     // Send result to chat
    "channel": "feishu",    // Optional: specific channel
    "bestEffort": true      // Don't fail if delivery fails
  }
}
```

For silent background jobs:
```json
{
  "delivery": { "mode": "none" }
}
```

## Template: Daily Cron Job

```json
{
  "name": "daily-task",
  "schedule": {
    "kind": "cron",
    "expr": "30 5 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Task description here",
    "lightContext": true,
    "timeoutSeconds": 300
  },
  "delivery": { "mode": "announce" }
}
```

## Template: One-shot Reminder

```json
{
  "name": "reminder",
  "schedule": {
    "kind": "at",
    "at": "2026-04-11T15:00:00+08:00"
  },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder: meeting in 10 minutes"
  },
  "deleteAfterRun": true
}
```

## Debugging Cron Failures

```bash
# Check job status
cron list

# Check run history
cron runs jobId="<job-id>"

# Common failure patterns:
# - consecutiveErrors > 0 → check timeout
# - status "timeout" → increase timeoutSeconds
# - status "error" → check message/model availability
```

## ⚠️ Pitfalls

| Pitfall | Fix |
|---------|-----|
| 120s timeout for full-context job | Use 300s minimum |
| systemEvent on isolated session | systemEvent requires sessionTarget=main |
| agentTurn on main session | agentTurn requires isolated/current/session:xxx |
| Forgot lightContext for script jobs | Add `lightContext: true` |
| Cron timeout ≠ model timeout | Check both — model 408 can stall the entire job |
