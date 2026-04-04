# OpenClaw Evolution Protocol

让 OpenClaw 超越 Claude Code 的记忆与反思系统。

## 5 模块架构

| 模块 | 做什么 | 核心优势 |
|------|--------|---------|
| **1. 结构化记忆** | 4 类分类（user/feedback/project/reference）+ LanceDB hybrid retrieval | 比 Claude Code 快（本地）且免费 |
| **2. 反思协议** | 每轮 coding 强制结构化反思 + 分类归档 | 比两者都主动（每轮 vs 被动压缩时） |
| **3. 模式提取** | 持续积累 PATTERNS.md + 向量匹配检索 | 比 CLAUDE.md 自动 + 持续 |
| **4. 技能建议** | 3+ 次重复流程 → 自动建议生成新 skill | 比手写更主动 |
| **5. Evolution Extension** | 3 tools: reflect / pattern_match / evolve | 原生集成，不拦截 native tools |

## 目录结构

```
evolution-protocol/
├── MEMORY.md              ← 记忆索引（无敏感路径）
├── AGENTS.md              ← 完整协议规则
├── PATTERNS.md            ← 可复用模式库
├── skills/                ← 3 个协议级 skill
│   ├── reflection/
│   ├── pattern-extract/
│   └── skill-suggest/
└── docs/
    ├── memory-system.md
    ├── reflection-protocol.md
    └── implementation.md
```

## 与 Claude Code / Hermes 对比

| | Claude Code | Hermes | OpenClaw + Evolution |
|---|---|---|---|
| 记忆分类 | 4 种 ✓ | 2 文件 | **4 种 + 目录化** |
| 记忆检索 | Sonnet（贵） | 无 | **LanceDB（本地）** |
| 反思 | 被动压缩时 | 被动压缩时 | **每轮主动 + 分类归档** |
| 模式积累 | 手写 CLAUDE.md | 无 | **自动提取 + 向量匹配** |
| 上下文压缩 | snipCompact | ContextCompressor | **LCM DAG（最强）** |

## 核心设计原则

1. **协议 > 代码**：显式协议 + tool 检查点，比隐式模型循环更可靠
2. **永远不拦截 native tools**：fusion_handle 是可选增强，不是阻塞
3. **文件 > 脑记**：所有记忆必须写文件，不做 mental note
4. **熔断机制**：同一步 2 轮失败 → 强制收束，不死循环
5. **update 安全**：所有内容在 `~/.openclaw/workspace/` 和 `extensions/`，不受 openclaw update 影响

## Phase 1-3 已完成实施

详见 [docs/implementation.md](docs/implementation.md)

## 快速开始

1. 克隆本仓库
2. 将 `AGENTS.md` 和 `PATTERNS.md` 放入 `~/.openclaw/workspace/`
3. 将 `memory/` 目录放入 `~/.openclaw/workspace/`
4. 将 `skills/{reflection,pattern-extract,skill-suggest}/` 放入 `~/.openclaw/workspace/skills/`
5. 可选：安装 [openclaw-evolution extension](https://clawhub.ai) 获取 3 个原生 tool

## License

MIT
