---
name: openclaw-plugin-dev
description: OpenClaw plugin development checklist and workflow. Use when creating, debugging, or deploying OpenClaw plugins/extensions. Covers SDK API verification, minimal spike testing, config deployment (plugins.allow + load.paths + entries), and common pitfalls from real production incidents.
---

# OpenClaw Plugin Development

## Before Writing Any Code

```bash
# 1. Verify SDK API signatures - NEVER rely on memory
grep -A10 "registerTool\|definePluginEntry" \
  ~/.npm-global/lib/node_modules/openclaw/dist/plugin-entry*.js
```

Key signatures (verified 2026-04-04):
- `definePluginEntry({ id, name, description, register(api, config) {...} })` — field is `register`, NOT `activate`
- `api.registerTool({ name, label, description, parameters, execute })` — single object param, NOT 3 params

## Development Workflow

### Phase 1: Minimal Spike (1 tool)

Write the absolute minimum plugin with 1 tool. Verify it loads before adding logic.

```javascript
// ~/.openclaw/extensions/my-plugin/index.js
import { definePluginEntry } from 'openclaw/plugin-entry';

export default definePluginEntry({
  id: 'my-plugin',
  name: 'My Plugin',
  description: 'Does one thing',
  register(api, config) {
    api.registerTool({
      name: 'my_tool',
      label: 'My Tool',
      description: 'Test tool',
      parameters: { type: 'object', properties: {}, required: [] },
      execute: async (params) => ({ result: 'ok' })
    });
  }
});
```

### Phase 2: Deploy Config (ALL THREE at once)

One `config.patch` call, three fields — miss any one and the plugin won't load:

```json
{
  "plugins": {
    "allow": ["...existing...", "my-plugin"],
    "load": {
      "paths": [
        "...existing paths...",
        "/home/park/.openclaw/extensions/my-plugin"
      ]
    },
    "entries": {
      "my-plugin": {
        "enabled": true,
        "config": {}
      }
    }
  }
}
```

⚠️ After config change, do NOT immediately call `gateway restart`. Let Gateway auto-reload. If you must restart, batch all config changes first, then restart once.

### Phase 3: Verify Loading

```bash
# Check gateway logs for plugin registration
grep -i "my-plugin\|registerTool" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -20
```

### Phase 4: Add Full Logic

Only after spike loads successfully, add remaining tools and logic.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `activate` instead of `register` | Plugin loads but no tools appear | Use `register` field |
| 3-param `registerTool(name, desc, fn)` | TypeError at startup | Use single-object param |
| Missing `plugins.allow` | Gateway warn + auto-discovery | Add to allow list |
| Missing `load.paths` | Plugin not found | Add extension path |
| Missing `entries` | Plugin disabled | Add entries with enabled:true |
| Config change + immediate restart | Gateway unstable 5+ min | Let auto-reload handle it, or batch then restart once |

## File Locations

- Custom plugins: `~/.openclaw/extensions/`
- Built-in plugins: `~/.npm-global/lib/node_modules/openclaw/dist/extensions/`
- Config: `~/.openclaw/openclaw.json`
- Logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
