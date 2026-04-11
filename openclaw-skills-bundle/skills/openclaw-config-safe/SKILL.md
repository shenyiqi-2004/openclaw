---
name: openclaw-config-safe
description: Safe OpenClaw configuration modification workflow. Use when changing openclaw.json, adding plugins, modifying providers, or any Gateway config update. Prevents common mistakes like partial config writes, premature restarts, and orphan session cleanup failures.
---

# OpenClaw Config Safe Modification

## Pre-flight Checklist

Before any config change:

1. **Identify scope**: Which config section? (plugins / providers / acp / channels / agents)
2. **Use `config.patch`** — never `config.apply` unless replacing entire config
3. **Batch changes** — collect all changes, apply once, restart once (if needed)

## Config Change Workflow

### Step 1: Read current state

```
gateway config.get path="plugins"
```

Or for specific subsection:

```
gateway config.schema.lookup path="plugins.entries"
```

### Step 2: Apply with config.patch

```
gateway config.patch path="plugins.entries.my-plugin" raw='{"enabled":true,"config":{}}'
```

For plugin deployment, **all three fields in one patch**:

```json
{
  "plugins.allow": ["...existing...", "new-plugin"],
  "plugins.load.paths": ["...existing...", "/path/to/new-plugin"],
  "plugins.entries.new-plugin": { "enabled": true, "config": {} }
}
```

### Step 3: Post-change behavior

| Change Type | Gateway Behavior | Action Needed |
|-------------|-----------------|---------------|
| Plugin config | Hot-reload | None — wait 5s |
| Provider/model | Hot-reload | None — wait 5s |
| Channel config | Requires restart | Gateway will auto-restart |
| ACP config | Requires restart | Gateway will auto-restart |

⚠️ **Do NOT call `gateway restart` immediately after config.patch.** Gateway handles reload/restart timing internally. Manual restart while tasks are running causes 5+ minute instability.

### Step 4: Verify

```bash
# Check logs for config reload
tail -20 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "config\|reload\|restart"
```

## Session Cleanup (when removing plugins/sessions)

Three things must be cleaned together:

1. `sessions.json` — remove the session key entry
2. `.jsonl` transcript — delete the session transcript file
3. Related cron jobs — check and remove any associated cron

```bash
# Find session files
ls ~/.openclaw/agents/main/sessions/*.jsonl

# Check cron for related jobs
cron list
```

⚠️ If you only clean `sessions.json` but leave `.jsonl`, Gateway will reconstruct orphan runs from transcripts on next startup → slow boot.

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|------------|------------|
| config.apply instead of config.patch | Overwrites entire config | Always use config.patch |
| Restart right after config change | 5+ min instability if tasks running | Let auto-reload handle it |
| Partial plugin config (missing allow/paths/entries) | Plugin silently fails to load | Deploy all 3 fields together |
| Clean sessions.json but not .jsonl | Slow gateway startup | Clean both + check cron |
| Change provider without checking model name | HTTP 400 Unknown Model | Verify model name in provider docs first |
