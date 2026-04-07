# Context Compact Strategies

四种上下文压缩策略的触发条件与适用场景。

---

## 保护区（禁止压缩）

| 区域 | 内容 | 说明 |
|------|------|------|
| **head** | system prompt + 首轮交互 | 始终保留 |
| **tail** | 最近 ~20k token | 始终保留 |

压缩只作用于 head 和 tail 之间的中间轮次。

---

## 四种策略

### 1. summarizer
完整摘要策略。

- **触发条件**: 手动调用 / 探索→执行转换 / 调试完成后 / 死路放弃后
- **压缩效果**: head 保留，tail 保留，中间生成结构化摘要（Goal / Progress / Decisions / Files / Next Steps）
- **性能开销**: 高（LLM 调用）
- **适用场景**: 长程任务收尾、死路放弃后清场、上下文即将耗尽前主动压缩

### 2. micro
轻量裁剪策略。

- **触发条件**: idle > 30s 或 cache_edits 信号触发
- **压缩效果**: 裁剪 tool output，不生成完整摘要，保留原始 message 结构
- **性能开销**: 低（纯裁剪）
- **适用场景**: 短暂 idle 后的状态保存、不影响后续可用性的中间产物丢弃

### 3. auto
自动判断策略（circuit breaker）。

- **触发条件**: Token 使用率达到阈值（由系统配置）
- **压缩效果**: 根据上下文状态自动选择 summarizer 或 micro
- **性能开销**: 中（需判断 + 可选 LLM）
- **适用场景**: 被动触发，防止上下文溢出，production 环境

### 4. sessionMemory
会话结束策略。

- **触发条件**: 会话关闭时
- **压缩效果**: 复用 SessionMemory 文件内容，蒸馏为长期记忆
- **性能开销**: 中（涉及记忆写入）
- **适用场景**: 会话结束时提取关键结论、教训、待办到外部记忆系统

---

## 策略选择决策树

```
Token使用率 < 60% 且 会话时长 < 30min?
├── YES → 不压缩
└── NO
    ├── idle > 30s 或 cache_edits?
    │   ├── YES → micro（轻量裁剪）
    │   └── NO
    │       ├── 会话即将结束?
    │       │   ├── YES → sessionMemory（蒸馏记忆）
    │       │   └── NO
    │       │       ├── 探索→执行 / 调试完成 / 死路放弃?
    │       │       │   ├── YES → summarizer（完整摘要）
    │       │       │   └── NO
    │       │       │       └── auto（circuit breaker）
    │       │       └── （继续等待或手动触发）
```

---

## 压缩摘要模板

当使用 summarizer 时，中间轮次替换为：

```
## [Compact] Summary
- **Goal**: <任务目标>
- **Progress**: <已完成的关键步骤>
- **Decisions**: <已做出的决策及理由>
- **Files**: <修改过的文件路径>
- **Next**: <下一步计划>
```

---

## 触发时机规范

| 时机 | 策略 | 理由 |
|------|------|------|
| 探索→执行转换 | summarizer | research context 笨重，plan 是蒸馏产出 |
| 调试完成后 | summarizer | debug trace 污染后续无关工作 |
| 死路放弃后 | summarizer | 清除失败推理再尝试新方案 |
| idle > 30s | micro | 临时状态保存 |
| 会话关闭 | sessionMemory | 提取教训到外部记忆 |
| 被动/自动 | auto | 防止上下文溢出 |

**实现中途禁止压缩**（丢失 partial state 代价高）。

---

## 相关文件

- `references/strategy-matrix.md` — 策略对比矩阵
