# Test Strategies for OpenClaw Plugins

**描述**: 边界值轰炸 + Round编号制 + 跨平台测试策略

---

## 1. 边界值轰炸法

### 1.1 基础边界值

| 类型 | 测试值 |
|------|--------|
| 空值 | `null`, `undefined`, `""`, `''` |
| 极长字符串 | `"a".repeat(100000)`, `"π".repeat(50000)` |
| 超大数字 | `Number.MAX_SAFE_INTEGER`, `1e308`, `-1e308` |
| 负数 | `-1`, `-999999`, `-Number.MIN_VALUE` |
| 特殊字符 | `!@#$%^&*()_+-=[]{}|;':",./<>?` |

### 1.2 路径边界值

| 路径类型 | 测试路径 |
|----------|----------|
| 根目录 | `/`, `C:\`, `\` |
| 系统目录 | `/tmp`, `/home`, `/mnt/c`, `~/.ssh` |
| 跨平台 | `/mnt/c/Users/w/Desktop`, `\\wsl$\Ubuntu\home` |
| 特殊路径 | `/proc/self`, `/sys/kernel`, `NUL`, `COM1` |

### 1.3 Token边界值

| 边界 | 测试值 |
|------|--------|
| 最小 | `0`, `1` |
| 常规 | `128`, `256`, `512`, `1024`, `2048` |
| 大值 | `10000`, `100000`, `999999` |
| 超限 | token长度超过API限制的字符串 |

---

## 2. Round编号制测试命名

### 2.1 命名规则

```
test-round-{number}-{description}.js
```

### 2.2 示例

```
test-round-001-null-handling.js        # Round 1: 空值处理
test-round-002-path-traversal.js      # Round 2: 路径遍历修复
test-round-003-token-overflow.js      # Round 3: Token溢出修复
test-round-004-regression-auth.js     # Round 4: 认证回归测试
```

### 2.3 规则

- 每个bug修复对应一个测试用例
- 回归测试以 `regression-` 前缀标识
- 测试按Round编号顺序执行

---

## 3. 跨平台测试矩阵

### 3.1 平台路径差异

| 平台 | 路径格式 | 示例 |
|------|----------|------|
| Windows WSL | `/mnt/c/...` | `/mnt/c/Users/w/Desktop` |
| Linux WSL原生 | `/home/...` | `/home/park/.openclaw` |
| Windows原声 | `C:\...` | `C:\Users\w\Desktop` |
| 跨系统共享 | 相对路径 | `./shared/` |

### 3.2 环境变量差异

| 差异点 | Windows | Unix/Linux |
|--------|---------|------------|
| 行尾符 | CRLF (`\r\n`) | LF (`\n`) |
| 路径分隔符 | `;` | `:` |
| 环境变量引用 | `%VAR%` | `$VAR` |
| 默认shell | `cmd.exe` / `powershell` | `bash` / `zsh` |

### 3.3 测试命令

```bash
# 检测行尾符
file test-file.txt
od -c test-file.txt | head -5

# 跨平台路径转换
node -e "console.log('/mnt/c/Users'.replace('/mnt/c','C:\\\\'))"

# WSL路径验证
ls -la /mnt/c/Users/w/Desktop 2>/dev/null && echo "WSL path accessible"
```

---

## 4. 工具测试策略

### 4.1 成功路径测试

```javascript
// 测试工具正常调用
async function testToolSuccess() {
  const result = await tool({ param: 'valid-value' });
  assert(result.status === 'success');
  assert(result.data !== null);
}
```

### 4.2 错误路径测试

```javascript
// 无效参数
async function testInvalidParam() {
  await assert.rejects(tool({ param: null }), /null not allowed/);
  await assert.rejects(tool({ param: undefined }), /undefined not allowed/);
  await assert.rejects(tool({ param: '' }), /empty string not allowed/);
}

// 权限拒绝
async function testPermissionDenied() {
  await assert.rejects(tool({ path: '/root/protected' }), /permission denied/i);
}

// 超时不响应
async function testTimeout() {
  await assert.rejects(
    tool({ param: 'slow-value', timeout: 1 }),
    /timeout/i
  );
}
```

### 4.3 并发测试

```javascript
// 多个工具同时调用
async function testConcurrency() {
  const promises = Array.from({ length: 10 }, (_, i) =>
    tool({ param: `value-${i}` })
  );
  const results = await Promise.allSettled(promises);
  
  const successes = results.filter(r => r.status === 'fulfilled');
  const failures = results.filter(r => r.status === 'rejected');
  
  console.log(`Success: ${successes.length}, Failures: ${failures.length}`);
}
```

---

## 5. 自动化测试命令

### 5.1 运行所有测试

```bash
# Node.js 测试
node --test test-round-*.js

# Jest 测试
jest --testPathPattern="test-round"

# Mocha 测试
mocha "test-round-*.js" --reporter spec
```

### 5.2 运行特定Round

```bash
# 运行 Round 1-3
node --test test-round-[123]-*.js

# 运行回归测试
node --test regression-*.js
```

### 5.3 跨平台测试

```bash
# 在WSL中测试Windows路径
node --test --experimental-test-coverage test-round-*.js

# 带环境变量模拟
NODE_OPTIONS="--enable-source-maps" node --test test-round-*.js
```

### 5.4 完整CI命令

```bash
# 边界值轰炸 + Round制 + 跨平台
npm test 2>&1 | tee test-report.txt

# 并发测试专用
node --test test-concurrency-*.js

# 覆盖率报告
node --test --experimental-test-coverage --test-coverage-threshold=80
```

---

## 6. 测试清单

- [ ] 边界值: 空值、极长字符串、超大数字、负数、特殊字符
- [ ] 路径边界: 根目录、系统目录、跨平台路径
- [ ] Token边界: 0/1/1024/2048/100000
- [ ] Round编号: 每个bug一个测试文件
- [ ] 回归测试: 确保不破坏已有功能
- [ ] Windows WSL路径: `/mnt/c` 格式
- [ ] Linux WSL原生路径
- [ ] CRLF vs LF 行尾符检测
- [ ] 成功路径测试
- [ ] 错误路径测试 (无效参数/权限/超时)
- [ ] 并发测试 (10+ 同时调用)
