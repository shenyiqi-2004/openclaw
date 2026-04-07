import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { getDb } from "../db/connection.js";
import { initSchema } from "../db/schema.js";
import { logDecisionTool } from "../tools/log-decision.js";
import { logGovernanceEventTool } from "../tools/log-governance-event.js";
import { queryDecisionsTool } from "../tools/query-decisions.js";
import { queryGovernanceEventsTool } from "../tools/query-governance-events.js";
import { logToolStatTool } from "../tools/log-tool-stat.js";
import { toolStatsSummaryTool } from "../tools/tool-stats-summary.js";

const plugin = {
  id: "openclaw-governance",
  name: "OpenClaw Governance",
  description:
    "SQLite governance log + decision tracking + session stats",
  register(api: OpenClawPluginApi) {
    // Initialize database schema
    const db = getDb();
    initSchema(db);

    // Register tools
    api.registerTool(logDecisionTool);
    api.registerTool(logGovernanceEventTool);
    api.registerTool(queryDecisionsTool);
    api.registerTool(queryGovernanceEventsTool);
    api.registerTool(logToolStatTool);
    api.registerTool(toolStatsSummaryTool);
  },
};

export default plugin;
