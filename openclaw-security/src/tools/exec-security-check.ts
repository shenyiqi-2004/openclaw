/**
 * exec-security-check.ts
 * Tool: Performs security pre-flight checks on shell commands.
 */
import { Type } from "@sinclair/typebox";
import { SECURITY_RULES, PATH_BLACKLIST, PATH_WHITELIST } from "../security-rules.js";
import { jsonResult, readStringParam } from "./common.js";

/** Result of a single rule match. */
interface RuleMatch {
  ruleId: string;
  description: string;
  layer: number;
  riskWeight: number;
  blocked: boolean;
  matchedText: string;
}

/** Full security check result. */
export interface ExecSecurityCheckResult {
  safe: boolean;
  risks: string[];
  blocked: boolean;
  reason?: string;
  score: number;
  matches: RuleMatch[];
  layerBreakdown: Record<number, { risks: string[]; score: number }>;
}

/**
 * Perform a complete security check on a command string.
 * Returns the detailed result plus a simplified safe/blocked summary.
 */
export function runSecurityCheck(command: string): ExecSecurityCheckResult {
  const normalized = command.trim();
  const matches: RuleMatch[] = [];
  const layerBreakdown: Record<number, { risks: string[]; score: number }> = {};

  for (const rule of SECURITY_RULES) {
    if (!rule.pattern.test(normalized)) continue;

    // Find the actual matched text
    const match = normalized.match(rule.pattern);
    const matchedText = match ? match[0] : rule.pattern.source;

    matches.push({
      ruleId: rule.id,
      description: rule.description,
      layer: rule.layer,
      riskWeight: rule.riskWeight,
      blocked: rule.blocked,
      matchedText,
    });

    if (!layerBreakdown[rule.layer]) {
      layerBreakdown[rule.layer] = { risks: [], score: 0 };
    }
    layerBreakdown[rule.layer].risks.push(rule.description);
    layerBreakdown[rule.layer].score += rule.riskWeight;
  }

  // Path blacklist check
  for (const { pattern, description } of PATH_BLACKLIST) {
    if (pattern.test(normalized)) {
      const match = normalized.match(pattern);
      matches.push({
        ruleId: "path-blacklist",
        description,
        layer: 2,
        riskWeight: 90,
        blocked: true,
        matchedText: match ? match[0] : pattern.source,
      });
      if (!layerBreakdown[2]) layerBreakdown[2] = { risks: [], score: 0 };
      layerBreakdown[2].risks.push(`Blacklisted path: ${description}`);
      layerBreakdown[2].score += 90;
    }
  }

  // Path whitelist bonus (no risk reduction, just informational)
  const whitelisted = PATH_WHITELIST.some(({ pattern }) => pattern.test(normalized));

  // Compute total score (capped at 100)
  const rawScore = matches.reduce((sum, m) => sum + m.riskWeight, 0);
  const score = Math.min(rawScore, 100);

  // Determine if any blocked rule matched
  const blocked = matches.some((m) => m.blocked);

  // Generate risk descriptions
  const risks = [...new Set(matches.map((m) => m.description))];

  let reason: string | undefined;
  if (blocked) {
    const blockedRules = matches.filter((m) => m.blocked);
    reason = `Blocked: ${blockedRules.map((m) => `${m.description} (layer ${m.layer})`).join("; ")}`;
  } else if (score >= 70) {
    reason = `High risk score (${score}): ${risks.join("; ")}`;
  } else if (score >= 40) {
    reason = `Medium risk score (${score}): ${risks.join("; ")}`;
  } else if (risks.length > 0) {
    reason = `Low risk flags (${score}): ${risks.join("; ")}`;
  }

  const safe = !blocked && score < 40;

  return {
    safe,
    risks,
    blocked,
    reason,
    score,
    matches,
    layerBreakdown,
  };
}

/** Create the exec_security_check tool. */
export function createExecSecurityCheckTool(): AnyAgentTool {
  return {
    name: "exec_security_check",
    description:
      "Performs security pre-flight checks on a shell command before execution. " +
      "Checks 15 security layers including command injection, path traversal, dangerous commands, " +
      "privilege escalation, network probes, fork bombs, environment variable injection, " +
      "encoding bypass, sensitive file access, signal abuse, filesystem destruction, " +
      "network exfiltration, crontab injection, container escape, and history erasure. " +
      "Returns detailed risk assessment with per-layer breakdown and overall safety verdict.",
    parameters: Type.Object({
      command: Type.String({
        description: "The shell command string to security-check",
      }),
    }),

    async execute(toolCallId: string, params: Record<string, unknown>) {
      const command = readStringParam(params, "command", { required: true });
      if (command === undefined) {
        return jsonResult({ error: "command parameter is required" });
      }

      const result = runSecurityCheck(command);
      return jsonResult(result);
    },
  };
}
