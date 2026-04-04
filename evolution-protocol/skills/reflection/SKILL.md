# Reflection Skill

## Description
Coding 任务完成后的结构化反思协议。自动评估结果、提取教训、归档记忆。

## When to trigger
- 每轮 coding 任务结束时（修改代码、调试、重构、补测试、实施功能）
- 不触发：纯解释、方案讨论、日志解读、文档整理

## Protocol

### Step 1: 结构化评估
输出：
```
Outcome: pass | fail | blocked
Lesson: [新教训一句话，没有写"无"]
Next: [下一步 | 任务完成 | 需要收束]
```

### Step 2: 收束判断
- 连续 2 轮 outcome=fail 且无新信号 → 强制收束
- 收束格式：`现状 → 阻塞点 → 建议下一步`
- 缺环境/权限/依赖/仓库上下文 → 直接收束，不猜
- "无新信号"定义：没有缩小范围、没有新可执行计划、没有新代码改动、验证无新信息、缺上下文却在猜

### Step 3: 记忆归档
如果 Lesson ≠ "无"：
1. 判断类型：
   - 被用户纠正 / 操作教训 → `memory/feedback/`
   - 项目状态变化 → `memory/project/`
   - 发现外部资源位置 → `memory/reference/`
   - 用户偏好 → `memory/user/`
2. 写入对应文件（追加，格式：`规则 → Why → How to apply`）
3. 更新 MEMORY.md 索引（如果是新文件）
4. 如果是可复用模式（同一 pattern 出现 2+ 次）→ 追加到 PATTERNS.md

### Step 4: LanceDB 写入（可选）
- 只在教训足够重要且长期有效时写入
- category 对齐：preference→user, fact→feedback/reference, entity→project, decision→feedback
- scope: `agent:main`
- ≤200 字蒸馏结论

## What NOT to do
- 不把反思本身当成回复给用户（反思是内部协议，用户看到的是结果）
- 不往 LanceDB 塞原始反思过程
- 不在没有新发现时强行写记忆
- outcome=pass 且 lesson=无 时，不做任何归档动作
