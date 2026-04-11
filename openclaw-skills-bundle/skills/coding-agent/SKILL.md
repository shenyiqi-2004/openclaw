---
name: coding-agent
description: Delegate complex coding tasks to Claude Code via ACP protocol for multi-file changes, git workflows, project-wide analysis, and full-context debugging.
---

# Coding Agent — Claude Code via ACP

## When to Use
- Complex multi-file coding tasks (refactor, new feature across multiple files)
- Git workflow automation (commit, diff review, branch management)
- Project-wide search and understanding
- Debugging with full project context
- 生成完整应用/游戏/工具

## How to Invoke

### ACP 模式（默认，推荐）
```
sessions_spawn(
  runtime="acp",
  task="任务描述，包含具体需求和输出路径",
  label="任务简称",
  mode="run",
  runTimeoutSeconds=180
)
→ sessions_yield() 等完成事件
```

**要点：**
- `runtime="acp"` 会自动走 ACPX → claude-agent-acp adapter → Claude Code
- 文件输出默认指定到 `/mnt/c/Users/w/Desktop/wsl共享/` 或项目目录
- task 描述要具体：包含文件名、路径、功能需求、技术约束
- 完成事件通过 sessions_yield 自动回调

### 无头模式（降级，ACP 不可用时）
```bash
claude -p "<TASK>" --output-format json
```

## Configuration

### ACP 配置（openclaw.json）
```json
{
  "acp": {
    "enabled": true,
    "backend": "acpx",
    "defaultAgent": "claude",
    "dispatch": { "enabled": true },
    "maxConcurrentSessions": 3
  }
}
```

**⚠️ 关键：**
- `defaultAgent` 必须是 `"claude"`（内置注册名），不是 `"claude-code"`
- 不要在 `acpx.config` 里自定义 `agents` 对象，让内置 AGENT_REGISTRY 工作
- acpx 必须在 `plugins.allow` + `load.paths` + `entries` 三处都配置

### 前置依赖
- `npm install -g @agentclientprotocol/claude-agent-acp@latest`（预装 adapter）
- `~/.claude/settings.json` 配有第三方 API（ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN）

### 详细配置文档
→ `memory/reference/acp-claude-code-setup.md`

## Usage Rules
1. **Use for complex coding only** — simple edits use OpenClaw's native edit/write tools
2. **task 描述要具体** — 包含输出路径、文件名、功能要求、技术栈
3. **One task per spawn** — ACP session 是隔离的，不共享状态
4. **yield 等结果** — spawn 后 sessions_yield()，完成事件自动回调
5. **Review before delivering** — 验证输出文件存在且内容正确

##踩坑记录
| 坑 | 现象 | 解法 |
|----|------|------|
| 自定义 agents.command | exit=143, trust prompt 阻塞 | 删掉 agents 配置，用内置注册表 |
| defaultAgent="claude-code" | agent not found | 用 "claude"（内置名） |
| acpx 只加 allow | 插件不加载 | allow + load.paths + entries 三处齐 |
| 未预装 adapter | 首次 npx 下载慢 | `npm i -g @agentclientprotocol/claude-agent-acp` |

## Fallback Chain
1. ACP spawn → 首选
2. `claude -p "task"` → ACP 不可用时降级
3. `free-code/cli -p "task"` → 官方 CLI 也挂时

## Architecture
```
OpenClaw (orchestrator)
  └─ sessions_spawn(runtime="acp")
       └─ ACPX plugin
            └─ claude-agent-acp adapter
                 └─ Claude Code (Sonnet 4.6, third-party API)
                      └─ 输出文件到指定路径
```

OpenClaw = 编排 + 记忆 + 投递
Claude Code = 编码执行器（via ACP protocol）
