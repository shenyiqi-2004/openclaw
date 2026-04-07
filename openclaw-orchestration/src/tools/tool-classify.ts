/**
 * tool_classify — return the safety and concurrency classification of a named tool.
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { classifyTool } from "../tool-registry.js";
import type { ClassificationResult } from "./common.js";
import { ToolClassifyInputSchema } from "./common.js";

export function createToolClassifyTool(_api: OpenClawPluginApi) {
  return {
    name: "tool_classify",
    description:
      "Return the safety and concurrency classification for a given tool name. " +
      "Indicates whether a tool is read-only (safe to parallelize), a mutation " +
      "(must run serially), or unknown. Also returns concurrency limits, timeout, " +
      "and retry policy.",

    parameters: ToolClassifyInputSchema,

    async execute(
      _toolCallId: string,
      params: Record<string, unknown>,
    ): Promise<string> {
      const toolName = (typeof params.tool_name === "string" ? params.tool_name : "").trim();

      if (!toolName) {
        const result: ClassificationResult = {
          category: "unknown",
          safe_concurrent: false,
          max_concurrent: 1,
          timeout_ms: 60_000,
          retry_allowed: false,
        };
        return JSON.stringify(result, null, 2);
      }

      const classification = classifyTool(toolName);
      const result: ClassificationResult = {
        category: classification.category,
        safe_concurrent: classification.safe_concurrent,
        max_concurrent: classification.max_concurrent,
        timeout_ms: classification.timeout_ms,
        retry_allowed: classification.retry_allowed,
      };

      return JSON.stringify(result, null, 2);
    },
  };
}
