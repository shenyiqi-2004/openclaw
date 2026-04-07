# Bug Round Number System

**描述**: Round编号制bug回归网，每个bug有编号+测试+回归验证

---

## 1. Round编号规范

| 属性 | 规范 |
|------|------|
| 格式 | `Round-{number}-{year}{month}`，例 `Round-001-202604` |
| 编号策略 | 每个bug分配唯一编号，**不复用** |
| 顺序 | 编号从小到大，标记修复顺序 |

**文件命名**: `Round-{number}-{year}{month}.md`，如 `Round-001-202604.md`

---

## 2. Bug严重程度分级

| 等级 | 标识 | 说明 |
|------|------|------|
| Critical | `CRITICAL` | 系统崩溃、数据丢失、安全漏洞 |
| High | `HIGH` | 核心功能失效、严重用户体验问题 |
| Medium | `MEDIUM` | 非核心功能异常、可绕过 |
| Low | `LOW` | 界面瑕疵、文档错误、无实际影响 |

---

## 3. Bug文档模板

```markdown
# Round-{number}-{year}{month}

**日期**: YYYY-MM-DD
**严重程度**: [CRITICAL / HIGH / MEDIUM / LOW]
**状态**: [Open / Fixed / Verified / Closed]

---

## 触发条件

[复现步骤]

## 根因分析

[技术根因]

## 修复方案

[具体修复内容]

## 验证方法

[验证步骤]

## 回归测试用例

| 用例ID | 测试场景 | 预期结果 | 状态 |
|--------|----------|----------|------|
| TC-001 |  |  | Pass/Fail |

## 关联

- 上一轮: Round-{n-1}-YYYYMM
- 下一轮: Round-{n+1}-YYYYMM
```

---

## 4. 回归网（Regression Web）

**规则**:
- 所有Round按时间线串联
- 新Round修复后，**必须**验证不破坏旧Round
- 验证方式：执行旧Round的回归测试用例

**回归验证记录**:
```markdown
## 回归验证

| 旧Round | 验证用例 | 结果 | 验证人 | 日期 |
|---------|----------|------|--------|------|
| Round-001-202604 | TC-001 | Pass |  |  |
```

---

## 5. 工具支持

**搜索**:
```bash
# 按Round编号搜索
grep -r "Round-001" .

# 按严重程度搜索
grep -r "CRITICAL\|HIGH" .

# 按关键词搜索
grep -ri "关键词" .
```

**文件结构**:
```
{workspace}/
└── bugs/
    ├── Round-001-202604.md
    ├── Round-002-202604.md
    └── ...
```

---

## 6. OpenClaw四层Bug追踪

| 层级 | 追踪内容 | 工具 |
|------|----------|------|
| Gateway | 网络、认证、连接问题 | `openclaw gateway status` |
| Agent | LLM调用、响应生成异常 | session日志 |
| Plugin | 插件加载、API调用失败 | 插件日志 |
| Skill | Skill逻辑错误、模板偏差 | Round文档 |

**Bug上报流程**:
1. 在对应层级创建Round文档
2. 填入模板，标记严重程度
3. 修复后执行回归测试
4. 验证不破坏其他Round后关闭
