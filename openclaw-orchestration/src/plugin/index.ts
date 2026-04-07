/**
 * openclaw-orchestration — Tool concurrency orchestration + execution hooks.
 *
 * Provides three tools:
 *  1. orchestrate_tools  — build a safe scheduling plan for a list of tool calls
 *  2. tool_classify      — return safety/concurrency attributes of a named tool
 *  3. execution_stats    — return in-memory execution statistics for the session
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { createExecutionStatsTool } from "../tools/execution-stats.js";
import { createOrchestrateToolsTool } from "../tools/orchestrate-tools.js";
import { createToolClassifyTool } from "../tools/tool-classify.js";

const orchestrationPlugin = {
  id: "openclaw-orchestration",
  name: "OpenClaw Orchestration",
  description:
    "Tool concurrency orchestration + execution hooks. " +
    "Classifies tools as read-only or mutation, builds safe scheduling plans, " +
    "and tracks execution statistics.",

  register(api: OpenClawPluginApi): void {
    const cfg = (api.pluginConfig ?? {}) as Record<string, unknown>;
    const enabled = typeof cfg.enabled === "boolean" ? cfg.enabled : true;
    const maxParallelReadOnly =
      typeof cfg.maxParallelReadOnly === "number"
        ? Math.max(1, Math.min(50, cfg.maxParallelReadOnly))
        : 10;
    api.logger.info(
      `[orchestration] Plugin loaded (enabled=${enabled}, maxParallelReadOnly=${maxParallelReadOnly})`,
    );

    // Register tools
    api.registerTool((ctx) =>
      createOrchestrateToolsTool(api),
    );
    api.registerTool((ctx) =>
      createToolClassifyTool(api),
    );
    api.registerTool((ctx) =>
      createExecutionStatsTool(api),
    );
  },
};

export default orchestrationPlugin;
