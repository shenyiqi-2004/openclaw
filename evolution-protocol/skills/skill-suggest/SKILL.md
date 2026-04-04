# Skill Suggest Skill

## Description
分析任务历史，建议将高频操作流程固化为新 skill。

## When to trigger
- 反思时发现某个多步骤流程被执行 3+ 次
- 用户问"有没有更快的方式"
- 手动触发："建议 skill"、"有什么可以自动化"

## Protocol

### Step 1: 识别候选流程
从以下来源寻找高频多步骤操作：
1. `memory/feedback/` — 反复出现的纠正说明该流程容易出错
2. `PATTERNS.md` — 已有 pattern 如果步骤 ≥3 且频率高，可以升级为 skill
3. LCM 历史 — 用 lcm_grep 搜索重复出现的工具调用序列
4. 当前任务 — 如果当前任务的流程复杂且通用

### Step 2: 评估是否值得成为 skill
必须同时满足：
- 流程 ≥3 步
- 预期未来还会用 ≥3 次
- 不是纯一次性业务逻辑
- 现有 skills/ 目录没有覆盖

### Step 3: 生成 SKILL.md 模板
```markdown
# [Skill Name]

## Description
[一句话描述]

## When to trigger
[触发条件]

## Protocol
### Step 1: [步骤名]
[具体操作]
...

## What NOT to do
[边界]
```

### Step 4: 询问用户
输出建议：
```
建议新 skill: [名称]
原因: [为什么值得固化]
预计覆盖场景: [哪些任务会用到]
要创建吗？
```

等用户确认后：
1. 写入 `skills/[name]/SKILL.md`
2. OpenClaw 自动发现，无需额外配置

## What NOT to do
- 不自动创建 skill（必须用户确认）
- 不建议过于细分的 skill（一个 skill 只做一件事 → 太碎）
- 不建议已有 skill 覆盖的流程
- 不把 skill 当成 alias（"npm test 的 skill"→ 不值得）
