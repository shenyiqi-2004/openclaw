# 反思协议详解

## 核心思想

Claude Code 和 Hermes 都在**上下文压缩时**才提取记忆（被动）。

Evolution Protocol 要求在**每轮 coding 结束后**主动反思（主动）。

## 三层反思机制

### 1. 每轮反思（强制检查点）

每轮 coding 任务结束时，必须调用 `evolution_reflect` tool：

```
Outcome: pass | fail | blocked
Lesson: [新教训，一句话。没有写"无"]
Next: [下一步 | 任务完成 | 需要收束]
```

**触发条件**：修改代码、调试失败、补测试、重构、实施功能。

**不触发**：纯解释、方案讨论、日志解读、架构评审、文档整理、翻译注释。

### 2. 收束规则（熔断）

连续 2 轮 `outcome=fail` 且无新信号 → 强制收束：

```
现状 → 阻塞点 → 建议下一步
```

"无新信号"定义：
- 没有缩小范围
- 没有新可执行计划
- 没有新代码改动
- 验证无新信息
- 缺上下文却在猜

**收束后**：不继续扩散问题，不蛮干。

### 3. 实时反思（Mid-task Check）

执行到第 3 步时暂停检查：
- 当前方向是否还指向目标？
- 有没有跳过更简单的方案？
- 已做的步骤有没有引入新问题？

## 记忆归档流

```
coding 结束
    ↓
evolution_reflect tool
    ↓
Lesson ≠ "无" ?
    ├─ yes → 判断类型 → 写入 memory/[type]/
    │         ├─ 可复用模式 → 追加 PATTERNS.md
    │         └─ LanceDB 写入（可选）
    └─ no → 无归档动作
    ↓
Outcome = fail × 2 → 收束
```

## 为什么比两者都强

| | Claude Code | Hermes | Evolution Protocol |
|---|---|---|---|
| 反思时机 | 压缩时（被动） | 压缩时（被动） | **每轮 coding 后（主动）** |
| 归档分类 | 4 类目录 | 2 文件 | **4 类目录 + LanceDB** |
| 熔断机制 | 无 | 无 | **2 轮 fail → 强制收束** |
| 模式积累 | 无 | 无 | **PATTERNS.md 持续积累** |

## 从哪里提取教训

1. **用户直接纠正**：用户说"别这样" → feedback
2. **任务完成回顾**：pass 时有没有可以更好的地方 → feedback/project
3. **环境问题**：路径/Bug/工具问题 → reference
4. **项目状态**：决策/截止/范围变化 → project
