# MEMORY.md — 记忆索引

> 本文件是记忆索引，具体内容在 `memory/` 子目录。
> 写记忆时按类型分类，不要往这里塞内容。
> 本文件通过 boot-md 自动加载到每个 session，关键摘要写在下方。

## 记忆目录

### memory/user/ — 用户画像
- `owner-profile.md` — 技术水平、沟通风格、偏好、雷区、工作模式

### memory/feedback/ — 行为纠正
- `core-rules.md` — 核心规则（不造轮子、不碰网络、不列选项、清理 subagent、反思要实质、读 SDK 再写代码、register 不是 activate、config 一次改完、spike first）
- `auto-lessons.md` — 自动归档的教训

### memory/project/ — 项目状态
- `openclaw-evolution.md` — Evolution 项目完成状态

### memory/reference/ — 外部指针
- `system-locations.md` — 系统关键路径（运行时、配置、源码位置）

### memory/YYYY-MM-DD.md — 每日日志
按日期存放的操作日志，不分类。

## 关键教训速查（前 5 条最重要）
1. 写插件前 grep SDK dist 确认 API 签名，不要凭记忆
2. registerTool 单参数 { name, label, description, parameters, execute }
3. definePluginEntry 用 register 不是 activate
4. 新插件 config.patch 一次改齐 plugins.allow + load.paths + entries
5. 先 spike 1 tool 验证加载，再写完整逻辑

## LanceDB 写入规范
- category 对齐 4 种类型：preference→user, fact→feedback/reference, entity→project, decision→feedback
- scope: `agent:main`
- 每条 ≤200 字，蒸馏结论，不存原始聊天
- **允许写入**：用户偏好、环境事实、稳定结论、操作流程
- **禁止写入**：原始聊天消息、heartbeat 轮询、临时排障记录、一次性指令
