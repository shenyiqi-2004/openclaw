# PATTERNS.md — 可复用模式库

> 格式：`[when 场景] → [pattern 模式] → [do 执行]`
> 写入条件：同一模式被执行或纠正 2+ 次
> 使用方式：coding 开始前检索匹配，匹配到直接用

## 环境
- WSL + Edge CDP → 先检查 portproxy 是否存活 → `curl -s http://172.18.160.1:9222/json/version`
- portproxy 丢失（WSL 重启后） → 重建 → `netsh interface portproxy add v4tov4 listenport=9222 listenaddress=172.18.160.1 connectport=9222 connectaddress=127.0.0.1`
- Ollama 连接 → 用 Windows 侧地址 → `http://172.18.160.1:11434`，不是 127.0.0.1

## 飞书
- 多维表格批量写入 → 用 batch_create → 单条循环 create 会触发限流
- 发用户身份消息 → 必须先确认对象和内容 → 不能自动发
- 日历创建 → 必须传 user_open_id → 否则日程只在应用日历上

## OpenClaw
- 重启 gateway → `gateway restart` 工具 → 不用 systemctl
- session 清理 → sessions.json 移除 key + 删 .jsonl + 检查关联 cron
- extension 代码 → 放 extensions/ 不放 npm-global → update 不覆盖
- config 改动 → 用 config.patch 不用 config.apply → 减少全量覆盖风险

## OpenClaw 插件开发（2026-04-04 血泪总结）
- 新插件部署 → 一次 config.patch 改齐 3 处 → plugins.allow + plugins.load.paths + plugins.entries
- definePluginEntry → register 字段（不是 activate） → `definePluginEntry({ id, name, description, register(api, config) {...} })`
- registerTool → 单参数对象 → `api.registerTool({ name, label, description, parameters, execute })` 不是 3 参数
- 新插件 → 先写最小 1-tool spike 确认加载 → 再补完整逻辑，不要一口气 300 行
- 写插件前 → grep SDK dist 确认 API 签名 → `grep -A10 "registerTool\|definePluginEntry" ~/.npm-global/lib/node_modules/openclaw/dist/plugin-entry*.js`

## Coding
- 连续 2 轮无进展 → 停止扩散，返回现状+阻塞+建议
- 缺环境/权限/依赖 → 停，不猜
- 验证状态 → 必须标 Ran/Static/Not run
- 制定计划前 → 先列出平台已有能力 → 只规划增量，不重复造轮子

## 执行循环
- 3+ 步复杂任务 → 先拆再做 → Plan→Execute→Check→Fix→Next 显式循环
- 每步执行后 → 必须验证 → 运行命令/检查输出/读文件
- 同一步修 2 轮仍失败 → 熔断收束 → 不扩散不死循环
- 执行到第 3 步 → mid-task check → 方向校正
- 多步任务 → 维护状态追踪 → ✅🔄⬜❌
- 被打断后恢复 → 先输出当前状态再继续