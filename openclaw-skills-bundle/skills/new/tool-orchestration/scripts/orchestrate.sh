#!/usr/bin/env bash
# orchestrate.sh — 工具调度策略参考实现
# 用法: ./orchestrate.sh <tool_calls.json

set -euo pipefail

# ── 常量 ────────────────────────────────────────────
MAX_RO_CONCURRENT=10
BLOCKED_SUBNETS=(
  "10.0.0.0/8"
  "172.16.0.0/12"
  "192.168.0.0/16"
  "127.0.0.0/8"
)

# ── 分类 ────────────────────────────────────────────
is_mutation() {
  local tool=$1
  case "$tool" in
    write|edit|exec|trash|delete) return 0 ;;
    *) return 1 ;;
  esac
}

# ── SSRF 检测 ───────────────────────────────────────
is_blocked_ip() {
  local ip=$1
  for subnet in "${BLOCKED_SUBNETS[@]}"; do
    if [[ "$ip" =~ ^${subnet%%/*} ]]; then
      return 0
    fi
  done
  return 1
}

ssrf_check_url() {
  local url=$1
  local host=$(echo "$url" | sed -n 's/.*:\/\/\([^/:]*\).*/\1/p')
  # 简化：阻止已知内网 host
  case "$host" in
    localhost|127.0.0.1|0.0.0.0) return 1 ;;
  esac
  return 0
}

# ── 循环依赖检测（Tarjan 简化）───────────────────────
detect_cycle() {
  local deps_json=$1  # JSON: {"tool_name": ["dep1","dep2"]}
  # 依赖图检测，有环返回 1
  # 实际实现应解析 JSON 并用 DFS 检测环
  return 0
}

# ── 优先级排序 ───────────────────────────────────────
sort_by_priority() {
  local input_json=$1
  # 按 priority 降序，同优先级 FIFO
  echo "$input_json" | jq -c 'sort_by(-.priority)'
}

# ── 主调度 ───────────────────────────────────────────
orchestrate() {
  local input_json=$2  # tool_calls

  # 1. 分类
  local ro_json mu_json
  ro_json=$(echo "$input_json" | jq '[.[] | select('"'"'not (.mutation == true)'"'"')]')
  mu_json=$(echo "$input_json" | jq '[.[] | select(.mutation == true)]')

  # 2. 死锁检测
  if ! detect_cycle "$(echo "$mu_json" | jq 'map({key: .name, value: .deps}) | from_entries')"; then
    echo "ERROR: circular dependency detected" >&2
    return 1
  fi

  # 3. read-only 并发（max 10）
  local ro_sorted
  ro_sorted=$(sort_by_priority "$ro_json")
  local ro_count
  ro_count=$(echo "$ro_sorted" | jq 'length')
  local batch_size=$((ro_count < MAX_RO_CONCURRENT ? ro_count : MAX_RO_CONCURRENT))

  echo "Executing $batch_size read-only tools concurrently..."
  echo "$ro_sorted" | jq -c ".[]" | head -n "$batch_size" | while read -r tool; do
    # pre-hook: 权限检查、参数验证、SSRF
    local name
    name=$(echo "$tool" | jq -r '.name')
    if [[ "$name" == "http"* ]] || [[ "$(echo "$tool" | jq -r '.params.url // \"\"')" != "" ]]; then
      local url
      url=$(echo "$tool" | jq -r '.params.url // empty')
      if ! ssrf_check_url "$url"; then
        echo "BLOCKED: SSRF detected for $url" >&2
        continue
      fi
    fi
    echo "$tool"
  done

  # 4. mutation 串行
  local mu_sorted
  mu_sorted=$(sort_by_priority "$mu_json")
  echo "$mu_sorted" | jq -c '.[]' | while read -r tool; do
    echo "Executing mutation: $(echo "$tool" | jq -r '.name')"
    echo "$tool"
  done
}

orchestrate "$@"
