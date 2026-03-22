# memory-lancedb-pro

`memory-lancedb-pro` is the sole long-term memory plugin for this OpenClaw install.

## Architecture

- Markdown memory remains the cognitive control plane:
  - strategy
  - reflection
  - summary
  - memory policy
- `memory-lancedb-pro` is only for compact long-term retrieval and durable persistence.
- Recall is limited, deduplicated, filtered by score, and injected as a small context block.
- Persistence is gated to durable values only:
  - user preferences
  - reusable workflows
  - verified project facts
  - important failures and fixes
  - stable constraints

## Guardrails

- no graph memory
- no second long-term memory plugin
- no broad raw recall injection
- no persistence of temporary chatter or transient state

## Local Ollama setup

This install is configured to use local Ollama only for embeddings.

Configured embedding backend:

- base URL: `http://172.18.160.1:11434/v1`
- api key: `ollama-local`
- model: `qwen3-embedding:4b`
- dimensions: `2560`

Required local model pull:

```bash
ollama pull qwen3-embedding:4b
```

Optional reranker model:

```bash
ollama pull dengcao/Qwen3-Reranker-0.6B:Q8_0
```

Reranker status:

- not enabled
- not wired into `memory-lancedb-pro`
- left disabled intentionally because the current minimal plugin has no clean rerank hook
- installed locally under the Ollama tag `dengcao/Qwen3-Reranker-0.6B:Q8_0`

## Config fields changed

In `~/.openclaw/openclaw.json`:

- `plugins.slots.memory = "memory-lancedb-pro"`
- `plugins.entries["memory-lancedb-pro"].enabled = true`
- `plugins.entries["memory-lancedb-pro"].hooks.allowPromptInjection = true`
- `plugins.entries["memory-lancedb-pro"].config.embedding.apiKey = "ollama-local"`
- `plugins.entries["memory-lancedb-pro"].config.embedding.baseUrl = "http://172.18.160.1:11434/v1"`
- `plugins.entries["memory-lancedb-pro"].config.embedding.model = "qwen3-embedding:4b"`
- `plugins.entries["memory-lancedb-pro"].config.embedding.dimensions = 2560`
- `plugins.entries["memory-lancedb-pro"].config.recallMinScore = 0.62`
- `plugins.entries["memory-lancedb"].enabled = false`

## How to verify

1. Confirm the slot:

```bash
python3 - <<'PY'
import json
cfg=json.load(open('/home/park/openclaw/.openclaw/openclaw.json', encoding='utf-8'))
print(cfg['plugins']['slots']['memory'])
print(cfg['plugins']['entries']['memory-lancedb-pro']['config']['embedding'])
print(cfg['plugins']['entries']['memory-lancedb']['enabled'])
PY
```

Expected:

- slot is `memory-lancedb-pro`
- embedding model is `qwen3-embedding:4b`
- old `memory-lancedb` is `false`

2. Confirm the model exists locally:

```bash
ollama list | grep qwen3-embedding:4b
```

3. Restart gateway:

```bash
cd /home/park/openclaw
node dist/index.js gateway restart
node dist/index.js gateway status
```

4. Verify it is no longer safe-disabled:

```bash
grep -n "safe-disabled" /tmp/openclaw/openclaw-$(date +%F).log | tail
```

After the Ollama config change and restart, you should not see new `safe-disabled` entries.

## No paid key required

This setup does not require any paid cloud embedding provider.

- the plugin uses the local Ollama OpenAI-compatible endpoint
- the `apiKey` field is just a local dummy token for that endpoint
- markdown memory remains authoritative even if the local embedding model is missing or temporarily unavailable
