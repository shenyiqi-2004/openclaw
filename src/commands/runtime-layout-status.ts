import { describeOpenClawRuntimeArtifacts } from "../infra/openclaw-runtime-artifacts.js";
import type { RuntimeEnv } from "../runtime.js";

function renderRuntimeLayoutLines(
  summary: ReturnType<typeof describeOpenClawRuntimeArtifacts>,
): string[] {
  return [
    "OpenClaw Runtime Layout",
    `CLI entry: ${summary.entry.cli}`,
    `Main entry: ${summary.entry.main}`,
    `Package root: ${summary.entry.packageRoot}`,
    `Dist dir: ${summary.build.distDir}`,
    `Control UI: ${summary.build.controlUiIndex}`,
    `State dir: ${summary.paths.stateDir}`,
    `Config path: ${summary.paths.configPath}`,
    `Logs dir: ${summary.paths.logsDir}`,
    `Log file: ${summary.paths.logFile}`,
    `Cache dir: ${summary.paths.cacheDir}`,
    `Temp dir: ${summary.paths.tmpDir}`,
    `Gateway lock dir: ${summary.paths.gatewayLockDir}`,
    `Runtime root: ${summary.paths.runtimeRoot}`,
    `External memory root: ${summary.paths.externalMemoryRoot}`,
    `External memory trace: ${summary.paths.externalMemoryTracePath}`,
    `External memory ack: ${summary.paths.externalMemoryAckPath}`,
    `External memory runtime: ${summary.paths.externalMemoryRuntimePath}`,
    `Memory backend: ${summary.memory.canonicalBackend} (fallback: ${summary.memory.fallbackBackend})`,
    `Memory request boundary: ${summary.memory.requestBoundary}`,
    `Memory background boundary: ${summary.memory.backgroundBoundary}`,
    `Memory bridge: ${summary.memory.bridgePath}`,
  ];
}

export async function runtimeLayoutStatusCommand(
  opts: { json?: boolean },
  runtime: RuntimeEnv,
): Promise<void> {
  const summary = describeOpenClawRuntimeArtifacts();
  if (opts.json) {
    runtime.log(JSON.stringify(summary, null, 2));
    return;
  }
  runtime.log(renderRuntimeLayoutLines(summary).join("\n"));
}
