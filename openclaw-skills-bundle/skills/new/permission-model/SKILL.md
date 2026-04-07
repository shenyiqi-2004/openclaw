# Permission Three-Layer Model

**描述**: 规则匹配→语义分类→沙箱隔离三层权限模型

## 架构总览

```
                    ┌─────────────────────────┐
                    │   permission_check()    │
                    │      API 入口           │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
         ┌─────────┐       ┌───────────┐       ┌──────────┐
         │ Layer 1 │──────▶│  Layer 2  │──────▶│  Layer 3 │
         │ Exact   │ DENY  │ Semantic  │ DENY  │ Sandbox  │
         │ Match   │       │ Intent    │       │ Isolation│
         └─────────┘       └───────────┘       └──────────┘
           O(1)              O(n)                 O(1)
         whitelist/        risk score          container
         blacklist          0-100              profile
```

## 操作类型

| 操作 | 含义 | 危险等级 |
|------|------|----------|
| read | 读取文件/资源 | 低 |
| write | 写入/创建文件 | 中 |
| delete | 删除文件 | 高 |
| execute | 执行命令/脚本 | 高 |
| network | 网络请求/连接 | 高 |

## Layer 1 — 规则匹配

**策略**: exact whitelist/blacklist 精确匹配，O(1) 高速过滤

**规则格式**:
```json
{
  "path": "/home/park/.ssh/*",
  "operation": ["read"],
  "action": "deny"
}
```

**匹配顺序**: blacklist → whitelist → default(deny)

**适用场景**: 已知危险路径（系统文件、密钥目录）、已知安全路径（工作区）

---

## Layer 2 — 语义分类

**策略**: intent 分析 + 风险评分(0-100)，判断操作意图

**评分维度**:

| 维度 | 分值 | 说明 |
|------|------|------|
| path_depth | 0-20 | 路径深度越深越可信 |
| parent_dirs | 0-20 | 父目录是否为可信目录 |
| file_ext | 0-30 | 扩展名风险（.sh+.py+.exe 高） |
| operation_type | 0-30 | 操作类型危险度 |

**阈值**:
- 0-40: allowed
- 41-70: warn + allowed（记录）
- 71-100: denied

**Intent 示例**:
```
target: "/home/park/.ssh/id_rsa"
operation: "read"
→ path_depth=3, parent="/home/park/.ssh"(trusted)=20, ext=".ssh"(low)=5
→ score = 25 → ALLOWED (无警告)

target: "/etc/passwd"
operation: "write"
→ system_path=true, operation=write=30
→ score = 95 → DENIED
```

---

## Layer 3 — 沙箱隔离

**策略**: 若 Layer1+2 通过，给出隔离建议

**隔离维度**:

| 维度 | 选项 | 说明 |
|------|------|------|
| filesystem | none/read-only/temp | 文件系统访问范围 |
| network | none/localhost/full | 网络访问范围 |
| process | spawn/privileged/none | 进程创建权限 |
| memory | limit_mb | 内存上限 |

**配置示例**:
```json
{
  "filesystem": "read-only",
  "network": "localhost",
  "process": "none",
  "memory": 512
}
```

---

## 拒绝追踪 (denialTracking)

**存储结构**:
```json
{
  "id": "uuid",
  "timestamp": "ISO8601",
  "target": "/path",
  "operation": "write",
  "layer": 2,
  "reason": "score=95, system_path=true",
  "context": {
    "session": "agent:xxx",
    "tool": "exec"
  }
}
```

**用途**:
- 审计日志
- 规则自动学习（黑名单自动扩展）
- 误报检测

---

## 权限预检 API

```typescript
interface PermissionRequest {
  target: string;      // 路径或网络地址
  operation: 'read' | 'write' | 'delete' | 'execute' | 'network';
}

interface PermissionResponse {
  allowed: boolean;
  layer: 1 | 2 | 3 | null;
  reason: string;
  score?: number;       // Layer 2 风险评分
  isolation?: SandboxProfile;  // Layer 3 建议
}
```

**调用示例**:
```
输入: { target: "/tmp/test.sh", operation: "execute" }
输出: { allowed: true, layer: 3, reason: "whitelisted", isolation: { filesystem: "read-only", process: "spawn" } }

输入: { target: "/etc/shadow", operation: "write" }
输出: { allowed: false, layer: 1, reason: "blacklist match /etc/*" }
```

---

## 层间对比

| 属性 | Layer 1 | Layer 2 | Layer 3 |
|------|---------|---------|---------|
| 复杂度 | O(1) | O(n) | O(1) |
| 精度 | 精确 | 模糊 | 配置化 |
| 延迟 | <1ms | 5-20ms | <1ms |
| 适用 | 已知路径 | 未知路径 | 高危操作 |
| 决策 | deny/allow | score(0-100) | isolation profile |
| 误报率 | 低 | 中 | 低 |
