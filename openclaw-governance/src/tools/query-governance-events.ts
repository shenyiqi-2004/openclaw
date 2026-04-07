import { getDb, isJsonMode } from "../db/connection.js";
import {
  queryGovernanceEventsSchema,
  buildTool,
} from "./common.js";

interface QueryGovernanceEventsParams {
  limit?: number;
  event_type?: "tool_blocked" | "permission_denied" | "secret_detected" | "policy_violation";
  severity?: "info" | "warning" | "critical";
  unresolved_only?: boolean;
}

export const queryGovernanceEventsTool = buildTool({
  name: "query_governance_events",
  description: "Query governance events from the governance log",
  parameters: queryGovernanceEventsSchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();
    const limit = params.limit ?? 20;

    if (isJsonMode()) {
      let rows = (db as unknown as { all: (sql: string) => unknown[] }).all(
        `SELECT * FROM governance_events LIMIT ${limit}`
      ) as Array<Record<string, unknown>>;

      if (params.event_type) {
        rows = rows.filter((r) => r.event_type === params.event_type);
      }
      if (params.severity) {
        rows = rows.filter((r) => r.severity === params.severity);
      }
      if (params.unresolved_only) {
        rows = rows.filter((r) => !r.resolved_at);
      }
      return rows.map((r) => ({
        ...r,
        payload: r.payload ? JSON.parse(r.payload as string) : null,
      }));
    }

    let sql = "SELECT * FROM governance_events";
    const queryParams: unknown[] = [];
    const conditions: string[] = [];

    if (params.event_type) {
      conditions.push(`event_type = ?`);
      queryParams.push(params.event_type);
    }
    if (params.severity) {
      conditions.push(`severity = ?`);
      queryParams.push(params.severity);
    }
    if (params.unresolved_only) {
      conditions.push(`resolved_at IS NULL`);
    }

    if (conditions.length > 0) {
      sql += ` WHERE ${conditions.join(" AND ")}`;
    }
    sql += ` ORDER BY id DESC LIMIT ?`;
    queryParams.push(limit);

    const rows = db.all<Record<string, unknown>>(sql, queryParams);
    return rows.map((r) => ({
      ...r,
      payload: r.payload ? JSON.parse(r.payload as string) : null,
    }));
  },
});
