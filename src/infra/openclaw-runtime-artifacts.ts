import fs from "node:fs";
import path from "node:path";
import {
  resolveConfigPathCandidate,
  resolveGatewayLockDir,
  resolveStateDir,
} from "../config/config.js";
import { readLoggingConfig } from "../logging/config.js";
import { DEFAULT_LOG_FILE } from "../logging/logger.js";
import { resolveControlUiDistIndexPathForRoot } from "./control-ui-assets.js";
import { describeMemoryInteractionBoundary } from "./memory-interaction.js";
import { describeOpenClawRuntimeLayout } from "./openclaw-runtime-layout.js";
import { resolvePreferredOpenClawTmpDir } from "./tmp-openclaw-dir.js";

export type OpenClawRuntimeArtifacts = {
  entry: {
    cli: string;
    main: string;
    packageRoot: string;
  };
  build: {
    distDir: string;
    mainExists: boolean;
    controlUiIndex: string;
    controlUiExists: boolean;
  };
  paths: {
    stateDir: string;
    configPath: string;
    logsDir: string;
    logFile: string;
    cacheDir: string;
    tmpDir: string;
    gatewayLockDir: string;
    runtimeRoot: string;
    externalMemoryRoot: string;
    externalMemoryStateDir: string;
    externalMemoryTracePath: string;
    externalMemoryAckPath: string;
    externalMemoryRuntimePath: string;
  };
  memory: {
    canonicalBackend: string;
    fallbackBackend: string;
    requestBoundary: string;
    backgroundBoundary: string;
    bridgePath: string;
    bridgeAvailable: boolean;
  };
};

export function describeOpenClawRuntimeArtifacts(
  env: NodeJS.ProcessEnv = process.env,
): OpenClawRuntimeArtifacts {
  const layout = describeOpenClawRuntimeLayout(env);
  const memory = describeMemoryInteractionBoundary(env);
  const stateDir = resolveStateDir(env);
  const configPath = resolveConfigPathCandidate(env);
  const distDir = path.join(layout.packageRoot, "dist");
  const mainPath = path.join(layout.packageRoot, "openclaw.mjs");
  const controlUiIndex = resolveControlUiDistIndexPathForRoot(layout.packageRoot);
  const loggingCfg = readLoggingConfig();
  const logFile = loggingCfg?.file?.trim() || DEFAULT_LOG_FILE;
  const logsDir = path.join(stateDir, "logs");
  const cacheDir = path.join(stateDir, "cache");
  const tmpDir = resolvePreferredOpenClawTmpDir();
  const gatewayLockDir = resolveGatewayLockDir();
  const externalMemoryStateDir = path.join(memory.externalMemoryRoot, "memory");

  return {
    entry: {
      cli: mainPath,
      main: path.join(distDir, "index.js"),
      packageRoot: layout.packageRoot,
    },
    build: {
      distDir,
      mainExists: fs.existsSync(path.join(distDir, "index.js")),
      controlUiIndex,
      controlUiExists: fs.existsSync(controlUiIndex),
    },
    paths: {
      stateDir,
      configPath,
      logsDir,
      logFile,
      cacheDir,
      tmpDir,
      gatewayLockDir,
      runtimeRoot: layout.runtimeRoot,
      externalMemoryRoot: memory.externalMemoryRoot,
      externalMemoryStateDir,
      externalMemoryTracePath: path.join(externalMemoryStateDir, "traces.jsonl"),
      externalMemoryAckPath: path.join(externalMemoryStateDir, "acks.jsonl"),
      externalMemoryRuntimePath: path.join(externalMemoryStateDir, "runtime.json"),
    },
    memory: {
      canonicalBackend: memory.canonicalBackend,
      fallbackBackend: memory.fallbackBackend,
      requestBoundary: memory.requestBoundary,
      backgroundBoundary: memory.backgroundBoundary,
      bridgePath: memory.bridgePath,
      bridgeAvailable: memory.bridgeAvailable,
    },
  };
}
