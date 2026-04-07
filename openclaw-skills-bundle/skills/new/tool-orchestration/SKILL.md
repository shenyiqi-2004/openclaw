# Tool Orchestration Strategy

**描述**: 工具并发调度策略，read-only并发/mutation串行，死锁防护

---

## 1. 工具分类

| 类型 | 工具 | 说明 |
|------|------|------|
| read-only | `read`, `grep`, `glob`, `exec`(只读), `list` | 不修改状态，可并发 |
| mutation | `write`, `edit`, `exec`(修改), `trash`, `delete` | 修改状态，强制串行 |

---

## 2. 并发配置

| 类型 | max并发 | 调度规则 |
|------|---------|---------|
| read-only | 10 | 并发执行 |
| mutation | 1 | 强制串行 |

---

## 3. 死锁防护

- **循环依赖检测**: 构建依赖图，检测环（Tarjan算法），有环则拒绝执行并报警
- **优先级队列**: 工具按 `priority` 字段排序；高优先级先执行；同优先级 FIFO

---

## 4. 调度算法

```
input: 工具列表 [{name, params, priority, deps}]
output: 执行序列

1. 分类: read-only → RO[], mutation → MU[]
2. 依赖解析: 构建 DAG，检测环
3. RO 按优先级排序 → 并发执行（max 10）
4. MU 按优先级排序 → 串行执行
5. MU 必须在 RO 全部完成后才能开始（避免竞态）
```

---

## 5. 工具执行 Hook

| 阶段 | 动作 |
|------|------|
| pre-tool | 权限检查、参数验证、SSRF 检测 |
| post-tool | 结果日志、治理事件记录（`log_governance_event`） |

---

## 6. SSRF 防护

HTTP 请求时阻止以下内网地址段：

| 地址段 | 范围 |
|--------|------|
| 10.0.0.0/8 | 私有 |
| 172.16.0.0/12 | 私有 |
| 192.168.0.0/16 | 私有 |
| 127.0.0.0/8 | localhost |
| ::1 | localhost IPv6 |

命中则拒绝请求并记录 `policy_violation` 事件。

---

## 7. 适用场景

- 多步骤任务需要并发执行独立 read-only 工具时
- 需要确保 mutation 工具执行顺序时
- 需要防止循环依赖导致的死锁时

## 8. 禁忌

- 禁止对同一文件同时并发读写（mutation 串行保护）
- 禁止在 RO 仍在运行时启动有依赖的 MU
- 禁止跳过 SSRF 检测发送 HTTP 请求
