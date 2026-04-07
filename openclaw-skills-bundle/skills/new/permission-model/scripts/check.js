/**
 * Permission Three-Layer Model — Reference Implementation
 *
 * Usage:
 *   node check.js <operation> <target>
 *   node check.js write /tmp/test.txt
 *   node check.js execute /home/user/script.sh
 */

const WHITELIST = [
  { path: '/home/park/.openclaw/workspace/**', operation: ['read', 'write', 'delete', 'execute'] },
  { path: '/tmp/**', operation: ['read', 'write'] },
  { path: '/mnt/c/Users/w/Desktop/wsl共享/**', operation: ['read', 'write', 'delete'] },
];

const BLACKLIST = [
  { path: '/etc/shadow', operation: ['read', 'write', 'delete'] },
  { path: '/etc/passwd', operation: ['write', 'delete'] },
  { path: '/home/park/.ssh/**', operation: ['write', 'delete', 'execute'] },
  { path: '/root/**', operation: ['read', 'write', 'delete', 'execute'] },
  { path: '/sys/**', operation: ['read', 'write'] },
  { path: '/proc/sys/**', operation: ['read', 'write'] },
];

const TRUSTED_PARENTS = [
  '/home/park/.openclaw/workspace',
  '/tmp',
  '/mnt/c/Users/w/Desktop/wsl共享',
];

const DANGEROUS_EXTENSIONS = {
  '.sh': 20, '.bash': 20, '.zsh': 20,
  '.py': 15, '.js': 10, '.exe': 30, '.dll': 30,
  '.ps1': 25, '.bat': 25, '.cmd': 25,
};

const OPERATION_SCORES = {
  read: 0,
  write: 15,
  delete: 25,
  execute: 30,
  network: 30,
};

const SCORE_THRESHOLDS = { warn: 41, deny: 71 };

// ── Layer 1: Exact Match ────────────────────────────────────────────────────

function layer1_match(operation, target) {
  for (const rule of BLACKLIST) {
    if (matchPath(rule.path, target) && rule.operation.includes(operation)) {
      return { allowed: false, layer: 1, reason: `blacklist match: ${rule.path}` };
    }
  }
  for (const rule of WHITELIST) {
    if (matchPath(rule.path, target) && rule.operation.includes(operation)) {
      return { allowed: true, layer: 1, reason: `whitelist match: ${rule.path}` };
    }
  }
  return null; // no match → fall through
}

function matchPath(pattern, target) {
  if (pattern.endsWith('/**')) {
    const prefix = pattern.slice(0, -3);
    return target === prefix || target.startsWith(prefix + '/');
  }
  if (pattern.endsWith('/*')) {
    const dir = pattern.slice(0, -2);
    const parts = target.split('/');
    return parts.slice(0, -1).join('/') === dir;
  }
  return target === pattern;
}

// ── Layer 2: Semantic Intent ─────────────────────────────────────────────────

function layer2_score(operation, target) {
  let score = 0;

  // 1. path depth (deeper = more specific = more trustworthy)
  const depth = target.split('/').filter(Boolean).length;
  score += Math.min(depth * 3, 20);

  // 2. parent directory trust
  const parent = target.split('/').slice(0, -1).join('/');
  if (TRUSTED_PARENTS.some(t => parent.startsWith(t))) {
    score += 20;
  }

  // 3. file extension risk
  const ext = target.match(/\.[^./]+$/)?.[0] || '';
  score += DANGEROUS_EXTENSIONS[ext.toLowerCase()] || 5;

  // 4. operation type
  score += OPERATION_SCORES[operation] || 0;

  return Math.min(score, 100);
}

function layer2_decide(operation, target) {
  const score = layer2_score(operation, target);
  if (score < SCORE_THRESHOLDS.warn) {
    return { allowed: true, layer: 2, reason: `score=${score}`, score };
  }
  if (score < SCORE_THRESHOLDS.deny) {
    return { allowed: true, layer: 2, reason: `score=${score} (warn)`, score, warn: true };
  }
  return { allowed: false, layer: 2, reason: `score=${score} exceeds deny threshold`, score };
}

// ── Layer 3: Sandbox Isolation ───────────────────────────────────────────────

function layer3_isolation(operation, target) {
  const ext = target.match(/\.[^./]+$/)?.[0]?.toLowerCase() || '';
  const isExecutable = ['.sh', '.bash', '.py', '.js', '.ps1', '.bat', '.cmd', '.exe'].includes(ext);

  const profiles = {
    read:       { filesystem: 'read-only', network: 'none', process: 'none', memory: null },
    write:      { filesystem: 'read-write', network: 'none', process: 'none', memory: 256 },
    delete:     { filesystem: 'read-only', network: 'none', process: 'none', memory: null },
    execute:    { filesystem: isExecutable ? 'temp' : 'read-only', network: 'localhost', process: 'spawn', memory: 512 },
    network:    { filesystem: 'none', network: 'full', process: 'none', memory: 128 },
  };

  return profiles[operation] || profiles.read;
}

// ── Main API ────────────────────────────────────────────────────────────────

function permission_check(operation, target) {
  // Layer 1
  const l1 = layer1_match(operation, target);
  if (l1 !== null) {
    log_denial({ ...l1, target, operation });
    if (l1.allowed) l1.isolation = layer3_isolation(operation, target);
    return l1;
  }

  // Layer 2
  const l2 = layer2_decide(operation, target);
  log_denial({ ...l2, target, operation });
  if (l2.allowed) l2.isolation = layer3_isolation(operation, target);
  return l2;
}

// ── Denial Tracking ─────────────────────────────────────────────────────────

const denials = [];

function log_denial(entry) {
  if (!entry.allowed) {
    denials.push({
      id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36),
      timestamp: new Date().toISOString(),
      target: entry.target,
      operation: entry.operation,
      layer: entry.layer,
      reason: entry.reason,
      score: entry.score || null,
    });
  }
}

// ── CLI ─────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const [, , operation, target] = process.argv;
  if (!operation || !target) {
    console.error('Usage: node check.js <operation> <target>\n  operation: read|write|delete|execute|network\n  target: /path/to/resource');
    process.exit(1);
  }

  const VALID_OPS = ['read', 'write', 'delete', 'execute', 'network'];
  if (!VALID_OPS.includes(operation)) {
    console.error(`Invalid operation: ${operation}. Must be one of: ${VALID_OPS.join(', ')}`);
    process.exit(1);
  }

  const result = permission_check(operation, target);
  console.log(JSON.stringify(result, null, 2));
}

module.exports = { permission_check, layer1_match, layer2_score, layer2_decide, layer3_isolation, denials };
