import { getDb, jsonInsert, isJsonMode } from "../db/connection.js";
import {
  logToolStatSchema,
  buildTool,
} from "./common.js";

interface LogToolStatParams {
  tool_name: string;
  duration_ms: number;
  success: boolean;
  error_message?: string;
}

export const logToolStatTool = buildTool({
  name: "log_tool_stat",
  description: "Record a tool execution statistic",
  parameters: logToolStatSchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();

    if (isJsonMode()) {
      const now = new Date().toISOString();
      const row = {
        tool_name: params.tool_name,
        duration_ms: params.duration_ms,
        success: params.success ? 1 : 0,
        error_message: params.error_message ?? null,
        session_key: null,
        created_at: now,
      };
      const id = jsonInsert("tool_stats", row);
      return { id };
    }

    const stmt = db.prepare(`
      INSERT INTO tool_stats (tool_name, duration_ms, success, error_message, session_key)
      VALUES (?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      params.tool_name,
      params.duration_ms,
      params.success ? 1 : 0,
      params.error_message ?? null,
      null
    );
    return { id: result.id ?? result };
  },
});
