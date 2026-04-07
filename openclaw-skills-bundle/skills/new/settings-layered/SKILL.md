# Layered Configuration System

**描述**: 多源配置合并：managed → local → CLI → env → MDM → drop-in 六层

---

## 配置合并顺序

```
① managed  →  ② local  →  ③ CLI  →  ④ env  →  ⑤ MDM  →  ⑥ drop-in
     (最低)                                                            (最高)
```

**后面的层覆盖前面的层。**

---

## 各层详情

| 层 | 名称 | 来源 | 优先级 | 格式支持 |
|----|------|------|--------|----------|
| ① | managed | OpenClaw 内置默认配置（代码/内置 defaults） | 最低 | yaml, json |
| ② | local | `~/.openclaw/` 下的用户配置文件 | 低 | yaml, json, env |
| ③ | CLI | 命令行参数 `--config`, `--model`, `--session` 等 | 中 | —（直接覆盖） |
| ④ | env | 环境变量 `OPENCLAW_*` | 高 | env |
| ⑤ | MDM | 移动设备管理策略（企业场景，从管理服务器拉取） | 很高 | json |
| ⑥ | drop-in | `/etc/openclaw.d/` 下的片段文件（文件名排序，字典序靠后的覆盖前面的） | 最高 | yaml, json, env |

---

## 配置热重载

- **触发信号**: `SIGUSR1` 发送给 OpenClaw 进程
- **行为**: 重新按上述顺序加载并合并全部六层配置，替换运行中配置
- **限制**: 某些配置项（如 `--host`、端口绑定）需要重启才生效

```bash
kill -USR1 <openclaw-pid>
```

---

## 配置验证

1. 启动时对合并后的完整配置做 JSON Schema 校验
2. 校验失败时：
   - 记录错误日志（含具体字段和原因）
   - **回退到 managed 层（①）作为 fallback**
   - 继续启动，不阻塞运行
3. 校验范围：模型参数、超时、路径、类型约束

---

## OpenClaw 当前配置实际情况

| 配置项 | 当前行为 |
|--------|----------|
| **session 维护** | session 状态保存在 `~/.openclaw/sessions.json`，退出不自动清理 |
| **cron 保留** | cron jobs 持久化到 `~/.openclaw/jobs.json`，重启后保留 |
| **agents 默认** | 主 agent 默认 model: `minimax/MiniMax-M2-7`，temperature: `0.7` |
| **subagent 超时** | 默认 `300s`（5分钟），可通过 CLI `--subagent-timeout` 或 `OPENCLAW_SUBAGENT_TIMEOUT` 覆盖 |

### 关键环境变量

| 变量 | 作用 |
|------|------|
| `OPENCLAW_MODEL` | 覆盖默认 model |
| `OPENCLAW_SUBAGENT_TIMEOUT` | subagent 超时秒数 |
| `OPENCLAW_CONFIG` | 指向本地配置文件路径 |
| `OPENCLAW_SESSION_DIR` | session 文件存储目录 |

---

## 快速参考

```bash
# 查看当前完整配置（含来源层）
openclaw config --show

# 查看指定层的配置
openclaw config --layer=env
openclaw config --layer=local

# 热重载配置
kill -USR1 $(pgrep -f openclaw)

# 验证配置文件
openclaw config --validate /etc/openclaw.d/*.yaml
```
