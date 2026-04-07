/**
 * orchestrate_tools — builds a tool scheduling plan without executing tools.
 *
 * Strategy modes:
 *  - auto:   read-only tools in parallel batches (max 10), mutations strictly serial
 *  - parallel: all tools concurrent (user explicitly asked for parallelism)
 *  - serial:  all tools sequential
 */

import { Type } from "@sinclair/typebox";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { classifyTool } from "../tool-registry.js";
import type {
  OrchestrationPlan,
  ScheduleGroup,
  ToolInvocation,
} from "./common.js";
import {
  OrchestrateToolsInputSchema,
} from "./common.js";

const DEFAULT_MAX_PARALLEL = 10;

interface PluginConfig {
  enabled?: boolean;
  maxParallelReadOnly?: number;
}

function buildAutoPlan(tools: ToolInvocation[], maxParallel: number): OrchestrationPlan {
  const groups: ScheduleGroup[] = [];
  let groupIndex = 1;

  // Partition: read-only first, then mutations interleaved
  const readOnlyBatches: ToolInvocation[][] = [];
  const mutationTools: ToolInvocation[] = [];

  for (const tool of tools) {
    const classification = classifyTool(tool.name);
    if (classification.category === "read_only") {
      // Find last batch that isn't full
      let lastBatch = readOnlyBatches[readOnlyBatches.length - 1];
      if (!lastBatch || lastBatch.length >= maxParallel) {
        lastBatch = [];
        readOnlyBatches.push(lastBatch);
      }
      lastBatch.push(tool);
    } else {
      mutationTools.push(tool);
    }
  }

  // Emit read-only batches as concurrent groups
  for (const batch of readOnlyBatches) {
    if (batch.length > 0) {
      groups.push({
        group: groupIndex++,
        concurrent: true,
        tools: batch.map((t) => t.name),
      });
    }
  }

  // Emit mutations as serial steps (one tool per group)
  for (const tool of mutationTools) {
    groups.push({
      group: groupIndex++,
      concurrent: false,
      tools: [tool.name],
    });
  }

  const concurrentGroups = groups.filter((g) => g.concurrent).length;
  const serialSteps = groups.filter((g) => !g.concurrent).length;

  return {
    plan: groups,
    stats: {
      total: tools.length,
      concurrent_groups: concurrentGroups,
      serial_steps: serialSteps,
    },
  };
}

function buildParallelPlan(tools: ToolInvocation[]): OrchestrationPlan {
  // All tools in one concurrent group
  const group: ScheduleGroup = {
    group: 1,
    concurrent: true,
    tools: tools.map((t) => t.name),
  };

  return {
    plan: [group],
    stats: {
      total: tools.length,
      concurrent_groups: 1,
      serial_steps: 0,
    },
  };
}

function buildSerialPlan(tools: ToolInvocation[]): OrchestrationPlan {
  const groups: ScheduleGroup[] = tools.map((tool, index) => ({
    group: index + 1,
    concurrent: false,
    tools: [tool.name],
  }));

  return {
    plan: groups,
    stats: {
      total: tools.length,
      concurrent_groups: 0,
      serial_steps: groups.length,
    },
  };
}

export function createOrchestrateToolsTool(api: OpenClawPluginApi) {
  const pluginConfig = (api.pluginConfig ?? {}) as PluginConfig;
  const maxParallel =
    typeof pluginConfig.maxParallelReadOnly === "number"
      ? Math.max(1, Math.min(50, pluginConfig.maxParallelReadOnly))
      : DEFAULT_MAX_PARALLEL;

  return {
    name: "orchestrate_tools",
    description:
      "Build a tool scheduling plan without executing tools. " +
      "Classifies tools as read-only or mutation, then groups them for safe concurrent execution. " +
      "Use 'auto' strategy for intelligent scheduling (read-only parallel, mutation serial), " +
      "'parallel' for all concurrent, or 'serial' for all sequential.",

    parameters: OrchestrateToolsInputSchema,

    async execute(
      _toolCallId: string,
      params: Record<string, unknown>,
    ): Promise<string> {
      const tools: ToolInvocation[] = (Array.isArray(params.tools) ? params.tools : []) as ToolInvocation[];
      const strategy: "auto" | "parallel" | "serial" = (typeof params.strategy === "string" ? params.strategy : "auto") as "auto" | "parallel" | "serial";

      if (tools.length === 0) {
        const result: OrchestrationPlan = {
          plan: [],
          stats: { total: 0, concurrent_groups: 0, serial_steps: 0 },
        };
        return JSON.stringify(result, null, 2);
      }

      let plan: OrchestrationPlan;

      switch (strategy) {
        case "parallel":
          plan = buildParallelPlan(tools);
          break;
        case "serial":
          plan = buildSerialPlan(tools);
          break;
        case "auto":
        default:
          plan = buildAutoPlan(tools, maxParallel);
          break;
      }

      return JSON.stringify(plan, null, 2);
    },
  };
}
