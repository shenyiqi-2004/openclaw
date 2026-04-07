import { getDb, isJsonMode } from "../db/connection.js";
import {
  toolStatsSummarySchema,
  buildTool,
} from "./common.js";

interface ToolStatsSummaryParams {
  tool_name?: string;
  last_hours?: number;
}

interface ToolStatRow {
  tool_name: string;
  duration_ms: number;
  success: number;
  error_message: string | null;
}

interface SummaryResult {
  total: number;
  success_rate: number;
  avg_duration_ms: number;
  by_tool: Record<string, { count: number; success_rate: number; avg_ms: number }>;
}

export const toolStatsSummaryTool = buildTool({
  name: "tool_stats_summary",
  description: "Summarize tool execution statistics over a time window",
  parameters: toolStatsSummarySchema,
  execute: async (params: Record<string, unknown>) => {
    const db = getDb();
    const lastHours = params.last_hours ?? 24;
    const cutoff = new Date(Date.now() - lastHours * 3600 * 1000).toISOString();

    if (isJsonMode()) {
      const rows = (db as unknown as { all: (sql: string) => unknown[] }).all(
        `SELECT * FROM tool_stats WHERE created_at >= '${cutoff}'`
      ) as ToolStatRow[];

      const filtered = params.tool_name
        ? rows.filter((r) => r.tool_name === params.tool_name)
        : rows;

      return computeSummary(filtered);
    }

    let sql = `
      SELECT tool_name, duration_ms, success, error_message
      FROM tool_stats
      WHERE created_at >= ?
    `;
    const queryParams: unknown[] = [cutoff];

    if (params.tool_name) {
      sql += ` AND tool_name = ?`;
      queryParams.push(params.tool_name);
    }

    const rows = db.all<ToolStatRow>(sql, queryParams);
    return computeSummary(rows);
  },
});

function computeSummary(rows: ToolStatRow[]): SummaryResult {
  if (rows.length === 0) {
    return { total: 0, success_rate: 0, avg_duration_ms: 0, by_tool: {} };
  }

  const total = rows.length;
  const totalSuccess = rows.filter((r) => r.success === 1 || r.success === true).length;
  const success_rate = Math.round((totalSuccess / total) * 1000) / 1000;
  const totalDuration = rows.reduce((sum, r) => sum + (r.duration_ms ?? 0), 0);
  const avg_duration_ms = Math.round(totalDuration / total);

  const byTool: Record<string, { count: number; success_sum: number; total_duration: number }> = {};
  for (const row of rows) {
    if (!byTool[row.tool_name]) {
      byTool[row.tool_name] = { count: 0, success_sum: 0, total_duration: 0 };
    }
    byTool[row.tool_name].count++;
    byTool[row.tool_name].success_sum += row.success === 1 || row.success === true ? 1 : 0;
    byTool[row.tool_name].total_duration += row.duration_ms ?? 0;
  }

  const by_tool: Record<string, { count: number; success_rate: number; avg_ms: number }> = {};
  for (const [name, data] of Object.entries(byTool)) {
    by_tool[name] = {
      count: data.count,
      success_rate: Math.round((data.success_sum / data.count) * 1000) / 1000,
      avg_ms: Math.round(data.total_duration / data.count),
    };
  }

  return { total, success_rate, avg_duration_ms, by_tool };
}
