# MCP Transport Protocols

**描述**: MCP三种传输协议 Stdio / SSE / StreamableHTTP 的适用场景对比

---

## 传输协议对比

| 特性 | **Stdio** | **SSE** | **StreamableHTTP** |
|------|-----------|---------|---------------------|
| 通信模式 | 标准输入输出 | 服务器推送 | 双向流 |
| 方向 | 单向（parent→child） | 单向（server→client） | 双向 |
| 延迟 | 低 | 中 | 低 |
| 传输格式 | JSON-stdio | EventStream | Chunked transfer / JSON |
| 进程管理 | 需要子进程管理 | 无 | 无 |
| 浏览器友好 | 否 | 是 | 是 |
| 典型场景 | 本地MCP Server | 简单通知/推送 | 实时AI响应 |

---

## 适用场景矩阵

| 场景 | 推荐协议 |
|------|----------|
| 本地 MCP Server | **Stdio** |
| 远程 MCP Server | SSE 或 StreamableHTTP |
| 实时 AI 对话 | **StreamableHTTP** |
| 简单请求/响应 | SSE |
| 需要低延迟工具调用 | **Stdio** 或 **StreamableHTTP** |
| 跨网络防火墙限制 | SSE |

---

## 安全考虑

- **TLS**: 生产环境远程通信必须启用 TLS
- **认证**: HTTP-based 协议支持 Bearer Token / OAuth
- **速率限制**: 防止 DoS，建议在网关层配置
- **输入验证**: 所有协议均需严格校验 JSON payload
- **网络隔离**: Stdio 仅限本地，不暴露网络接口

---

## OpenClaw MCP 工具包装逻辑

OpenClaw 通过 MCP SDK 连接 Server 时，根据 Server URL 自动选择传输层：

```
stdio://... 或无 scheme   → StdioTransport
http://...                → StreamableHTTPTransport
https://...               → StreamableHTTPTransport (TLS)
```

**工具调用流程**:

1. 解析 `mcpServers` 配置，获取 `command` / `url`
2. 实例化对应 Transport（stdio / http）
3. 建立 MCP session，交换 JSON-RPC 消息
4. 工具结果通过 transport 返回，OpenClaw 解析 `content` 字段

**Stdio 配置示例**:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

**HTTP 配置示例**:

```json
{
  "mcpServers": {
    "remote": {
      "url": "https://mcp.example.com/sse"
    }
  }
}
```

---

## 选型决策树

```
是否本地进程？
  ├─ 是 → Stdio
  └─ 否 → 是否需要实时双向交互？
            ├─ 是 → StreamableHTTP
            └─ 否 → SSE
```
