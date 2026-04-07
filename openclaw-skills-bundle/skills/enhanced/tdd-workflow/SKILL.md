---
name: tdd-workflow
description: "Enforces test-driven development with 80%+ coverage. Use when writing new features, fixing bugs, or refactoring code. RED → GREEN → REFACTOR with git checkpoint discipline."
---

# Test-Driven Development Workflow

Enforces TDD with 80%+ coverage including unit, integration, and E2E tests.

## When to Use

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints
- Creating new components

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements
- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. Test Types

**Unit Tests** — Individual functions, component logic, pure functions, helpers
**Integration Tests** — API endpoints, database operations, service interactions
**E2E Tests** — Critical user flows, complete workflows, browser automation

### 4. Git Checkpoints
- Create a checkpoint commit after each TDD stage
- Do not squash until workflow is complete
- Each commit message must describe the stage and evidence captured
- Only count commits on the current active branch for the current task

## TDD Workflow Steps

### Step 1: Write User Journeys
```
As a [role], I want to [action], so that [benefit]
```

### Step 2: Generate Test Cases
For each user journey, create comprehensive test cases covering happy path + edge cases + error scenarios.

### Step 3: Run Tests — RED Gate (Mandatory)
```bash
npm test  # or project-specific test command
# Tests MUST fail — we haven't implemented yet
```

**RED validation requirements:**
- The test target compiles successfully
- The new/changed test is actually executed
- The result is RED (failure)
- The failure is caused by the intended missing implementation, NOT by syntax errors, broken setup, or unrelated regressions

A test that was only written but not compiled and executed does not count as RED.

**Do not edit production code until RED state is confirmed.**

If under git, commit immediately after RED validation:
- `test: add reproducer for <feature or bug>`

### Step 4: Implement Code
Write **minimal** code to make tests pass. Nothing more.

### Step 5: Run Tests — GREEN Gate (Mandatory)
```bash
npm test  # Same test target
# Tests MUST now pass
```

Rerun the same test target. Confirm the previously failing test is now GREEN.

If under git, commit immediately after GREEN validation:
- `fix: <feature or bug>`

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance
- Enhance readability

If under git, commit after refactor:
- `refactor: clean up after <feature or bug> implementation`

### Step 7: Verify Coverage
```bash
npm run test:coverage
# Verify 80%+ coverage achieved
```

## Testing Patterns

### Unit Test (Jest/Vitest)
```typescript
describe('Component', () => {
  it('renders with correct text', () => { /* ... */ })
  it('calls handler when clicked', () => { /* ... */ })
  it('is disabled when disabled prop is true', () => { /* ... */ })
})
```

### API Integration Test
```typescript
describe('GET /api/endpoint', () => {
  it('returns data successfully', async () => { /* ... */ })
  it('validates query parameters', async () => { /* ... */ })
  it('handles database errors gracefully', async () => { /* ... */ })
})
```

### E2E Test (Playwright)
```typescript
test('user can complete workflow', async ({ page }) => {
  await page.goto('/')
  // Navigate, interact, assert
})
```

## Test File Organization
```
src/
├── components/
│   └── Button/
│       ├── Button.tsx
│       └── Button.test.tsx          # Unit tests
├── app/api/
│   └── endpoint/
│       ├── route.ts
│       └── route.test.ts            # Integration tests
└── e2e/
    └── workflow.spec.ts             # E2E tests
```

## Common Mistakes to Avoid

- ❌ Testing implementation details → ✅ Test user-visible behavior
- ❌ Brittle selectors (`.css-class-xyz`) → ✅ Semantic selectors (`button:has-text("Submit")`)
- ❌ Tests depend on each other → ✅ Independent tests with own setup
- ❌ Skipping RED gate → ✅ Always verify failure before implementation

## Best Practices

1. **Write Tests First** — Always TDD
2. **One Assert Per Test** — Focus on single behavior
3. **Descriptive Test Names** — Explain what's tested
4. **Arrange-Act-Assert** — Clear test structure
5. **Mock External Dependencies** — Isolate unit tests
6. **Test Edge Cases** — Null, undefined, empty, large
7. **Test Error Paths** — Not just happy paths
8. **Keep Tests Fast** — Unit tests < 50ms each
9. **Clean Up After Tests** — No side effects
10. **Review Coverage Reports** — Identify gaps

## Success Metrics

- 80%+ code coverage achieved
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution (< 30s for unit tests)
- E2E tests cover critical user flows

## Boundary Value Bombing (from Claude Code test suite)

穷举式边界值测试策略，确保每个输入参数在极端情况下都有测试覆盖。

### 每个输入参数至少测试 5 个边界

```
参数类型 → 5 个边界测试用例

String:
  1. null / undefined（语言相关）
  2. empty string ""
  3. whitespace only " ", "\\t\\n"
  4. 正常值（非空有内容）
  5. 超长字符串 >1MB

Number:
  1. null / undefined
  2. 0 和 -1（边界穿越）
  3. 最大安全整数 MAX_SAFE_INTEGER（9007199254740991）
  4. NaN 和 Infinity
  5. 负数（包括 -0）

Path/String（文件系统）:
  1. null / undefined
  2. empty string
  3. 正常路径
  4. 259 字符（Windows MAX_PATH，不含终止符）
  5. 260+ 字符（Windows 长路径，需要 \\\\?\\ 前缀）

Unicode 边界（通用文本输入）:
  1. U+0000（NUL，字符串终止符）
  2. U+FFFF（不属于任何字符的代码点）
  3. 代理对 U+D800-U+DFFF（必须成对）
  4. 组合字符 U+0300-U+036F（叠加于前一个字符）
  5. 混合脚本：中文 + Arabic + Emoji + Control Characters

Boolean:
  1. true
  2. false
  3. null / undefined
  4. 1 / 0（来自某些语言的类型混淆）
  5. "true" / "false"（字符串形式）

Array/Collection:
  1. null / undefined
  2. empty array []
  3. single element [x]
  4. duplicate elements [x, x]
  5. 极大数组（10000+ 元素，测试分页/流式处理）

Date/Time:
  1. Unix epoch (1970-01-01T00:00:00Z)
  2. Far future (2099-12-31T23:59:59Z)
  3. Timezone edge cases (UTC±12, UTC+8)
  4. Leap second (23:59:60)
  5. Epoch overflow (64-bit timestamp max: 2262-04-11)
```

### Round 编号制（大规模测试组织）

当测试用例数量超过 20 个时，使用 ROUND 编号制避免混乱：

```
命名规范：ROUND-XXX-<description>
  ROUND-001-auth-null-input
  ROUND-002-auth-empty-string
  ROUND-003-auth-whitespace
  ROUND-004-auth-max-length
  ROUND-005-path-win-max-path
  ROUND-006-unicode-bmp-edge
  ROUND-007-unicode-surrogate-pair
  ROUND-008-unicode-combining
  ...

回归网（Regression Grid）：
  每完成一个 ROUND，记录通过/失败状态
  后续任何修改后，重跑对应 ROUND 区间
  
  ROUND-001 ~ ROUND-010   →  基础边界
  ROUND-011 ~ ROUND-020   →  类型混淆
  ROUND-021 ~ ROUND-030   →  Unicode 专项
  ROUND-031 ~ ROUND-040   →  路径/平台专项

工具辅助：
  # 自动生成 ROUND 测试用例骨架
  for i in $(seq -f "%03g" 1 50); do
    echo "ROUND-${i}-: test case" >> test_rounds.sh
  done
```

### 边界测试的自动化策略

```typescript
// 参数化边界测试示例（使用 Jest parameterized）
const boundaryCases = [
  { value: null,         label: 'null' },
  { value: undefined,   label: 'undefined' },
  { value: '',          label: 'empty string' },
  { value: ' ',         label: 'whitespace only' },
  { value: 'x'.repeat(1_000_000), label: '1MB string' },
]

test.each(boundaryCases)('handles $label', ({ value }) => {
  expect(validateInput(value)).toBeDefined()
})
```

---
Origin: Adapted from Everything Claude Code (ECC) tdd-workflow skill.

### 新增：边界值轰炸策略

TDD中边界值测试设计：
- 空值：null, undefined, "", []
- 极值：超长字符串(10000+字符)、超大数字(2^53)、负数、零
- 特殊字符：!@#$%^&*()_+-=[]{}|;':",./<>?
- 路径边界：/, /tmp, /home, ~/.ssh, /mnt/c
- 类型边界：string vs number vs boolean vs object

### 新增：Round编号制

Bug修复测试命名：
```
test-round-001-20260407-handler-field.js
test-round-002-20260407-esm-double-default.js
test-round-003-20260407-sed-self-reference.js
```

每个修复对应一个测试：
1. 写失败的测试（复现bug）
2. 修复代码使测试通过
3. 回归测试确保不破坏其他Round

### 新增：跨平台测试

- Windows路径：/mnt/c/Users/w/Desktop
- WSL路径：/home/park/.openclaw/workspace
- 混合路径：Windows进程调用WSL命令
- 行尾符：CRLF vs LF差异处理
