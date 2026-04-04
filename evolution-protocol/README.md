# OpenClaw Evolution Protocol

让 OpenClaw 超越 Claude Code 的记忆与反思系统。

## 5 模块架构

| 模块 | 做什么 | 核心优势 |
|------|--------|---------|
| **1. 结构化记忆** | 4 类分类（user/feedback/project/reference）+ LanceDB hybrid retrieval | 比 Claude Code 快（本地）且免费 |
| **2. 反思协议** | 每轮 coding 强制结构化反思 + 分类归档 | 比两者都主动（每轮 vs 被动压缩时） |
| **3. 模式提取** | 持续积累 PATTERNS.md + 向量匹配检索 | 比手写 CLAUDE.md 自动 + 持续 |
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

### Claude Code vs OpenClaw + Evolution

| | Claude Code | OpenClaw + Evolution |
|---|---|---|
| 记忆分类 | 4 种 ✓ | **4 种 + 目录化** |
| 记忆检索 | Sonnet（贵，每次选花 API 钱） | **LanceDB（本地，免费，<100ms）** |
| 反思 | 被动（上下文压缩时才提取） | **每轮 coding 后主动 + 分类归档** |
| 模式积累 | 手写 CLAUDE.md | **自动提取 + PATTERNS.md + 向量匹配** |
| 上下文压缩 | snipCompact | **LCM DAG（最强）** |
| 熔断机制 | 无（会死循环） | **2 轮 fail → 强制收束** |
| Subagent 清理 | 无规范 | **强制清理 subagent** |

### Hermes vs OpenClaw + Evolution

**Hermes**（`~/hermes-agent/`，Python）是另一个 OpenClaw 外挂智能体。它有记忆层，但设计思路不同：

| | Hermes | OpenClaw + Evolution |
|---|---|---|
| 记忆架构 | MemoryProvider ABC + 2 文件（user/project） | **4 类目录 + LanceDB hybrid** |
| 记忆检索 | 无检索（直接读文件） | **向量检索（qwen3-embedding）+ BM25** |
| 反思 | 被动（上下文压缩时才提取） | **每轮 coding 后主动反思** |
| 模式积累 | 无 | **PATTERNS.md 持续积累 + 提取流程** |
| 技能建议 | 无 | **3+ 次重复 → 自动建议生成 skill** |
| 上下文压缩 | ContextCompressor | **LCM DAG（最强）** |
| 威胁检测 | MEMORY_THREAT_PATTERNS（12 条 regex） | **沙箱隔离 + 蒸馏写入** |
| 工具路由 | MemoryManager tool routing | **evolution 原生 3-tool** |
| skill 数量 | slash_commands（手写） | **85+ skills 目录，持续扩充** |

**Hermes 的弱点**：
1. **记忆检索靠读文件**，没有向量检索，大记忆库会变慢
2. **没有主动反思协议**，依赖压缩时机，容易错过后续任务需要的教训
3. **没有模式积累机制**，每次遇到同类问题都要重新摸索
4. **没有 skill 自动化建议**，只能手写 slash_commands
5. **skill 依赖手写**，无法根据使用频率自动推荐

**OpenClaw + Evolution 胜出点**：
- 记忆检索快（本地向量）且免费，Hermes 读文件在大记忆库下会越来越慢
- 每轮主动反思，不依赖压缩时机，教训不遗漏
- 持续积累模式，后续遇到同类问题直接复用，不用重新探索
- 熔断机制防止死循环，Hermes 无此保护

### 核心设计原则（为什么协议 > 代码）

1. **显式协议 + tool 检查点 > 隐式模型循环**：Claude Code 的 self-correction 靠模型自己判断，容易死循环；Evolution 用 `evolution_reflect` tool 强制检查点
2. **熔断机制**：同一步 2 轮失败 → 强制收束，不扩散
3. **文件 > 脑记**：所有记忆写文件，不做 mental note
4. **永远不拦截 native tools**：fusion_handle 是可选增强，不是阻塞
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
