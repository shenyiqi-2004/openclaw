/**
 * Shared types and utilities for orchestration tools.
 */

import { Type } from "@sinclair/typebox";

/** Input: a single tool invocation request. */
export const ToolInvocationSchema = Type.Object({
  name: Type.String({ description: "Tool name" }),
  params: Type.Record(Type.String(), Type.Unknown(), { description: "Tool parameters" }),
});

/** Strategy for orchestrating multiple tool calls. */
export const OrchestrationStrategySchema = Type.Union([
  Type.Literal("auto"),
  Type.Literal("parallel"),
  Type.Literal("serial"),
], { description: "Scheduling strategy: auto (read-only parallel, mutation serial), parallel (all concurrent), serial (all sequential)" });

/** Input schema for orchestrate_tools. */
export const OrchestrateToolsInputSchema = Type.Object({
  tools: Type.Array(ToolInvocationSchema, { description: "List of tool invocations to schedule" }),
  strategy: Type.Optional(OrchestrationStrategySchema),
});

/** Input schema for tool_classify. */
export const ToolClassifyInputSchema = Type.Object({
  tool_name: Type.String({ description: "Name of the tool to classify" }),
});

/** Input schema for execution_stats. */
export const ExecutionStatsInputSchema = Type.Object({
  session_key: Type.Optional(Type.String({ description: "Optional session key (reserved for future use)" })),
});

/** A group of tools scheduled to run concurrently. */
export interface ScheduleGroup {
  group: number;
  concurrent: boolean;
  tools: string[];
}

/** The orchestration plan returned by orchestrate_tools. */
export interface OrchestrationPlan {
  plan: ScheduleGroup[];
  stats: {
    total: number;
    concurrent_groups: number;
    serial_steps: number;
  };
}

/** Classification result returned by tool_classify. */
export interface ClassificationResult {
  category: "read_only" | "mutation" | "unknown";
  safe_concurrent: boolean;
  max_concurrent: number;
  timeout_ms: number;
  retry_allowed: boolean;
}

/** Execution statistics for the current session. */
export interface ExecutionStatsResult {
  total_calls: number;
  by_tool: Record<string, number>;
  errors: number;
  avg_duration_ms: number;
}

/** Tool execution record for tracking stats. */
export interface ExecutionRecord {
  tool_name: string;
  started_at: number;
  duration_ms: number;
  error: boolean;
}
