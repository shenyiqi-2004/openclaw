# Hook Events Reference

完整事件清单与event对象结构。

---

## 工具执行

### `before_tool_call`
工具执行前触发。

```typescript
{
  toolName: string,   // 工具名称，如 "exec", "read"
  params: object      // 调用参数
}
```

### `after_tool_call`
工具执行后触发。

```typescript
{
  toolName: string,
  params: object,
  result: unknown,    // 执行结果
  error?: Error       // 如有错误
}
```

---

## 模型推理

### `before_model_resolve`
模型选择前触发，可修改模型参数。

```typescript
{
  modelOptions: {
    model?: string,
    temperature?: number,
    maxTokens?: number,
    // ...其他模型选项
  }
}
```

### `before_prompt_build`
Prompt构建前触发，可对prompt进行预处理。

```typescript
{
  prompt: string | Message[],  // 原始prompt
  context: {
    sessionId: string,
    userId?: string,
    channel?: string
  }
}
```

---

## Agent生命周期

### `before_agent_start`
Agent启动前触发。

```typescript
{
  agentConfig: {
    name: string,
    model: string,
    systemPrompt?: string,
    tools?: string[],
    // ...其他配置
  }
}
```

### `subagent_spawning`
子agent创建前触发。

```typescript
{
  task: {
    label: string,
    prompt: string,
    parentSession?: string
  }
}
```

---

## 会话生命周期

### `session_start`
会话建立时触发。

```typescript
{
  sessionId: string,
  context: {
    channel: string,
    userId?: string,
    timestamp: string
  }
}
```

### `session_end`
会话结束时触发。

```typescript
{
  sessionId: string,
  context: {
    channel: string,
    userId?: string,
    durationMs?: number,
    turnCount?: number
  }
}
```

---

## 网络安全

### `before_http_request`
HTTP请求发出前触发，SSRF防护。

```typescript
{
  url: string,        // 目标URL
  method: string,     // HTTP方法
  headers: object,   // 请求头
  body?: string | Buffer
}
```

**返回值**: 返回 `false` 或抛出错误可阻止请求；返回修改后的对象可修改请求参数。
