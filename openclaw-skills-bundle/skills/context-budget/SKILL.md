---
name: context-budget
description: "Audit context window consumption across skills, agents, MCP servers, and config files. Identify bloat and produce token-savings recommendations. Use when performance degrades or before adding new components."
---

# Context Budget

Analyze token overhead across every loaded component and surface actionable optimizations.

## When to Use

- Session performance feels sluggish or output quality is degrading
- Recently added many skills or tools
- Want to know how much context headroom you have
- Planning to add more components and need room check
- "How much context am I using?"

## How It Works

### Phase 1: Inventory

Scan all component directories and estimate token consumption:

**Skills** (`skills/*/SKILL.md`)
- Count tokens per SKILL.md (words × 1.3)
- Flag: files >400 lines (heavy)
- Count total skills loaded

**Boot Files** (AGENTS.md, SOUL.md, USER.md, TOOLS.md, MEMORY.md, etc.)
- Count tokens per file
- Flag: combined total >500 lines

**Config** (openclaw.json)
- Estimate loaded plugin overhead
- Count configured extensions

**Rules / Conventions**
- Count tokens in PATTERNS.md and other convention files

### Phase 2: Classify

| Bucket | Criteria | Action |
|--------|----------|--------|
| **Always needed** | Boot files, core skills matching current task | Keep |
| **Sometimes needed** | Domain-specific skills, rarely triggered | Consider lazy-load |
| **Rarely needed** | Duplicate content, outdated references | Remove or archive |

### Phase 3: Detect Issues

- **Duplicate skills** — skills with overlapping functionality
- **Heavy skills** — SKILL.md >400 lines (should be split or trimmed)
- **Boot file bloat** — AGENTS.md/MEMORY.md with verbose historical data
- **Orphan references** — paths pointing to deleted directories

### Phase 4: Report

```
Context Budget Report
═══════════════════════════════════════

Total estimated overhead: ~XX,XXX tokens

Component Breakdown:
┌─────────────────┬────────┬───────────┐
│ Component       │ Count  │ Tokens    │
├─────────────────┼────────┼───────────┤
│ Boot files      │ N      │ ~X,XXX    │
│ Skills          │ N      │ ~X,XXX    │
│ Plugins         │ N      │ ~X,XXX    │
│ Memory index    │ 1      │ ~X,XXX    │
└─────────────────┴────────┴───────────┘

Issues Found (N):
[ranked by token savings]

Top 3 Optimizations:
1. [action] → save ~X,XXX tokens
2. [action] → save ~X,XXX tokens
3. [action] → save ~X,XXX tokens
```

## Token Estimation Rules

- Prose: words × 1.3
- Code: chars / 4
- JSON/YAML: chars / 3.5
- Each skill SKILL.md in skill catalog: ~50 tokens (name + description only, not full content)
- Full SKILL.md loaded on demand: actual token count

## Best Practices

- Audit after adding any skill or plugin
- Boot files combined should stay under 2000 tokens
- MEMORY.md should be an index (pointers), not content
- Archive old patterns instead of accumulating in PATTERNS.md

## Token Budget Strategies (from Claude Code compact service)

根据上下文窗口使用率自动选择合适的压缩策略，确保关键信息不丢失。

### 四档策略（使用率阈值）

| 使用率 | 档位 | 策略 | 说明 |
|--------|------|------|------|
| **<25%** | 🟢 正常 | 正常运行，无需干预 | 充裕空间，随便用 |
| **25-50%** | 🟡 关注 | 启用 tool output 裁剪 | 工具输出截断到关键部分 |
| **50-75%** | 🟠 警告 | 启用 LLM 摘要压缩 | 压缩中间轮次，保留 head + tail |
| **>75%** | 🔴 紧急 | 紧急截断 + 强制摘要 | 立即压缩，丢弃非关键信息 |

### Tool Output 裁剪策略（50% 档位）

```
触发条件：token 使用率 >50%

裁剪规则：
- 文件读取：保留前 100 行 + 后 50 行（中间用 <!-- N lines --> 标注）
- 工具错误：只保留错误类型 + 关键参数，删除堆栈中间行
- 列表操作：只保留前 10 条 + 总数，标注 "... and N more"
- 长命令输出：只保留最后 20 行 + exit code
- grep/search 结果：只保留前 20 条匹配，标注行号

禁止裁剪：
- system prompt / AGENTS.md / SOUL.md
- 用户明确要求保留的输出
- 安全相关的错误信息
- 正在进行的 deep execution 状态
```

### LLM 摘要压缩（75% 档位）

```
触发条件：token 使用率 >75%

压缩模板（结构化摘要，替换中间轮次）：

## [Task Name]
- Goal: [原始目标，一句话]
- Progress: [已完成：X 步 / 共 Y 步]
- Decisions: [关键决策点，3 条以内]
- Files: [修改过的文件列表]
- Next: [当前正在做什么]
- Blockers: [如有]

保留策略：
- 保护 head（system prompt + 首轮交互）
- 保护 tail（最近 ~20k token）
- 中间轮次用结构化摘要替代
```

### Prompt Cache Break 检测

修改 system prompt、SKILL.md 或 AGENTS.md 后，必须检查 cache 命中是否被破坏：

```bash
# 检测 prompt cache 状态（OpenClaw internal）
# 查看 session 是否有 cache_hit / cache_miss 标记
# 或观察 token 计数的突变（cache break 后会突然飙升）
```

**Cache Break 典型信号：**
- 修改了 SKILL.md 后，同一 skill 的 tool call 行为异常
- token 计数突然增加 20-50%（原 cache 内容被刷新）
- 某个 skill 的指令突然不生效（被旧 cache 覆盖后又刷新）

**Cache-Friendly 消息排列原则：**
```
✅ Good: 同一 skill 的工具调用尽量连续
   1. Read SKILL.md
   2. Execute skill task (tool calls)
   3. Done → 切换到下一个 skill

❌ Bad: skill 交错导致 cache miss
   1. Skill A step 1
   2. Skill B step 1
   3. Skill A step 2  ← 重新加载 Skill A prompt
   4. Skill B step 2  ← 重新加载 Skill B prompt
```

**Cache 命中率监控指标：**
- 每次 skill 切换后检查 token 计数增量（正常 <500 tokens cache hit）
- 如果 skill 重新加载 >2000 tokens，说明 cache break
- 发现 cache break 后，在该 skill 完成后主动压缩上下文

---
Origin: Adapted from Everything Claude Code (ECC) context-budget skill for OpenClaw environment.

## 新增：Token四档策略

| 档位 | 使用率 | 策略 |
|------|--------|------|
| 25% | <25% | 正常：保护head+tail，压缩中间 |
| 50% | 25-50% | 警戒：head保持，tail压缩50% |
| 75% | 50-75% | 警告：head+tail都压缩，启动micro |
| 100% | >75% | 熔断：立即压缩，block新对话 |

## 新增：压缩触发条件

- 硬性阈值：token使用率>75% → 立即压缩
- 软性阈值：token使用率>50% + idle>60s → 延迟压缩
- 会话结束：自动触发sessionMemoryCompact
- 手动触发：用户指令"压缩上下文"

## 新增：保护区规则

- head保护区：system prompt + 首轮对话 + AGENTS.md/SOUL.md
- tail保护区：最近20k token不压缩
- 压缩禁区：正在执行的coding任务中间状态禁止压缩
