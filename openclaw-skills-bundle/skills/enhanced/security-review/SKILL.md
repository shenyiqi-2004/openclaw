---
name: security-review
description: "Comprehensive security checklist for authentication, user input, secrets, API endpoints, and sensitive features. Use when handling auth, user input, secrets, or payment flows."
---

# Security Review

Ensures all code follows security best practices and identifies potential vulnerabilities.

## When to Use

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating new API endpoints
- Working with secrets or credentials
- Implementing payment features
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Security Checklist

### 1. Secrets Management
- ❌ Never hardcode API keys, tokens, or passwords
- ✅ All secrets in environment variables
- ✅ `.env.local` in .gitignore
- ✅ No secrets in git history
- ✅ Production secrets in hosting platform

### 2. Input Validation
- ✅ All user inputs validated with schemas (zod, joi, etc.)
- ✅ File uploads restricted (size, type, extension)
- ✅ No direct use of user input in queries
- ✅ Whitelist validation (not blacklist)
- ✅ Error messages don't leak sensitive info

### 3. SQL Injection Prevention
- ❌ Never concatenate SQL: `SELECT * FROM users WHERE email = '${input}'`
- ✅ Always use parameterized queries or ORM

### 4. Authentication & Authorization
- ✅ Tokens in httpOnly cookies (not localStorage — vulnerable to XSS)
- ✅ Authorization checks before sensitive operations
- ✅ Row Level Security enabled (Supabase/Postgres)
- ✅ Role-based access control implemented
- ✅ Session management secure

### 5. XSS Prevention
- ✅ User-provided HTML sanitized (DOMPurify)
- ✅ CSP headers configured
- ✅ No unvalidated dynamic content rendering

### 6. CSRF Protection
- ✅ CSRF tokens on state-changing operations
- ✅ SameSite=Strict on all cookies

### 7. Rate Limiting
- ✅ Rate limiting on all API endpoints
- ✅ Stricter limits on expensive operations (search, AI calls)
- ✅ IP-based + user-based rate limiting

### 8. Sensitive Data Exposure
- ❌ Never log passwords, tokens, card numbers
- ✅ Generic error messages for users
- ✅ Detailed errors only in server logs
- ✅ No stack traces exposed to users

### 9. Dependency Security
```bash
npm audit              # Check vulnerabilities
npm audit fix          # Auto-fix
npm ci                 # Reproducible builds in CI
```
- ✅ Lock files committed
- ✅ Dependabot/Renovate enabled

## Pre-Deployment Security Checklist

Before ANY production deployment, verify ALL:

- [ ] **Secrets**: No hardcoded secrets, all in env vars
- [ ] **Input Validation**: All user inputs validated
- [ ] **SQL Injection**: All queries parameterized
- [ ] **XSS**: User content sanitized
- [ ] **CSRF**: Protection enabled
- [ ] **Authentication**: Proper token handling
- [ ] **Authorization**: Role checks in place
- [ ] **Rate Limiting**: Enabled on all endpoints
- [ ] **HTTPS**: Enforced in production
- [ ] **Security Headers**: CSP, X-Frame-Options configured
- [ ] **Error Handling**: No sensitive data in errors
- [ ] **Logging**: No sensitive data logged
- [ ] **Dependencies**: Up to date, no vulnerabilities
- [ ] **CORS**: Properly configured
- [ ] **File Uploads**: Validated (size, type)

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Academy](https://portswigger.net/web-security)

## Command Injection Security (from Claude Code BashTool)

23 层命令注入验证清单的精简版，聚焦最常见的攻击向量。

### Top 10 最常见攻击向量检测

| 攻击向量 | 检测模式 | 风险级别 |
|----------|----------|----------|
| 管道注入 | `; cmd`, `&& cmd`, `\| cmd`, `\n cmd` | 🔴 CRITICAL |
| 命令替换 | `$(cmd)`, `` `cmd` `` | 🔴 CRITICAL |
| 路径遍历 | `../`, `..\\`, `..%2f` | 🔴 CRITICAL |
| 环境变量展开 | `$VAR`, `${VAR}` | 🟠 HIGH |
| 引号逃逸 | `'cmd'`, `"cmd"` | 🟠 HIGH |
| 选项注入 | `--`, `-z`, `-e` | 🟠 HIGH |
| 文件描述符 | `/dev/tcp`, `/dev/null` | 🟡 MEDIUM |
| Glob 注入 | `*`, `?`, `[a-z]` | 🟡 MEDIUM |
| 历史展开 | `!n`, `!!`, `!$` | 🟡 MEDIUM |
| Tilde 展开 | `~user/path`, `~/path` | 🟢 LOW |

### NTFS ADS（Alternate Data Streams）检测

Windows NTFS 支持 ADS，攻击者可隐藏数据：
```bash
# 检测 ADS（Windows）
dir /r                          # 显示所有流的文件
streams <file>                  # 使用 streams.exe
# 检测特征：file.txt:hidden_stream:$DATA
```
防御：避免动态构造文件路径，使用白名单文件扩展名检查。

### 8.3 短文件名（SFN）攻击

Windows 为兼容旧系统生成 8.3 短文件名：
```
C:\Program Files\ → C:\PROGRA~1\
C:\Program Files (x86)\ → C:\PROGRA~2\
C:\Document and Settings\ → C:\DOCUME~1\
```
攻击场景：长路径被禁止但短路径可能绕过。检测/防御：
```bash
# 检测当前目录是否有 8.3 别名冲突
fsutil file queryshortname . 2>nul
```
最佳实践：避免依赖路径存在性判断，改用文件内容/属性验证。

### Windows 特殊设备名

保留设备名在任何情况下都不会是合法文件：
```
CON   — 控制台（键盘/屏幕）
PRN   — 打印机
AUX   — 辅助设备
NUL   — 空设备
COM1-9 — 串行端口
LPT1-9 — 并行端口
```
攻击示例：`type NUL` 会清空文件（Unix: `> file` 等效）。
防御：在处理用户提供的路径前，强制检查是否为保留设备名：
```python
RESERVED = {'CON','PRN','AUX','NUL','NUL0','COM1','LPT1'}
# 路径最后一段转大写后检查是否在 RESERVED 中
import re
if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$', path.upper().split('\\')[-1]):
    raise ValueError("Reserved device name")
```

### 编码混淆检测

#### UTF-7 注入
攻击者可在邮件/文件头中注入 UTF-7 编码的恶意内容：
```
+ADw-script+AD4-alert(+ACI-test+ACI-)+ADsAPA-/script+AD4AAc-
# 解码: <script>alert("test");</script>
```
防御：明确指定 UTF-8 编码，禁止自动检测。

#### Overlong UTF-8 编码
非规范的长序列可绕过过滤器：
```
# 经典 overlong: `/` 可编码为
# 2-byte:    11000010 10101111 → C2 AF
# 3-byte:    11100000 10000000 10101111 → E0 80 AF
# 4-byte:    11110000 10000000 10000000 10101111 → F0 80 80 AF
```
防御：严格拒绝不合法的 UTF-8 序列（Python: `errors='strict'`）。

#### BOM 注入
UTF-8 BOM (`\xEF\xBB\xBF`) 可用于改变文件解释：
```bash
# 检测 BOM
grep -rl $'\\xEF\\xBB\\xBF' .   # UTF-8 BOM
grep -rl $'\\xFF\\xFE' .       # UTF-16 LE BOM
grep -rl $'\\xFE\\xFF' .       # UTF-16 BE BOM
```
防御：处理文件时跳过/剥离 BOM，明确验证文件魔数。

---
Origin: Adapted from Everything Claude Code (ECC) security-review skill.

## 新增：命令注入23层验证清单

补充free-code BashTool的23层验证链：

| 层 | 检测项 | 危险模式 |
|----|--------|----------|
| 1 | 命令分隔符 | `;` `|` `&` `&&` `||` `$()` `` ` `` |
| 2 | 路径遍历 | `../` `../../` `/etc` |
| 3 | 环境变量注入 | `${}` `$()` `` ` `` |
| 4 | globbing通配符 | `*` `?` `[` |
| 5 | 编码绕过 | `\x` hex `\u` unicode `\n` `\r` |
| 6 | 符号链接追踪 | `readlink -f` |
| 7 | 敏感文件访问 | `/etc/passwd` `~/.ssh/` `/root/` |
| 8 | NTFS ADS | `stream:$DATA` |
| 9 | 8.3短文件名 | `PROGRA~1` `DOCUME~1` |
| 10 | chmod危险权限 | `777` `4755` `u+s` `g+s` |
| 11 | dd磁盘写入 | `if=` `of=` |
| 12 | 磁盘操作 | `mkfs` `fdisk` `dd` |
| 13 | 进程注入 | `/proc/self/` |
| 14 | 网络导出 | `curl` `wget` `nc` `telnet` |
| 15 | 任务控制符号 | `;` `&` `|` `
` |
| 16 | 后台重定向 | `> /dev/null 2>&1` `
` |
| 17 | 管道链分析 | 逐层展开 `|` 连接的命令 |
| 18 | 命令别名展开 | `alias` `\command` |
| 19 | 历史扩展 | `!` `$HISTFILE` `$HISTCONTROL` |
| 20 | TTY检测 | `/dev/tty` |
| 21 | sed -i路径验证 | sed -i 写入路径审查 |
| 22 | find -exec | `-exec {} \;` `-exec {} +` |
| 23 | 命令行边界值 | 空字符串 超长参数 零除 |

### 新增：权限审查流程

**每次exec前**：运行 `exec_security_check`，根据返回 verdict 执行或拒绝。

**高危命令判定**：满足以下任意一项即触发权限审查流程：
- 涉及文件写入（`>` `>>` `-o` `mv` `cp` `rm` `chmod` `chown`）
- 涉及网络操作（`curl` `wget` `nc` `ssh` `scp`）
- 涉及系统配置（`chmod` `chown` `sudo` `su` `passwd`）
- 涉及敏感路径（`/etc/` `/root/` `~/.ssh/` `/proc/`）
- 涉及磁盘操作（`dd` `mkfs` `fdisk` `mount`）

**审查要素**：
1. **路径解析**：所有相对路径展开为绝对路径，验证最终路径在预期目录内
2. **参数验证**：命令参数逐项白名单检查，禁止动态构造路径
3. **文件描述符**：确认无 `/dev/tcp` `/dev/null` 被重定向到敏感资源
4. **进程树影响**：评估对父进程、子进程及系统状态的影响范围

**审查通过标准**：23层检测无🔴 CRITICAL，且无未解析的动态内容。
