---
name: edge-browser
description: 通过 WSL2 连接用户 Windows Edge 浏览器（CDP），保留登录态/书签/历史。
read_when:
  - 用户要求打开网页、搜索、浏览器操作
  - 用户提到 Edge、浏览器、打开网站
  - 需要截图、网页自动化
  - browser 工具报错连不上
---

# Edge 浏览器 CDP 连接

## 架构

```
Edge (Win 127.0.0.1:9222) ← portproxy (172.18.160.1:9222) ← WSL2 curl/browser工具
```

## 自动化机制（已部署）

**计划任务 `EdgePortProxy`**：用户登录时自动执行 `C:\tmp\edge_cdp_setup.bat`，以最高权限运行。

脚本做两件事：
1. 建 portproxy：`netsh interface portproxy add v4tov4 listenport=9222 listenaddress=172.18.160.1 connectport=9222 connectaddress=127.0.0.1`
2. 如果没有带 9222 的 Edge 在跑，自动启动一个：`start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --no-first-run`

这样不管用户后续怎么打开 Edge（快捷方式、URL 关联、OpenClaw 控制面板 `--app` 等），都会复用这个带 CDP 的主进程。

**补充措施**：
- Edge Startup Boost 已关闭：`HKLM:\SOFTWARE\Policies\Microsoft\Edge\StartupBoostEnabled = 0`（防止后台偷跑无 CDP 进程）
- 桌面 + 任务栏快捷方式目标已加 `--remote-debugging-port=9222`（双保险）

## 连接检测与修复

```bash
# 1. 快速测试
curl -s --connect-timeout 3 http://172.18.160.1:9222/json/version

# 2. 返回 JSON 有 "Browser": "Edg/..." → 正常，直接用 browser 工具

# 3. 连不上 → 分步排查：
```

### 排查步骤

**Step 1：Edge 是否带 9222 运行？**
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | Where-Object {-not (\$_.CommandLine -match '--type=')} | Select-Object ProcessId, CommandLine | Format-List"
```
- 看主进程命令行有没有 `--remote-debugging-port=9222`
- 如果没有 → Edge 被其他方式（如 OpenClaw `--app`）先启动了。需要用户关掉所有 Edge 窗口再从快捷方式重开，或者手动跑计划任务：`schtasks /run /tn EdgePortProxy`

**Step 2：portproxy 是否存在？**
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "netsh interface portproxy show all"
```
- 空输出 → 重建：
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "Start-Process netsh.exe -ArgumentList 'interface portproxy add v4tov4 listenport=9222 listenaddress=172.18.160.1 connectport=9222 connectaddress=127.0.0.1' -Verb RunAs -Wait"
```

**Step 3：一键修复（跑计划任务）**
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "schtasks /run /tn EdgePortProxy" 2>&1
sleep 3
curl -s --connect-timeout 3 http://172.18.160.1:9222/json/version
```

## browser 工具用法

```
browser(action="status")                                         # 连接状态
browser(action="tabs")                                           # 列标签页 → 拿 targetId
browser(action="open", url="...")                                # 新标签打开 URL
browser(action="screenshot")                                     # 当前页截图
browser(action="snapshot", targetId="xxx", compact=true)         # DOM 快照
browser(action="act", kind="click", ref="e12", targetId="xxx")  # 点击
browser(action="act", kind="type", ref="e36", text="内容", targetId="xxx") # 输入
browser(action="navigate", targetId="xxx", url="...")            # 导航
browser(action="close", targetId="xxx")                          # 关闭标签
```

**注意**：snapshot 返回的 ref（如 e12）是临时的，每次 snapshot 后都会变。必须先 snapshot 再用 ref 操作。

## 已知坑

| 问题 | 原因 | 解决 |
|------|------|------|
| curl 连不上但 Edge 在跑 | portproxy 丢了（WSL 重启就丢） | 重建 portproxy 或跑 `schtasks /run /tn EdgePortProxy` |
| Edge 带 9222 但 curl 不通 | portproxy 没建 | 同上 |
| Edge 主进程没有 9222 | 被 OpenClaw 控制面板 `--app` 或 URL 关联先启动了 | 用户关掉所有 Edge → 从快捷方式重开；或 `schtasks /run /tn EdgePortProxy`（脚本会检测并补启动） |
| browser(status) 超时 | gateway 缓存了旧连接 | 先 curl 确认通，再 `gateway restart` |
| PowerShell 中 $_ 被吃 | bash→PowerShell 参数传递问题 | 避免 Where-Object 用 `$_`，改用 `-Filter` 或 `-match` |
| cmd.exe 报 UNC 路径错误 | WSL 工作目录是 `\\wsl.localhost\...` | 加 `workdir=/tmp` 或 `/mnt/c/Windows/System32` |

## 绝对禁止

1. ❌ **taskkill 杀 Edge** — 关用户所有标签页，数据丢失
2. ❌ 改 `.wslconfig` networkingMode — VPN 冲突，WSL 全网断
3. ❌ 碰系统网络拓扑（VPN/防火墙/路由表/DNS）
4. ❌ `--user-data-dir` — 丢登录态
5. ❌ 硬编码 `127.0.0.1:9222` — WSL 的 127.0.0.1 不是 Windows
6. ❌ `profile=user` — 那是 Linux Chrome
7. ❌ `elevated=true` — 不可用，用 `Start-Process -Verb RunAs`

## 参数速查

| 项目 | 值 |
|------|------|
| Edge 调试端口 | 9222 |
| WSL 连接地址 | `http://172.18.160.1:9222` |
| OpenClaw profile | `remote` |
| portproxy | `172.18.160.1:9222 → 127.0.0.1:9222` |
| Edge 路径 | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` |
| 自动化脚本 | `C:\tmp\edge_cdp_setup.bat` |
| 计划任务 | `EdgePortProxy`（onlogon, highest） |
| WSL2 网关 | `172.18.160.1`（NAT 模式） |
| PowerShell 路径 | `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe` |
| cmd 路径 | `/mnt/c/Windows/System32/cmd.exe` |
| workdir 注意 | 调 Windows 命令时设 `/tmp` 避免 UNC 路径错误 |
