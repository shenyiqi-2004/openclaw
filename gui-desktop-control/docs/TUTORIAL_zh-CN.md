# 教程：把 WSL / OpenClaw 接到 Windows GUI

## 1. 方案总览

这套方案分两层：

### A. 鼠标层（socket bridge）
- `windows/mouse_bridge.py`
- `wsl/mouse_client.py`
- `wsl/mouse-socket.sh`

用途：
- 鼠标移动
- 鼠标点击
- 获取当前位置

优点：
- 比临时生成 `.ps1` 再执行更稳
- 往返链路短
- 适合频繁小动作

### B. PowerShell 工具层 + 键盘适配层
- `windows/input-sim.ps1`
- `windows/app-control.ps1`
- `windows/screen-info.ps1`
- `windows/drag.ps1`

用途：
- 输入文本
- 快捷键
- 中英文输入切换适配（IME heuristic）
- 窗口管理
- 截图
- 拖拽

---

## 2. 为什么要拆成两层

因为在 WSL → Windows GUI 这个场景里，不同动作稳定性不一样：

- 鼠标 move/click：socket server 最稳
- 键盘输入：PowerShell + `SendKeys` 足够直接
- 截图：PowerShell 调 .NET / GDI 很方便
- 窗口管理：PowerShell 调 Win32 API 最省事

所以最终不是“全都一个技术做”，而是“每种动作用最稳的那种方式”。

---

## 3. 环境要求

- Windows + WSL2
- Windows 安装 Python
- WSL 里有 `python3`
- WSL 能调用：
  - `/mnt/c/Windows/System32/cmd.exe`
  - `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`

---

## 4. 启动步骤

### Windows 端
```bat
cd /d <仓库路径>\windows
py -3 mouse_bridge.py
```

或者直接双击：
- `run_mouse_bridge.bat`

启动后会监听：
- `0.0.0.0:44555`

### WSL 端
先测连通：
```bash
cd gui-desktop-control
./tests/test_socket_ping.sh
```

如果成功，会返回 `pong` 和当前鼠标坐标。

---

## 5. 常见操作

### 鼠标移动
```bash
./wsl/mouse-socket.sh move 1000 600
```

### 鼠标点击
```bash
./wsl/mouse-socket.sh click 1000 600
```

### 输入文本
```bash
./wsl/dc-type-text.sh "hello from wsl"
```

### 自动处理中英文输入（键盘适配）
```bash
./wsl/dc-type-text-auto-ime.sh "你好，world"
```

### 发送快捷键
```bash
./wsl/dc-send-keys.sh "Ctrl+S"
./wsl/dc-send-keys.sh "Alt+Tab"
./wsl/dc-send-keys.sh "Enter"
```

### 列出窗口
```bash
./wsl/dc-list-windows.sh
```

### 聚焦窗口
```bash
./wsl/dc-focus-window.sh "Notepad"
```

### 截图
全屏：
```bash
./wsl/dc-screenshot.sh
```

指定窗口：
```bash
./wsl/dc-screenshot.sh "Notepad"
```

### 拖拽
```bash
./wsl/dc-mouse-drag.sh 200 300 800 300
```

---

## 6. 测试文件说明

### `tests/test_powershell_help.sh`
检查 PowerShell 脚本能否正常加载。

### `tests/test_socket_ping.sh`
检查 WSL → Windows socket 桥是否可连接。

### `tests/test_smoke.sh`
跑一轮最小冒烟测试。

---

## 7. GitHub 发布建议

建议仓库描述：

> Windows desktop GUI control toolkit for WSL/OpenClaw: mouse socket bridge + PowerShell input/screenshot/window management.

建议 README 里强调：
- 本地优先
- 不依赖云端
- 专门解决 WSL 控 Windows GUI 的桥接问题

---

## 8. 已知坑

### 1）服务必须跑在桌面会话里
如果你把 `mouse_bridge.py` 跑成 service / 计划任务 / Session 0，鼠标大概率不受控。

### 2）IME 切换不一定通用
不同输入法对切换热键处理不同，`dc-type-text-auto-ime.sh` 只是实用方案，不是绝对标准方案。

### 3）目标窗口必须真的可交互
有些管理员权限窗口、UAC 弹窗、锁屏界面，这套方案未必能稳定控制。

---

## 9. 后续可扩展方向

- 给 socket server 加 `right_click / double_click / drag / scroll`
- 加 OCR / UIA / 图像匹配
- 给截图结果加元素定位
- 做成 Python package 或更完整 CLI
