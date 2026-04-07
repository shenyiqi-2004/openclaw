/**
 * execution_stats — in-memory tool execution statistics for the current plugin session.
 *
 * Statistics are NOT persisted across plugin restarts.
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import type { ExecutionRecord, ExecutionStatsResult } from "./common.js";
import { ExecutionStatsInputSchema } from "./common.js";

/**
 * Module-level store for execution records.
 * Key: session key (or "default" if none)
 */
const _statsStore = new Map<string, ExecutionRecord[]>();

/**
 * Get the stats array for a session, creating if absent.
 * Prefix underscore to avoid TS collision with any future `stats` field.
 */
function getSessionRecords(sessionKey: string): ExecutionRecord[] {
  let records = _statsStore.get(sessionKey);
  if (!records) {
    records = [];
    _statsStore.set(sessionKey, records);
  }
  return records;
}

/**
 * Record a tool execution (call this from a hook or wrapper around tool calls).
 * Exported so other parts of the plugin can register calls.
 */
export function recordExecution(params: {
  sessionKey: string;
  tool_name: string;
  started_at: number;
  duration_ms: number;
  error: boolean;
}): void {
  getSessionRecords(params.sessionKey).push({
    tool_name: params.tool_name,
    started_at: params.started_at,
    duration_ms: params.duration_ms,
    error: params.error,
  });
}

/**
 * Clear stats for a session (useful for testing).
 */
export function clearStats(sessionKey: string): void {
  _statsStore.delete(sessionKey);
}

/**
 * Build the stats result object for a session.
 */
export function buildStatsResult(sessionKey: string): ExecutionStatsResult {
  const records = getSessionRecords(sessionKey);
  const total_calls = records.length;
  const errors = records.filter((r) => r.error).length;

  const by_tool: Record<string, number> = {};
  let totalDuration = 0;

  for (const record of records) {
    by_tool[record.tool_name] = (by_tool[record.tool_name] ?? 0) + 1;
    totalDuration += record.duration_ms;
  }

  const avg_duration_ms =
    total_calls > 0 ? Math.round(totalDuration / total_calls) : 0;

  return { total_calls, by_tool, errors, avg_duration_ms };
}

export function createExecutionStatsTool(_api: OpenClawPluginApi) {
  return {
    name: "execution_stats",
    description:
      "Return in-memory tool execution statistics for the current session. " +
      "Includes total calls, per-tool call counts, error count, and average duration. " +
      "Statistics are not persisted across plugin restarts and reset on each load.",

    parameters: ExecutionStatsInputSchema,

    async execute(
      _toolCallId: string,
      params: Record<string, unknown>,
    ): Promise<string> {
      // session_key param is accepted but ignored (reserved for future multi-session support)

      const sessionKey = (typeof params.session_key === "string" ? params.session_key : undefined) ?? "default";
      const result = buildStatsResult(sessionKey);
      return JSON.stringify(result, null, 2);
    },
  };
}
