import type { OpenClawToolDef } from "openclaw/plugin-sdk";
import { Type as T } from "@sinclair/typebox";

export const EventTypes = [
  "tool_blocked",
  "permission_denied",
  "secret_detected",
  "policy_violation",
] as const;

export const Severities = ["info", "warning", "critical"] as const;

export const decisionSchema = T.Object({
  title: T.String({ minLength: 1 }),
  rationale: T.Optional(T.String()),
  alternatives: T.Optional(T.Array(T.String())),
  supersedes_id: T.Optional(T.Number()),
  tags: T.Optional(T.Array(T.String())),
});

export const governanceEventSchema = T.Object({
  event_type: T.Union(EventTypes.map((t) => T.Literal(t))),
  payload: T.Optional(T.String()),
  severity: T.Optional(T.Union(Severities.map((s) => T.Literal(s)))),
});

export const queryDecisionsSchema = T.Object({
  limit: T.Optional(T.Number({ default: 10, minimum: 1, maximum: 200 })),
  tags: T.Optional(T.Array(T.String())),
  search: T.Optional(T.String()),
});

export const queryGovernanceEventsSchema = T.Object({
  limit: T.Optional(T.Number({ default: 20, minimum: 1, maximum: 200 })),
  event_type: T.Optional(T.Union(EventTypes.map((t) => T.Literal(t)))),
  severity: T.Optional(T.Union(Severities.map((s) => T.Literal(s)))),
  unresolved_only: T.Optional(T.Boolean()),
});

export const logToolStatSchema = T.Object({
  tool_name: T.String({ minLength: 1 }),
  duration_ms: T.Number({ minimum: 0 }),
  success: T.Boolean(),
  error_message: T.Optional(T.String()),
});

export const toolStatsSummarySchema = T.Object({
  tool_name: T.Optional(T.String()),
  last_hours: T.Optional(T.Number({ default: 24, minimum: 1 })),
});

export function buildTool(
  def: { name: string; description: string; parameters: unknown; execute: (params: Record<string, unknown>) => Promise<unknown> }
): OpenClawToolDef {
  return def as unknown as OpenClawToolDef;
}
