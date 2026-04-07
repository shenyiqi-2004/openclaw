#!/usr/bin/env bash
# exec-security-guide: 23层安全验证脚本参考实现
# 用法: check.sh "<command>" [args...]
# 返回: 0=通过, 1=拒绝

set -euo pipefail

COMMAND="${1:-}"
if [[ -z "$COMMAND" ]]; then
  echo "Usage: $0 <command>"
  exit 1
fi

# ============ 层1: 命令注入检测 ============
check_command_injection() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '[;&|`$()]|&&|\|\|'; then
    echo "[BLOCKED] Layer1: 命令注入检测 — 包含shell元字符"
    return 1
  fi
  return 0
}

# ============ 层2: 路径遍历检测 ============
check_path_traversal() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '\.\./|\.\.\\'; then
    echo "[BLOCKED] Layer2: 路径遍历检测 — 包含 ../ 穿越模式"
    return 1
  fi
  return 0
}

# ============ 层3: 变量注入检测 ============
check_variable_injection() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '\$\{?[a-zA-Z_][a-zA-Z0-9_]*\}?|\$\('; then
    echo "[BLOCKED] Layer3: 变量注入检测 — 包含变量或命令替换"
    return 1
  fi
  return 0
}

# ============ 层4: Globbing通配符检测 ============
check_globbing() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '\*|\?|\[.*\]'; then
    echo "[BLOCKED] Layer4: Globbing通配符检测 — 包含通配符"
    return 1
  fi
  return 0
}

# ============ 层5: 空白符注入检测 ============
check_whitespace_injection() {
  local cmd="$1"
  if echo "$cmd" | grep -qE $'\n|\r|\x00|\x1b'; then
    echo "[BLOCKED] Layer5: 空白符注入检测 — 包含换行/回车/null字节"
    return 1
  fi
  return 0
}

# ============ 层6: 编码绕过检测 ============
check_encoding_bypass() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '%[0-9a-fA-F]{2}|%25'; then
    echo "[BLOCKED] Layer6: 编码绕过检测 — 包含URL编码"
    return 1
  fi
  return 0
}

# ============ 层7: 环境变量覆盖检测 ============
check_env_override() {
  local cmd="$1"
  local dangerous_vars="PATH|LD_PRELOAD|LD_LIBRARY_PATH|IFS|BASH_ENV|HOME|USER|SHELL"
  if echo "$cmd" | grep -qE "(^export |^set )($dangerous_vars)="; then
    echo "[BLOCKED] Layer7: 环境变量覆盖检测 — 设置危险环境变量"
    return 1
  fi
  return 0
}

# ============ 层8: 敏感路径访问检测 ============
check_sensitive_paths() {
  local cmd="$1"
  local sensitive="/etc/shadow|/etc/passwd|/root|/home/.*/\.ssh|/proc/self|/sys/kernel"
  if echo "$cmd" | grep -qE "$sensitive"; then
    echo "[BLOCKED] Layer8: 敏感路径访问检测 — 访问敏感系统路径"
    return 1
  fi
  return 0
}

# ============ 层9: 符号链接追踪检测 ============
check_symlink() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '(^|/)-\w+|^/proc/self|^/proc/root'; then
    echo "[BLOCKED] Layer9: 符号链接穿越检测 — 符号链接模式"
    return 1
  fi
  return 0
}

# ============ 层10: 危险命令黑名单检测 ============
check_dangerous_commands() {
  local cmd="$1"
  local blacklist="rm\s+-rf\s+[/"]|chmod\s+-R\s+777\s+[/"]|dd\s+if=/dev/sd|dd\s+of=/dev/sd|mkfs|:\(\)\s*\{\s*:|:\|:&|curl\s+http.*\|\s*sh|wget.*\|\s*sh|chmod\s+\+s|sudo\s+-s|passwd\s+root|killall\s+-9|reboot|shutdown|init\s+0|telinit\s+0"
  if echo "$cmd" | grep -qiE "$blacklist"; then
    echo "[BLOCKED] Layer10: 危险命令黑名单检测 — 命令在黑名单中"
    return 1
  fi
  return 0
}

# ============ 层11: 特权提升检测 ============
check_privilege_escalation() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '^\s*(sudo|su)\s|chmod\s+[47][0-9][0-9][0-9]|chown\s.*:[0-9]'; then
    echo "[BLOCKED] Layer11: 特权提升检测 — 权限操作"
    return 1
  fi
  return 0
}

# ============ 层12: 网络探测检测 ============
check_network_probes() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '^\s*(curl|wget|nc|ncat|telnet|ssh|ftp)\s' && ! echo "$cmd" | grep -qE 'https?://'; then
    echo "[BLOCKED] Layer12: 网络探测检测 — 无明确URL的网络命令"
    return 1
  fi
  return 0
}

# ============ 层13: 文件系统破坏检测 ============
check_filesystem_destruction() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'rm\s+-rf|mkfs|dd\s+of=|>?\s*/dev/sd|>?\s*/dev/nvme'; then
    echo "[BLOCKED] Layer13: 文件系统破坏检测 — 破坏性操作"
    return 1
  fi
  return 0
}

# ============ 层14: 进程/信号滥用检测 ============
check_process_abuse() {
  local cmd="$1"
  if echo "$cmd" | grep -qE ':\(\)\s*\{\s*:|:\|:&|killall\s+-9|pkill\s+-9'; then
    echo "[BLOCKED] Layer14: 进程滥用检测 — fork bomb或强制kill"
    return 1
  fi
  return 0
}

# ============ 层15: 计划任务注入检测 ============
check_crontab_injection() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'crontab\s|at\s\s|systemctl\s+enable|service\s+.*\s+start'; then
    echo "[BLOCKED] Layer15: 计划任务/持久化检测"
    return 1
  fi
  return 0
}

# ============ 层16: 容器逃逸检测 ============
check_container_escape() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'docker\s+run\s+.*-v\s+[/"]/:|nsenter|mount\s+--bind.*/dev/|unshare'; then
    echo "[BLOCKED] Layer16: 容器逃逸检测"
    return 1
  fi
  return 0
}

# ============ 层17: Tty交互劫持检测 ============
check_tty_hijack() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'script\s|expect\s|pty|script -p'; then
    echo "[BLOCKED] Layer17: Tty交互劫持检测"
    return 1
  fi
  return 0
}

# ============ 层18: 历史记录篡改检测 ============
check_history_manipulation() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'history\s+-c|HISTSIZE=0|rm\s+.*bash_history'; then
    echo "[BLOCKED] Layer18: 历史记录篡改检测"
    return 1
  fi
  return 0
}

# ============ 层19: SSH密钥注入检测 ============
check_ssh_injection() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '\.ssh/authorized_keys|\.ssh/known_hosts|ssh-keygen'; then
    echo "[BLOCKED] Layer19: SSH密钥注入检测"
    return 1
  fi
  return 0
}

# ============ 层20: Sudo配置篡改检测 ============
check_sudoers_tampering() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '/etc/sudoers|visudo'; then
    echo "[BLOCKED] Layer20: Sudoers配置篡改检测"
    return 1
  fi
  return 0
}

# ============ 层21: NTFS ADS检测 ============
check_ntfs_ads() {
  local cmd="$1"
  if echo "$cmd" | grep -qE ':[^/\\:*?"<>|\$]+DATA|:stream|:zone\.identifier'; then
    echo "[BLOCKED] Layer21: NTFS ADS检测 — 备用数据流"
    return 1
  fi
  return 0
}

# ============ 层22: NTFS 8.3短文件名检测 ============
check_ntfs_83() {
  local cmd="$1"
  if echo "$cmd" | grep -qE '~[0-9]|PROGRA~[0-9]|DOCUME~[0-9]|SYSVOL~[0-9]|CONFIG~[0-9]'; then
    echo "[BLOCKED] Layer22: NTFS 8.3短文件名检测"
    return 1
  fi
  return 0
}

# ============ 层23: sed -i 路径遍历防护 ============
check_sed_i_path() {
  local cmd="$1"
  if echo "$cmd" | grep -qE 'sed\s+-i.*\.\./'; then
    echo "[BLOCKED] Layer23: sed -i 路径遍历防护"
    return 1
  fi
  if echo "$cmd" | grep -qE 'sed\s+-i.*(/etc/passwd|/etc/shadow|/etc/sudoers)'; then
    echo "[BLOCKED] Layer23: sed -i 危险目标文件"
    return 1
  fi
  return 0
}

# ============ 主流程 ============
run_all_checks() {
  local layers=(
    check_command_injection
    check_path_traversal
    check_variable_injection
    check_globbing
    check_whitespace_injection
    check_encoding_bypass
    check_env_override
    check_sensitive_paths
    check_symlink
    check_dangerous_commands
    check_privilege_escalation
    check_network_probes
    check_filesystem_destruction
    check_process_abuse
    check_crontab_injection
    check_container_escape
    check_tty_hijack
    check_history_manipulation
    check_ssh_injection
    check_sudoers_tampering
    check_ntfs_ads
    check_ntfs_83
    check_sed_i_path
  )

  for layer in "${layers[@]}"; do
    if ! "$layer" "$COMMAND"; then
      echo "[FAIL] 验证未通过，命令被拒绝。"
      exit 1
    fi
  done

  echo "[PASS] 23层验证全部通过。"
  exit 0
}

run_all_checks
