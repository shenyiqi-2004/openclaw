/**
 * permission-check.ts
 * Tool: Three-layer permission model for file/network operations.
 *
 * Layer 1 — Rule Match:   Exact whitelist / blacklist path matching
 * Layer 2 — Semantic:    Operation intent + risk scoring (0-100)
 * Layer 3 — Sandbox:     Isolation recommendations based on risk
 */
import { Type } from "@sinclair/typebox";
import { jsonResult, readStringParam } from "./common.js";
import { OPERATION_RISK_WEIGHTS, PATH_BLACKLIST, PATH_WHITELIST } from "../security-rules.js";

export type Operation = "read" | "write" | "delete" | "execute" | "network";

/** Result of permission check across three layers. */
export interface PermissionCheckResult {
  allowed: boolean;
  layer: string;
  reason: string;
  score: number;
  layerDetails: {
    layer1: {
      matched: boolean;
      rule?: string;
      description?: string;
    };
    layer2: {
      intent: string;
      score: number;
      classification: "safe" | "low" | "medium" | "high" | "critical";
    };
    layer3: {
      sandboxRecommended: boolean;
      suggestions: string[];
    };
  };
}

/** Classify a risk score into a severity tier. */
function classifyRisk(score: number): "safe" | "low" | "medium" | "high" | "critical" {
  if (score < 10) return "safe";
  if (score < 35) return "low";
  if (score < 60) return "medium";
  if (score < 80) return "high";
  return "critical";
}

/**
 * Perform Layer 1: direct rule matching against whitelist / blacklist.
 */
function layer1Match(operation: Operation, target: string): {
  matched: boolean;
  rule?: string;
  description?: string;
} {
  const t = target.trim();

  // Check blacklist first
  for (const { pattern, description } of PATH_BLACKLIST) {
    if (pattern.test(t)) {
      return {
        matched: true,
        rule: "blacklist",
        description: `Blocked by blacklist rule: ${description}`,
      };
    }
  }

  // Check whitelist
  for (const { pattern, description } of PATH_WHITELIST) {
    if (pattern.test(t)) {
      return {
        matched: true,
        rule: "whitelist",
        description: `Allowed by whitelist rule: ${description}`,
      };
    }
  }

  // Network operations check
  if (operation === "network") {
    // Allow localhost / loopback
    if (/^(localhost|127\.0\.0\.1|::1|\[::1\])/i.test(t)) {
      return {
        matched: true,
        rule: "whitelist",
        description: "Localhost is whitelisted",
      };
    }
    // Block obvious external exfiltration targets
    if (/\b(exfil|exfiltration|leak|dump)\b/i.test(t)) {
      return {
        matched: true,
        rule: "blacklist",
        description: "Network target name suggests exfiltration",
      };
    }
  }

  return { matched: false };
}

/**
 * Perform Layer 2: semantic intent analysis + risk scoring.
 */
function layer2Analyze(operation: Operation, target: string): {
  intent: string;
  score: number;
  classification: "safe" | "low" | "medium" | "high" | "critical";
} {
  const t = target.trim();
  let baseScore = OPERATION_RISK_WEIGHTS[operation] ?? 30;

  // Adjust score based on target characteristics
  if (/\/\.ssh\//.test(t)) baseScore += 30;
  if (/\/\.aws\//.test(t)) baseScore += 25;
  if (/\/\.env\b/.test(t)) baseScore += 20;
  if (/root|system|kernel|boot/i.test(t)) baseScore += 25;
  if (/\.pem|\.key|\.crt|\.pfx|\.jks/.test(t)) baseScore += 20;
  if (/sudo|chmod|chown|setuid/.test(t)) baseScore += 20;
  if (/\.tar|\.gz|\.zip|\.7z|\.bz2/.test(t)) baseScore += 10; // archive flags
  if (/https?:\/\/[^\/]+$/i.test(t)) baseScore += 5; // generic URL

  const cappedScore = Math.min(baseScore, 100);

  const intentMap: Record<Operation, string> = {
    read: `Reading from target: ${t}`,
    write: `Writing to target: ${t}`,
    delete: `Deleting target: ${t}`,
    execute: `Executing: ${t}`,
    network: `Network operation to: ${t}`,
  };

  return {
    intent: intentMap[operation],
    score: cappedScore,
    classification: classifyRisk(cappedScore),
  };
}

/**
 * Perform Layer 3: sandbox recommendations.
 */
function layer3Recommend(
  operation: Operation,
  layer1Result: { matched: boolean; rule?: string },
  layer2Result: { score: number; classification: string },
): {
  sandboxRecommended: boolean;
  suggestions: string[];
} {
  const suggestions: string[] = [];

  // Always sandbox network operations
  if (operation === "network") {
    suggestions.push("Run in network namespace isolation (--network=restricted)");
    suggestions.push("Limit outbound connections with firewall rules");
    suggestions.push("Consider using a read-only DNS resolver");
  }

  // Sandbox write/delete on sensitive paths
  if ((operation === "write" || operation === "delete") && layer2Result.score >= 50) {
    suggestions.push("Dry-run first with output review");
    suggestions.push("Use a temporary copy before modifying originals");
    suggestions.push("Consider read-only mount for target directory");
  }

  // Sandbox execute
  if (operation === "execute" && layer2Result.score >= 40) {
    suggestions.push("Execute inside a lightweight container or chroot");
    suggestions.push("Run with minimal Linux capabilities (setcap none)");
    suggestions.push("Use seccomp to restrict syscalls");
  }

  // Blocked by blacklist → hard sandbox
  if (layer1Result.matched && layer1Result.rule === "blacklist") {
    suggestions.unshift("Operation is on the blacklist — strongly consider denying entirely");
  }

  // High risk always gets sandbox recommendation
  if (layer2Result.classification === "high" || layer2Result.classification === "critical") {
    suggestions.unshift("High-risk operation — sandbox isolation strongly recommended");
    if (!suggestions.includes("Run inside ephemeral container/VM")) {
      suggestions.push("Run inside ephemeral container or VM");
    }
  }

  return {
    sandboxRecommended:
      layer1Result.rule === "blacklist" ||
      layer2Result.classification === "high" ||
      layer2Result.classification === "critical" ||
      suggestions.length > 0,
    suggestions,
  };
}

/** Main permission check function. */
export function runPermissionCheck(operation: Operation, target: string): PermissionCheckResult {
  const l1 = layer1Match(operation, target);
  const l2 = layer2Analyze(operation, target);
  const l3 = layer3Recommend(operation, l1, l2);

  let allowed: boolean;
  let layer: string;
  let reason: string;

  if (l1.matched && l1.rule === "blacklist") {
    allowed = false;
    layer = "Layer 1 (Blacklist)";
    reason = l1.description ?? "Target matches blacklist rule";
  } else if (l1.matched && l1.rule === "whitelist") {
    allowed = true;
    layer = "Layer 1 (Whitelist)";
    reason = l1.description ?? "Target matches whitelist rule";
  } else if (l2.classification === "critical" || l2.classification === "high") {
    allowed = false;
    layer = "Layer 2 (Risk Threshold)";
    reason = `Risk score ${l2.score} (${l2.classification}) exceeds safe threshold: ${l2.intent}`;
  } else if (l2.classification === "medium") {
    allowed = false; // medium is denied by default
    layer = "Layer 2 (Risk Threshold)";
    reason = `Medium risk score ${l2.score} — requires explicit approval: ${l2.intent}`;
  } else {
    allowed = true;
    layer = "Layer 2 (Semantic)";
    reason = `Risk score ${l2.score} (${l2.classification}) is within safe range: ${l2.intent}`;
  }

  return {
    allowed,
    layer,
    reason,
    score: l2.score,
    layerDetails: {
      layer1: { matched: l1.matched, rule: l1.rule, description: l1.description },
      layer2: { intent: l2.intent, score: l2.score, classification: l2.classification },
      layer3: { sandboxRecommended: l3.sandboxRecommended, suggestions: l3.suggestions },
    },
  };
}

/** Create the permission_check tool. */
export function createPermissionCheckTool(): AnyAgentTool {
  return {
    name: "permission_check",
    description:
      "Checks whether a given operation (read/write/delete/execute/network) on a target path or URL " +
      "should be allowed, based on a three-layer permission model: " +
      "(1) exact whitelist/blacklist path matching, " +
      "(2) semantic intent analysis with risk scoring 0-100, " +
      "(3) sandbox isolation recommendations. " +
      "Returns allowed/denied with detailed reasoning and layer-by-layer breakdown.",
    parameters: Type.Object({
      operation: Type.String({
        description:
          "The type of operation: read, write, delete, execute, or network",
        enum: ["read", "write", "delete", "execute", "network"],
      }),
      target: Type.String({
        description: "The target path, URL, or network address to check",
      }),
    }),

    async execute(toolCallId: string, params: Record<string, unknown>) {
      const operation = readStringParam(params, "operation", { required: true });
      const target = readStringParam(params, "target", { required: true });

      if (operation === undefined || target === undefined) {
        return jsonResult({ error: "Both operation and target are required" });
      }

      const validOps: Operation[] = ["read", "write", "delete", "execute", "network"];
      if (!validOps.includes(operation as Operation)) {
        return jsonResult({
          error: `Invalid operation '${operation}'. Must be one of: ${validOps.join(", ")}`,
        });
      }

      const result = runPermissionCheck(operation as Operation, target);
      return jsonResult(result);
    },
  };
}
