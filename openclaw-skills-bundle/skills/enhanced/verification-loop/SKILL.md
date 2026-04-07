---
name: verification-loop
description: "Full-chain verification: build → type-check → lint → test → security scan → diff review. Use after completing a feature, before PR, or after refactoring."
---

# Verification Loop

Comprehensive quality gate system. Run after every significant code change.

## When to Use

- After completing a feature or significant code change
- Before creating a PR
- When you want to ensure quality gates pass
- After refactoring

## Verification Phases

### Phase 1: Build Verification
```bash
# Detect and run build
npm run build 2>&1 | tail -20
# OR: pnpm build / cargo build / go build ./... / python -m py_compile
```
If build fails → **STOP and fix before continuing.**

### Phase 2: Type Check
```bash
# TypeScript
npx tsc --noEmit 2>&1 | head -30

# Python
pyright . 2>&1 | head -30
# OR: mypy . 2>&1 | head -30
```
Report all type errors. Fix critical ones before continuing.

### Phase 3: Lint Check
```bash
# JS/TS
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30

# Go
golangci-lint run 2>&1 | head -30
```

### Phase 4: Test Suite
```bash
npm run test -- --coverage 2>&1 | tail -50
```
Report: Total tests / Passed / Failed / Coverage %
Target: **80% minimum coverage.**

### Phase 5: Security Scan
```bash
# Hardcoded secrets
grep -rn "sk-\|api_key\|password\s*=" --include="*.ts" --include="*.js" --include="*.py" . 2>/dev/null | head -10

# Debug leftovers
grep -rn "console.log\|print(" --include="*.ts" --include="*.tsx" --include="*.py" src/ 2>/dev/null | head -10
```

### Phase 6: Diff Review
```bash
git diff --stat
git diff HEAD~1 --name-only
```
Review each changed file for:
- Unintended changes
- Missing error handling
- Potential edge cases

## Output Format

```
VERIFICATION REPORT
==================

Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY/NOT READY] for PR

Issues to Fix:
1. ...
2. ...
```

## Integration with Workflow

- **After every coding task** → run verification before reporting completion
- **Before PR creation** → full 6-phase verification mandatory
- **After refactoring** → at minimum Phase 1 + Phase 4

## Advanced Verification (from Claude Code)

在基础 6-phase 验证之上，增加 Prompt Cache Break 检测、依赖变更检测和安全扫描增强。

### Prompt Cache Break 检测

修改了 system prompt、SKILL.md 或 AGENTS.md 后的额外验证：

#### 1. Cache 命中状态检查
```bash
# 在 skill 修改后执行以下检查：
# 1. 观察首次调用该 skill 的 token 增量
#    - 正常 cache hit: <500 tokens
#    - cache break (重新加载): >2000 tokens
# 2. 检查 skill 行为是否异常（指令不生效）
# 3. 如发现 break，手动触发一次完整 skill 执行重建 cache
```

#### 2. 大量 Tool Output 侵占检测
```
信号：工具输出日志极长（>5000 tokens），但最终回复很短
原因：大量工具输出挤占了 context 中的 cache 保留区
处理：
  1. 分析工具输出是否可裁剪（保留关键行）
  2. 在工具调用前加更精确的 limit/filter 参数
  3. 输出仍然过长时，使用 context-budget skill 压缩
```

### 依赖变更检测（自动推断需要的额外步骤）

运行 `git diff --staged` 或 `git diff HEAD` 后，根据变更类型自动推断：

| 变更类型 | 检测模式 | 自动推断的额外步骤 |
|----------|----------|---------------------|
| `package.json` | 新增/升级/删除了依赖 | `npm install` 或 `pnpm install` |
| `package-lock.json` / `yarn.lock` | lock 文件变化 | `npm ci`（保证可复现） |
| `.env`, `.env.local`, `.env.production` | 环境变量文件变更 | 重启应用进程（config 缓存） |
| `tsconfig.json`, `next.config.js` | 构建配置变更 | 重启 dev server / rebuild |
| `prisma/schema.prisma` | 数据库迁移文件 | `prisma migrate dev` 或 `prisma db push` |
| `alembic.ini` | Python DB migration | `alembic upgrade head` |
| Dockerfile / docker-compose.yml | 容器配置变更 | `docker compose build` / restart |
| `.eslintrc`, `.prettierrc` | 代码格式配置变更 | 格式化全量代码后重跑 lint |

**自动验证流程：**
```bash
# 检测依赖变更并提示
if git diff --name-only | grep -qE '^(package\.json|yarn\.lock|package-lock\.json)$'; then
  echo "⚠️ 依赖文件变更检测到，请运行: npm install"
fi
if git diff --name-only | grep -qE '^prisma/'; then
  echo "⚠️ Prisma schema 变更，请运行: prisma migrate dev"
fi
if git diff --name-only | grep -qE '^\.env'; then
  echo "⚠️ .env 文件变更，请重启应用"
fi
```

### 安全扫描增强

在 Phase 5 Security Scan 基础上增加自动化扫描：

#### npm / pip 依赖漏洞扫描
```bash
# Node.js
npm audit 2>&1 | grep -E 'HIGH|CRITICAL' | head -20
npm audit --audit-level=high  # 失败级别设定

# Python
pip audit 2>&1 | head -30
safety check 2>&1 | head -30  # 使用 safety 工具
```

#### 硬编码密钥检测（正则扫描）
```bash
# AWS Access Key（常见格式）
grep -rnE 'AKIA[0-9A-Z]{16}' --include="*.ts" --include="*.js" --include="*.py" . 2>/dev/null

# OpenAI / 其他 API Keys
grep -rnE 'sk-[a-zA-Z0-9]{48}' --include="*.ts" --include="*.js" --include="*.py" . 2>/dev/null

# Private Key 文件特征
grep -rnE '-----BEGIN (RSA |EC |DSA |OPENSSH )PRIVATE KEY-----' --include="*.pem" --include="*.key" . 2>/dev/null

# 通用 Secret 模式（误报率较高，仅提示）
grep -rnE '(password|secret|token)\s*[=:]]\s*["\'][^"\'\\s]{8,}' --include="*.ts" --include="*.py" . 2>/dev/null | grep -v node_modules | head -20
```

#### .env 文件-gitignore 检查
```bash
# 检查 .env 是否在 .gitignore 中
if [ -f .env ] && ! grep -qE '^\.env$' .gitignore 2>/dev/null; then
  echo "🔴 CRITICAL: .env 文件未在 .gitignore 中！"
fi

# 检查是否有 .env.example 或 .env.template（最佳实践）
if [ ! -f .env.example ] && [ ! -f .env.template ]; then
  echo "🟡 WARNING: 建议创建 .env.example 记录环境变量模板"
fi
```

#### 自动化安全报告模板
```
ADVANCED SECURITY SCAN REPORT
=============================

[1] Dependency Audit:
    Status: PASS/FAIL
    High/Critical Issues: N

[2] Hardcoded Secrets:
    Status: PASS/FAIL
    Matches Found: N
    Locations: [list files]

[3] .gitignore Compliance:
    .env in gitignore: YES/NO
    .env.example exists: YES/NO

[4] Dependency Changes Detected:
    [list changed files → required actions]

Overall: [PASS/FAIL]
```

---
Origin: Adapted from Everything Claude Code (ECC) verification-loop skill.
