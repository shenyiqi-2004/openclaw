import fs from "node:fs";
import path from "node:path";
import JSON5 from "json5";
import { resolveConfigPathCandidate } from "../config/config.js";
import {
  queueExternalMemoryKernelRun,
  type QueueExternalMemoryKernelRunParams,
} from "./external-memory-kernel.js";
import { describeExternalMemoryRoot } from "./external-memory-root.js";
import { describeOpenClawRuntimeLayout } from "./openclaw-runtime-layout.js";

export type MemoryInteractionBoundary = {
  requestBoundary: "durable-event-emit";
  backgroundBoundary: "sidecar-worker";
  canonicalBackend: string;
  fallbackBackend: "json_snapshot";
  bridgePath: string;
  bridgeAvailable: boolean;
  runtimeRoot: string;
  externalMemoryRoot: string;
  externalMemorySource: string;
  externalMemoryDeprecated: boolean;
  configPath: string;
};

function readConfiguredMemoryBackend(configPath: string): string {
  try {
    const raw = fs.readFileSync(configPath, "utf8");
    const parsed = JSON5.parse(raw);
    const slot = parsed.plugins?.slots?.memory;
    if (typeof slot !== "string" || !slot.trim()) {
      return "unconfigured";
    }
    const entry = parsed.plugins?.entries?.[slot];
    if (entry && entry.enabled === false) {
      return `${slot}:disabled`;
    }
    return slot;
  } catch {
    return "unknown";
  }
}

export function describeMemoryInteractionBoundary(
  env: NodeJS.ProcessEnv = process.env,
): MemoryInteractionBoundary {
  const root = describeExternalMemoryRoot(env);
  const runtime = describeOpenClawRuntimeLayout(env);
  const configPath = resolveConfigPathCandidate(env);
  const bridgePath = path.join(runtime.runtimeRoot, "src", "infra", "memory-lancedb-pro-bridge.ts");
  return {
    requestBoundary: "durable-event-emit",
    backgroundBoundary: "sidecar-worker",
    canonicalBackend: readConfiguredMemoryBackend(configPath),
    fallbackBackend: "json_snapshot",
    bridgePath,
    bridgeAvailable: fs.existsSync(bridgePath),
    runtimeRoot: runtime.runtimeRoot,
    externalMemoryRoot: root.memoryRoot,
    externalMemorySource: root.source,
    externalMemoryDeprecated: root.deprecated,
    configPath,
  };
}

export function emitExternalMemoryInteraction(params: QueueExternalMemoryKernelRunParams): boolean {
  return queueExternalMemoryKernelRun(params);
}
