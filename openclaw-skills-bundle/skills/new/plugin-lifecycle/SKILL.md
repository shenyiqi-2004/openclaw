# Plugin Lifecycle Management

OpenClaw Plugin lifecycle: discover → validate → load → reconcile → cache

## 目录结构

```
skills/plugin-lifecycle/
└── SKILL.md   # 主文件
```

---

## 1. 生命周期阶段

### 1. discover
扫描 `paths` 配置，发现插件目录。

- 读取 `openclaw.extensions`（在 `package.json` 中）或等效配置
- 遍历每个路径，递归查找包含 `openclaw.plugin.json` 的目录

### 2. validate
检查 manifest、依赖、权限。

- 读取 `openclaw.plugin.json`（plugin manifest）
- 验证 `name`、`version`、`main` 字段存在
- 检查 `engines.openclaw` 版本兼容
- 解析 `dependencies`，检查运行时依赖是否满足
- 验证 `permissions`（网络、文件系统等）是否在白名单内

### 3. load
jiti 动态导入，ESM/CJS 解包。

- 使用 `jiti` 或 `createRequire` 动态加载 `main` 入口
- ESM 模块：解包 `default` 导出（插件入口通常是 `export default`）
- CJS 模块：直接 `require`
- **坑**：ESM 插件导出的是 `{ default: { default: ActualPlugin } }`（双层 default），需要解两层
- 实例化插件类或调用工厂函数，传入 `registerTool`/`registerHook` 等 API

### 4. reconcile
对比配置变化，注册/注销 tools/hooks。

- 对比新加载的 plugin 与缓存状态
- 注册新 tools → 更新 tool list
- 注册新 hooks → 更新 hook map
- 注销已移除的 tools/hooks
- **坑**：`registerTool` 的 `execute` 字段在 manifest 中叫 `handler`，字段名不同

### 5. cache
缓存已加载插件状态，加速下次启动。

- 持久化 plugin manifest + resolved path + version
- 下次启动时，`discover` 阶段直接命中缓存，跳过 validate + load
- 配置变更（paths 修改）时清除缓存

---

## 2. 关键文件

| 文件 | 位置 | 用途 |
|---|---|---|
| `openclaw.plugin.json` | 插件根目录 | Plugin manifest，定义 name/version/main/permissions/hooks |
| `package.json` | 插件根目录 | 声明 `engines.openclaw`、`dependencies`，可选 `openclaw.extensions` |

**openclaw.plugin.json 示例**
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "main": "dist/index.js",
  "engines": { "openclaw": ">=1.0.0" },
  "permissions": ["network"],
  "hooks": ["onMessage"]
}
```

**package.json 中的扩展配置**
```json
{
  "openclaw": {
    "extensions": ["./plugins/*"]
  }
}
```

---

## 3. registerTool 签名

单参数对象形式：

```ts
registerTool({
  name: string,          // 唯一标识，如 "github-search"
  label: string,        // 显示名称
  description: string,  // 功能描述
  parameters: object,   // JSON Schema（用于 UI 表单生成）
  execute: Function     // 执行函数 (params, context) => Promise<result>
})
```

**注意**：manifest 的 `tools[].handler` 字段对应这里 `execute`，字段名不同。

---

## 4. registerHook 签名

位置参数形式：

```ts
registerHook(hookName: string, handler: Function, opts?: {
  priority?: number   // 越小越先执行，默认 0
})
```

常用 hook：
- `onStart` — 插件加载完成后
- `onMessage` — 收到消息时
- `onToolCall` — tool 被调用前/后
- `preSwing` — swing 处理前

---

## 5. 已知坑

| 坑 | 描述 | 绕过方案 |
|---|---|---|
| `handler` vs `execute` 字段名 | manifest 用 `handler`，registerTool 用 `execute` | 映射表转换，或约定统一用 `execute` |
| ESM 双层 default 解包 | `export default` 在 jiti 中变成 `{ default: { default: ActualPlugin } }` | 加载后手动解包两层：`mod.default?.default ?? mod.default ?? mod` |
| `configSchema` 不能放 runtime | plugin 可能在不同进程/沙箱运行，schema 校验应在 load 前完成 | 将 schema 放 `openclaw.plugin.json`，validate 阶段校验，runtime 只读 `config` |

---

## 6. 调试方法

直接调用 tool 验证，不依赖加载日志。

1. **列出已注册 tools**：`GET /tools` 或通过 `openclaw tools list`
2. **手动调用 tool**：`POST /tools/{name}` + 参数，验证返回值
3. **列出已注册 hooks**：`GET /hooks` 或通过 `openclaw hooks list`
4. **触发 hook**：`POST /hooks/{hookName}` + payload，验证 handlers 是否被调用
5. **检查缓存**：`openclaw plugin-cache --list`，手动清除 `openclaw plugin-cache --clear`

**禁止**：通过查看加载日志来推断插件状态——日志可能不完整或被过滤，直接用 tool/hook 调用结果说话。
