---
name: code-review
description: "全面代码审查：正确性、安全性、性能、可维护性、测试覆盖。支持多语言（TS/JS/Python/Go/Rust）。合并了 ECC security-review 的安全清单。"
---

# Code Review

## When to Use
- PR review / merge request 审查
- 重构前的质量评估
- 新功能上线前的安全检查
- 用户说"review this code"、"帮我看看代码"

## 审查维度（按优先级排序）

### 1. 正确性 — CRITICAL
- 功能是否符合需求/spec
- 边界条件：null/undefined/empty/0/负数/MAX_INT
- 并发安全：race condition、deadlock、stale closure
- 错误处理：是否 catch 了所有可能的异常路径
- 状态管理：mutation vs immutable、副作用隔离

### 2. 安全性 — CRITICAL
- **Secrets**：无硬编码 API key/token/password，全部走环境变量
- **Input Validation**：所有用户输入用 schema 校验（zod/joi/pydantic）
- **SQL Injection**：禁止字符串拼接 SQL，必须 parameterized/ORM
- **XSS**：用户内容必须 sanitize（DOMPurify），CSP headers
- **CSRF**：state-changing 操作有 CSRF token，cookie SameSite=Strict
- **Auth/AuthZ**：token 在 httpOnly cookie（不在 localStorage），操作前检查权限
- **Rate Limiting**：API 有限流，昂贵操作（AI/搜索）有更严格限制
- **Sensitive Data**：不 log 密码/token/卡号，错误信息不暴露内部细节

### 3. 性能
- 时间/空间复杂度是否合理
- 数据库：N+1 查询、缺少索引、全表扫描
- 内存：资源泄漏（未关闭连接/文件/stream）
- 网络：不必要的请求、缺少缓存、payload 过大
- 前端：不必要的 re-render、bundle size

### 4. 可维护性
- 命名清晰：函数名 = 动词+名词，变量名 = 名词
- 单一职责：函数 <40 行，类/模块职责单一
- DRY：无重复逻辑（但避免过早抽象）
- 注释：只注释 Why，不注释 What
- 类型：TypeScript 项目无 `any`/`as`，Python 项目有 type hints

### 5. 测试覆盖
- 关键路径有单元测试
- 边界条件有测试用例
- 错误路径有测试
- 测试是否测行为（不是测实现细节）

### 6. 架构一致性
- 是否遵循项目已有 pattern
- 目录结构是否一致
- API 风格是否统一（RESTful/GraphQL/tRPC）
- 错误处理风格是否统一

## 输出格式

```markdown
## Code Review Report

### 📊 Summary
| 维度 | 评级 | 问题数 |
|------|------|--------|
| 正确性 | ✅/⚠️/❌ | N |
| 安全性 | ✅/⚠️/❌ | N |
| 性能 | ✅/⚠️/❌ | N |
| 可维护性 | ✅/⚠️/❌ | N |
| 测试 | ✅/⚠️/❌ | N |

### 🔴 Must Fix (blocking)
1. [file:line] 问题描述 → 修复建议

### 🟡 Should Fix (non-blocking)
1. [file:line] 问题描述 → 修复建议

### 🟢 Nice to Have
1. [file:line] 优化建议

### ✅ Highlights
- 值得表扬的设计/实现
```

## 多语言检查项

### TypeScript/JavaScript
- `any` 和 `as` 类型断言
- `==` vs `===`
- async/await 错误处理（try/catch 或 .catch）
- React: useEffect cleanup、dependency array
- Node: process.exit 清理、graceful shutdown

### Python
- type hints 覆盖
- with 语句管理资源
- f-string vs format 一致性
- async: await 遗漏、event loop 阻塞

### Go
- error 必须检查（不 `_ = err`）
- goroutine 泄漏（context cancellation）
- defer 顺序（LIFO）
- interface 最小化

### Rust
- unwrap()/expect() 在 production 代码中
- lifetime 标注合理性
- Clone 的必要性
- unsafe 块的安全性论证

## Review 策略

1. **先全局后细节**：先读 PR description + file list，理解改动意图
2. **先 diff 后全文**：先看改动行，再看上下文
3. **按严重度排序**：安全 > 正确性 > 性能 > 其他
4. **给出修复代码**：不只说"这里有问题"，给出具体修复

## Permission & MCP Audit (from Claude Code)

权限审查和 MCP 工具安全审查，针对工具调用层面的安全风险。

### 权限审查检查项

#### 文件操作权限控制
- ❌ 文件操作未限定路径范围（如 `read('/etc/passwd')`）
- ✅ 所有文件操作必须限定在白名单目录内
- ✅ 检查 `..` 路径遍历（Unix）和 `..\\` / `..%2f`（Windows）
- ✅ 禁止对 `/`, `/etc`, `/sys`, `C:\\Windows` 等系统目录进行写操作
- ✅ 临时文件用 `mktemp` / `os.mktemp`，禁止硬编码路径

#### 网络请求 SSRF 风险
- ❌ 直接使用用户提供的 URL 而不验证
- ✅ 所有 URL 必须经过 scheme + host 白名单验证
- ✅ 检测内网 IP 段：`127.0.0.1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`（云元数据）
- ✅ 检测 URL _redirect 链中的敏感端点
- ✅ DNS rebinding 防护：验证 Host header 与解析 IP 一致

#### 子进程调用安全
- ❌ 直接使用用户输入拼接 shell 命令
- ✅ 使用列表形式传参（`subprocess.run([...], shell=False)`）
- ✅ 禁止 `shell=True`，除非命令完全静态且经过严格验证
- ✅ 环境变量传递使用 `env=` 参数，禁止继承不信任的环境变量

#### 环境变量敏感信息检测
```bash
# 常见敏感环境变量（不应暴露到日志/错误/响应中）
env | grep -iE 'secret|token|key|password|credential|private|api_key|AKIA|AWS'
```
- ❌ 禁止将 `env` 内容记录到日志或返回给用户
- ✅ 使用前检查变量是否存在，避免 KeyError 暴露变量名

### MCP 工具安全审查

#### 工具参数 Schema 校验
- ❌ 工具参数直接透传给下游 API/命令，无校验
- ✅ 所有工具参数必须经过 JSON Schema 或等效校验
- ✅ 校验类型（string/number/boolean/object）和范围（minLength/maxItems）
- ✅ 禁止参数中包含未定义字段（防止 additionalProperties 逃逸）
- ✅ 敏感参数（file_path, url, command）使用严格的正则白名单

#### 工具输出大小限制
- ❌ 工具返回无限制数据，可能导致内存耗尽
- ✅ 强制实施输出大小限制：文件读取 `≤10MB`，API 响应 `≤1MB`
- ✅ 大文件使用流式读取/分页，禁止一次性加载到内存
- ✅ list 操作实施 page_size 上限（默认 50，最大 500）

#### 工具错误安全处理
- ❌ 错误信息暴露内部路径、堆栈、库版本
- ✅ 错误信息只返回必要信息：操作类型 + 失败原因（不包含路径）
- ✅ 堆栈跟踪只出现在服务端日志，不出现在响应中
- ✅ 防止 error-based 信息泄露：避免将内部错误直接 `str(error)` 返回

#### MCP 工具特别检查
| 风险项 | 检测 | 防御 |
|--------|------|------|
| 文件系统工具遍历 | 路径包含 `..` | 解析为绝对路径后验证在白名单内 |
| 网络工具 SSRF | URL 包含内网 IP | HEAD 请求前先 DNS 解析验证 |
| 代码执行工具注入 | 命令包含 `;`, `\|`, `$()` | 列表参数 + `shell=False` |
| 搜索工具结果污染 | 返回内容包含恶意脚本 | 输出内容执行 HTML 转义 |

---
Origin: 增强自 OpenClaw 原始 code-review skill + ECC security-review checklist。

### 新增：MCP工具审查

MCP Server工具包装审查要点：
- 工具参数schema是否完整（name/description/parameters）
- 返回值是否安全过滤（敏感信息脱敏）
- 错误处理是否泄露内部路径
- 超时设置是否合理
- 是否有SSRF风险（HTTP请求目标地址验证）

### 新增：权限审查

权限相关代码审查：
- 配置文件写入前是否校验schema
- 敏感操作(exec/write/trash)前是否有权限预检
- hook执行失败是否影响主流程
- 拒绝追踪(denialTracking)是否记录完整

### 新增：Plugin SDK审查

OpenClaw Plugin审查清单：
- registerTool单参数形式 {name, label, description, parameters, execute}
- registerHook位置参数 (hookName, handler, opts?)
- tool字段名必须是execute不是handler
- configSchema不能放runtime导出对象
- ESM default export双层解包处理
