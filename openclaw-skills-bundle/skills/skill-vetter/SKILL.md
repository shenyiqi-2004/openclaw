---
name: skill-vetter
version: 1.0.0
description: Security-first skill vetting for AI agents. Use before installing any skill from GitHub, ClawdHub, or other third-party sources to check for red flags, excessive permissions, and suspicious behavior.
---

# Skill Vetter

Use this skill before installing or trusting any external skill.

## Vetting checklist

### 1. Source

Check:
- repository owner
- stars or adoption signal
- last update time
- stated purpose

### 2. Code review

Reject immediately if you see:
- credential harvesting
- unexplained network calls
- shell download-and-execute patterns
- access to sensitive user files without clear reason
- obfuscated or encoded payloads
- privilege escalation requests

### 3. Permission scope

Confirm:
- what files it reads
- what files it writes
- what commands it runs
- whether network access is required
- whether the scope matches the claimed purpose

### 4. Risk judgment

- Low: notes, formatting, simple local workflows
- Medium: file edits, browser control, API integrations
- High: credentials, system configuration, trading, security controls
- Extreme: root access or hidden exfiltration

## Output format

Produce:
- source
- reviewed files
- red flags
- required permissions
- risk level
- final verdict

## Rule

When in doubt, do not install.
