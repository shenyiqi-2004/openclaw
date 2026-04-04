# 记忆系统设计

## 4 类记忆分类

| 类型 | 目录 | 写入条件 | 格式 | LanceDB category |
|------|------|---------|------|-----------------|
| 用户画像 | `memory/user/` | 发现用户偏好、角色、知识水平 | 事实 | `preference` |
| 行为纠正 | `memory/feedback/` | 被用户纠正、或反思发现教训 | 规则 → Why → How | `decision` |
| 项目状态 | `memory/project/` | 项目状态变化、决策、截止时间 | 事实 → Why → How | `entity` |
| 外部指针 | `memory/reference/` | 发现有用的外部资源位置 | 路径/URL → 用途 | `fact` |

## 为什么比 Claude Code 的 memdir 更好

Claude Code 用 Sonnet 做语义选择（每次花 API 钱，延迟 1-3 秒）。

OpenClaw 用 LanceDB hybrid retrieval（本地、免费、<100ms）。

架构对比：

```
Claude Code:
  user message → Sonnet ($$) → semantic select → memdir/ category

OpenClaw:
  user message → LanceDB hybrid (qwen3-embedding, 本地) → category + text match
```

## 目录结构

```
~/.openclaw/workspace/memory/
├── user/               ← 用户画像（技术水平、偏好、雷区）
├── feedback/           ← 行为纠正（规则+来源+如何应用）
├── project/            ← 项目状态（事实+来源+如何应用）
├── reference/          ← 外部指针（路径+用途）
└── YYYY-MM-DD.md      ← 每日日志（按日期）
```

## MEMORY.md 索引设计

MEMORY.md 本身只是索引，不存内容。好处：
- 内容在子目录，可以独立更新
- 索引始终保持简洁，加载快
- 每次 boot-md 只加载索引，具体记忆按需从子目录读取

## 写入规则

1. **文件 > 脑记**：要记住的事写文件，不做 mental note
2. **先分类再写**：判断类型 → 写入对应目录 → 更新索引
3. **格式固定**：`事实/规则 → Why → How to apply`
4. **蒸馏后写入**：不存原始对话，只存提炼结论（≤200 字）
5. **LanceDB 对齐**：category 字段必须和 4 种类型对齐

## LanceDB 写入规范（补充 AGENTS.md）

- **允许写入**：用户偏好、环境事实、稳定结论、操作流程
- **禁止写入**：原始聊天消息、heartbeat 轮询、临时排障记录、一次性指令
- scope: `agent:main`
- 每条 ≤200 字
