---
name: pattern-extract
description: Extract reusable patterns from reflections and repeated corrections, then record them in PATTERNS.md for future reuse.
---

# Pattern Extract Skill

## Description
从反思历史和行为纠正中提取可复用模式，写入 PATTERNS.md。

## When to trigger
- coding 完成后，reflection skill 发现了新教训
- 用户纠正了某个行为（第 2+ 次出现同一纠正）
- 手动触发："整理 patterns"、"提取模式"

## Protocol

### Step 1: 检查是否已有匹配 pattern
读 PATTERNS.md，搜索是否已有相同或相似模式。

### Step 2: 判断是否值得写入
写入条件（必须满足至少一个）：
- 同一模式被执行 2+ 次
- 同一纠正出现 2+ 次
- 操作复杂度高（3+ 步骤）且可能再次遇到

不写入：
- 一次性任务
- 纯业务逻辑（非工具/环境/流程层面）
- 已有 pattern 完全覆盖

### Step 3: 写入 PATTERNS.md
格式：`[when 场景] → [pattern 模式] → [do 执行]`

分类到对应章节：
- 环境：WSL、浏览器、网络、Ollama
- 飞书：API、多维表格、日历、消息
- OpenClaw：配置、重启、session、extension
- Coding：调试、验证、收束

### Step 4: 来源标注
在 pattern 后面加来源标注（可选）：
- `← feedback 2026-04-04` — 来自行为纠正
- `← reflection 2026-04-04` — 来自反思发现
- `← repeated 3x` — 来自重复执行

## What NOT to do
- 不写太具体的 pattern（"张三的项目用 vitest"→ 太具体）
- 不写太泛的 pattern（"写代码前先想想"→ 废话）
- 不重复已有 pattern
---
name: pattern-extract
description: Extract reusable patterns from reflections and repeated corrections, then record them in PATTERNS.md for future reuse.
---
