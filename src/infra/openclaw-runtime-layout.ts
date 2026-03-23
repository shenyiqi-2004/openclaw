import { resolveConfigPath, resolveGatewayLockDir, resolveStateDir } from "../config/paths.js";
import { describeExternalMemoryRoot } from "./external-memory-root.js";
import { resolveOpenClawPackageRootSync } from "./openclaw-root.js";
import { resolvePreferredOpenClawTmpDir } from "./tmp-openclaw-dir.js";

export type OpenClawRuntimeLayout = {
  packageRoot: string | null;
  stateDir: string;
  configPath: string;
  gatewayLockDir: string;
  tempDir: string;
  runtimeRoot: string;
  externalMemoryRoot: string;
  externalMemorySource: string;
  externalMemoryDeprecated: boolean;
};

export function describeOpenClawRuntimeLayout(
  env: NodeJS.ProcessEnv = process.env,
): OpenClawRuntimeLayout {
  const stateDir = resolveStateDir(env);
  const configPath = resolveConfigPath(env, stateDir);
  const memory = describeExternalMemoryRoot();
  return {
    packageRoot: resolveOpenClawPackageRootSync({
      cwd: process.cwd(),
      argv1: process.argv[1],
      moduleUrl: import.meta.url,
    }),
    stateDir,
    configPath,
    gatewayLockDir: resolveGatewayLockDir(),
    tempDir: resolvePreferredOpenClawTmpDir(),
    runtimeRoot: memory.runtimeRoot,
    externalMemoryRoot: memory.memoryRoot,
    externalMemorySource: memory.source,
    externalMemoryDeprecated: memory.deprecated,
  };
}
