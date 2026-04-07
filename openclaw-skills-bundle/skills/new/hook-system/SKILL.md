# Hook System Reference

**描述**: OpenClaw Hook四种执行模型：Command / Agent / HTTP / JS

---

## 四种执行模型对比

| 维度 | Command | Agent | HTTP | JS |
|------|---------|-------|------|-----|
| 触发方式 | shell命令 | AI模型推理 | Webhook回调 | 沙箱JS执行 |
| PTY支持 | ✅ | ❌ | ❌ | ❌ |
| before/after模型 | ❌ | ✅ | ❌ | ❌ |
| SSE/StreamableHTTP | ❌ | ❌ | ✅ | ❌ |
| 安全隔离 | 系统级 | 模型推理隔离 | 网络隔离 | 沙箱隔离 |
| 适用场景 | 交互CLI、日志染色 | 推理拦截、内容过滤 | 外部系统集成 | 轻量逻辑扩展 |

---

## Hook注册

```typescript
registerHook(hookName: string, handler: HookHandler, opts?: HookOptions): void
```

**opts参数**:

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `priority` | `number` | `0` | 优先级，数值越高越先执行 |
| `catchErrors` | `boolean` | `true` | hook失败不影响主流程 |
| `once` | `boolean` | `false` | 仅执行一次后自动注销 |

---

## 已知Hook事件

```typescript
// 工具执行
'before_tool_call'   // event: { toolName, params }
'after_tool_call'    // event: { toolName, params, result }

// 模型推理
'before_model_resolve'  // event: { modelOptions }
'before_prompt_build'   // event: { prompt }

// Agent生命周期
'before_agent_start'    // event: { agentConfig }
'subagent_spawning'     // event: { task }

// 会话生命周期
'session_start'         // event: { sessionId, context }
'session_end'           // event: { sessionId, context }

// 网络安全
'before_http_request'   // event: { url, method, headers } — SSRF防护钩子
```

---

## SSRF防护

`before_http_request` 钩子在HTTP请求发出前检查目标地址：

- 拦截内网IP段（`10.x`, `172.16-31.x`, `192.168.x`, `127.x`）
- 拦截`localhost`/`0.0.0.0`
- 拦截非标准端口（除80/443）
- 允许自定义白名单

---

## 错误处理

- `catchErrors` 默认为 `true`：hook抛出的异常被捕获并记录，主流程继续执行
- `catchErrors` 设为 `false`：hook异常将中断当前操作并向上传播
- 建议：关键业务hook设置 `catchErrors: false`，扩展性hook保持默认

---

## 文件结构

```
hook-system/
├── SKILL.md
└── references/
    └── hook-events.md
```
