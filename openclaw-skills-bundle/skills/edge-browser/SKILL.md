---
name: edge-browser
description: "WSL2 NAT 模式下通过 CDP 控制 Windows Edge 浏览器的完整指南。包含 portproxy、防火墙、排障流程、常见问题解决方案。"
---

# Edge Browser — WSL2 远程 CDP 控制指南

## 概述
在 WSL2 (NAT 模式) 下通过 Chrome DevTools Protocol (CDP) 控制 Windows 上的 Edge 浏览器。
本 skill 记录了完整的连接架构、踩坑经验和永久解决方案。

## 架构

```
OpenClaw (WSL2) ---> 172.18.160.1:9222 --[portproxy]--> 127.0.0.1:9222 ---> Edge (Windows)
```

- **OpenClaw** 运行在 WSL2 Linux 中
- **Edge** 运行在 Windows，监听 `127.0.0.1:9222`
- **portproxy** 是 Windows 内置的端口转发，将 WSL 网关 IP 的请求转发到 Windows 本地回环
- **防火墙** 必须允许 WSL 子网 (172.18.0.0/16) 访问 9222 端口

## 前置条件

### 1. Edge 必须带调试端口启动
```
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
```
- ⚠️ **关键踩坑**：如果 Edge 已经在运行（不带调试端口），后启动的带端口实例**无效**。必须先关闭所有 Edge 进程再启动
- 验证方法（Windows PowerShell）：`curl http://127.0.0.1:9222/json/version`
- 如果返回空或连接拒绝 → Edge 没有调试端口，需要重启 Edge
- 任务栏快捷方式已预配置 `--remote-debugging-port=9222`，用户正常点开即可

### 2. portproxy 规则（需管理员权限）
```powershell
# 查看 WSL 网关 IP
$wslIp = (Get-NetIPAddress -InterfaceAlias "vEthernet (WSL*)" -AddressFamily IPv4).IPAddress
# 通常是 172.18.160.1，但可能变化

# 设置转发
netsh interface portproxy add v4tov4 listenport=9222 listenaddress=$wslIp connectport=9222 connectaddress=127.0.0.1

# 验证
netsh interface portproxy show v4tov4
```

### 3. 防火墙规则（需管理员权限）
```powershell
New-NetFirewallRule -DisplayName "Edge CDP for WSL2" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9222 -Profile Any
```

## OpenClaw 配置

在 `openclaw.json` 中：
```json
{
  "browser": {
    "enabled": true,
    "defaultProfile": "remote",
    "profiles": {
      "remote": {
        "cdpUrl": "http://172.18.160.1:9222",
        "attachOnly": true,
        "color": "#00AA00"
      }
    }
  }
}
```

- `attachOnly: true` — 不启动新浏览器，只附加到已运行的 Edge
- `defaultProfile: "remote"` — 默认使用远程 CDP 配置

## 永久方案（开机自动配置）

脚本位置：`C:\tmp\edge-cdp-setup.ps1`

功能：
1. 自动检测 WSL 网关 IP
2. 设置 portproxy 转发规则
3. 添加防火墙入站规则（仅首次）
4. 如果 Edge 没运行，自动启动带调试端口的 Edge

注册为 Windows 计划任务（管理员 PowerShell）：
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File C:\tmp\edge-cdp-setup.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "Edge CDP for WSL2" -Action $action -Trigger $trigger -RunLevel Highest -Description "Auto-setup Edge CDP portproxy for OpenClaw"
```

## 排障流程（Layered Triage）

遇到浏览器连不上时，按以下顺序逐层排查：

### Layer 1: Edge 是否监听？
```powershell
# 在 Windows PowerShell 执行
curl http://127.0.0.1:9222/json/version
```
- ✅ 返回 JSON（含 Browser、Protocol-Version）→ 进入 Layer 2
- ❌ 连接拒绝 → Edge 没带调试端口。关闭所有 Edge，重新启动带 `--remote-debugging-port=9222`

### Layer 2: portproxy 是否配置？
```powershell
netsh interface portproxy show v4tov4
```
- ✅ 看到 9222 → 进入 Layer 3
- ❌ 空 → 执行 `C:\tmp\edge-cdp-setup.ps1`（管理员权限）

### Layer 3: WSL 能否访问？
```bash
# 在 WSL 中执行
curl -s --connect-timeout 3 http://172.18.160.1:9222/json/version
```
- ✅ 返回 JSON → 浏览器可用
- ❌ 超时/拒绝 → 检查防火墙规则，或 WSL IP 变了（重新执行 setup 脚本）

### Layer 4: OpenClaw browser 工具是否正常？
```
browser(action="status", target="host")
```
- `cdpReady: true` + `running: true` → 完全正常
- `cdpReady: false` → 检查 `openclaw.json` 中 `browser.profiles.remote.cdpUrl` 是否指向正确 IP

## 踩坑记录

### 1. Edge 进程已存在但没有调试端口
**现象**：Windows 有 18+ 个 msedge.exe 进程，但没有一个带 `--remote-debugging-port`
**原因**：Edge 首次启动时没带参数，后续带参数的启动会被合并到已有进程
**解决**：必须先关闭所有 Edge 进程，再带参数启动
**⚠️ 严禁** `taskkill /F /IM msedge.exe` 批量杀，会杀掉用户正在用的标签页。让用户手动关闭 Edge 再重开

### 2. WSL2 NAT 模式下 localhost/127.0.0.1 不互通
**现象**：WSL `curl localhost:9222` 连接拒绝，但 Windows `curl 127.0.0.1:9222` 正常
**原因**：WSL2 NAT 模式下 WSL 和 Windows 的 127.0.0.1 是不同的网络命名空间
**解决**：必须通过 portproxy 桥接，使用 WSL 网关 IP（如 172.18.160.1）

### 3. portproxy 需要管理员权限
**现象**：`netsh interface portproxy add` 报权限不足
**原因**：portproxy 是系统级网络配置，需要管理员
**解决**：以管理员身份运行 PowerShell，或用计划任务自动执行

### 4. portproxy 重启后丢失
**现象**：Windows 重启后 portproxy 规则消失，浏览器连不上
**原因**：portproxy 规则不持久化
**解决**：注册 Windows 计划任务，开机自动执行 `C:\tmp\edge-cdp-setup.ps1`

### 5. WSL 网关 IP 可能变化
**现象**：某次 WSL 重启后 IP 从 172.18.160.1 变成其他地址
**原因**：WSL2 NAT 模式下网关 IP 不固定
**解决**：setup 脚本动态检测 `vEthernet (WSL*)` 接口 IP；如果 IP 变了需要更新 `openclaw.json` 中的 `cdpUrl`

### 6. exec 命令被 Aborted
**现象**：在 OpenClaw 中通过 exec 执行 PowerShell 命令返回 "Aborted"
**原因**：部分 Windows 命令（如 Start-Process、taskkill）在 WSL exec 中受限
**解决**：写成 .ps1 脚本文件，让用户在 Windows 侧手动执行；或通过计划任务自动运行

### 7. DevToolsActivePort 文件路径
**现象**：尝试读取 Edge 的 `DevToolsActivePort` 文件失败
**原因**：WSL 中 `$env:LOCALAPPDATA` 不会展开为 Windows 路径
**解决**：直接硬编码路径 `/mnt/c/Users/<username>/AppData/Local/Microsoft/Edge/User Data/DevToolsActivePort`

### 8. PowerShell 脚本变量编码问题
**现象**：从 WSL 写入的 .ps1 脚本，`$ruleName` 等变量在 PowerShell 中为空，导致 `Get-NetFirewallRule -DisplayName $ruleName` 报错
**原因**：WSL 写入文件时可能引入 BOM 或编码差异，导致 PowerShell 解析变量失败
**解决**：在 .ps1 脚本中用**字符串字面量**替代变量引用。例如直接写 `"Edge CDP for WSL2"` 而非 `$ruleName`

### 9. 计划任务与 Edge 启动顺序
**现象**：开机后计划任务执行了，但浏览器仍连不上
**原因**：用户在计划任务执行前手动打开了 Edge（不带调试端口），计划任务的 Edge 启动被合并到已有进程
**解决**：计划任务中 portproxy + 防火墙不受影响，只需关闭所有 Edge 再重开即可恢复调试端口。或者将 Edge 快捷方式也改为带 `--remote-debugging-port=9222` 参数

### 10. browser.profiles.user.cdpUrl 配错端口
**现象**：`browser(action="status", profile="user")` 报 `Could not find DevToolsActivePort for chrome at /home/park/.config/google-chrome/DevToolsActivePort`
**原因**：`openclaw.json` 中 `browser.profiles.user.cdpUrl` 被配成了 `127.0.0.1:62236`（不存在的端口），browser tool 连接失败后回退去找 google-chrome 的 DevToolsActivePort 文件——但系统装的是 Edge 不是 Chrome
**解决**：把 user profile 的 cdpUrl 改成和 remote profile 一致：`http://172.18.160.1:9222`
**教训**：user 和 remote profile 的 cdpUrl 应该统一指向同一个 Edge CDP endpoint，避免配置不一致

### 11. browser tool 全部 Aborted
**现象**：browser tool 的 status/navigate/snapshot/tabs 等所有操作都返回 "Aborted"
**原因**：可能是某个 tab 进入异常状态（如页面崩溃、JS 卡死），或 Gateway 重启过程中 browser tool 的 CDP 会话断开
**解决**：
1. 先用 `curl http://172.18.160.1:9222/json/version` 确认 CDP 本身是否通
2. 如果 curl 通但 browser tool abort → 重启 Gateway（`openclaw gateway restart`）
3. 如果 curl 也不通 → 回到排障流程 Layer 1
**教训**：browser tool abort 不等于 CDP 断了，可能只是 tool 层面的会话状态问题

### 12. MiniMax 模型用 browser tool 时的格式错误
**现象**：MiniMax-M2.7 模型调用 browser tool 时生成了非标准的 JSON 格式（如 `{"command">powershell.exe ...`），导致工具调用失败
**原因**：MiniMax 模型的 tool calling 格式与标准不完全兼容，尤其在参数中包含 `>` 等特殊字符时
**解决**：browser 自动化任务建议切到高性能模型（如 Claude Opus），MiniMax 不适合复杂的 browser tool 交互
**教训**：不同模型的 tool calling 能力差异大，browser 自动化是对 tool calling 精度要求最高的场景之一

## 安全红线
- ❌ **绝对不碰** WSL 网络模式（mirrored/NAT 切换会导致全网断联）
- ❌ **绝对不碰** VPN、路由表、DNS 配置
- ❌ **禁止** `taskkill /F /IM msedge.exe` 批量杀 Edge 进程
- ✅ 只通过 portproxy + 防火墙规则解决网络可达性
