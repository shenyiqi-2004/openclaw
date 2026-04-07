import { getDb, jsonInsert, isJsonMode } from "../db/connection.js";
import {
  governanceEventSchema,
  buildTool,
} from "./common.js";

interface LogGovernanceEventParams {
  event_type: "tool_blocked" | "permission_denied" | "secret_detected" | "policy_violation";
  payload?: string;
  severity?: "info" | "warning" | "critical";
}

export const logGovernanceEventTool = buildTool({
  name: "log_governance_event",
  description: "Record a governance event (tool_blocked, permission_denied, secret_detected, policy_violation)",
  parameters: governanceEventSchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();
    const severity = params.severity ?? "info";

    if (isJsonMode()) {
      const now = new Date().toISOString();
      const row = {
        event_type: params.event_type,
        payload: params.payload ?? null,
        severity,
        resolved_at: null,
        created_at: now,
        session_key: null,
      };
      const id = jsonInsert("governance_events", row);
      return { id, event_type: params.event_type, severity, created_at: now };
    }

    const stmt = db.prepare(`
      INSERT INTO governance_events (event_type, payload, severity, session_key)
      VALUES (?, ?, ?, ?)
    `);
    const result = stmt.run(
      params.event_type,
      params.payload ?? null,
      severity,
      null
    );
    const row = db.get<{ id: number; event_type: string; severity: string; created_at: string }>(
      "SELECT id, event_type, severity, created_at FROM governance_events WHERE id = ?",
      [result.id ?? result]
    );
    return row;
  },
});
