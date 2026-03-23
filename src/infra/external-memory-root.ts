const DEFAULT_RUNTIME_ROOT = "/home/park/openclaw";
const DEFAULT_MEMORY_ROOT = `${DEFAULT_RUNTIME_ROOT}/memory-sidecar`;
const DEPRECATED_MEMORY_ROOTS = new Set(["/mnt/d/openclaw", "D:\\openclaw"]);

export type ExternalMemoryRootResolution = {
  runtimeRoot: string;
  memoryRoot: string;
  source: "env:OPENCLAW_EXTERNAL_MEMORY_ROOT" | "env:OPENCLAW_RUNTIME_ROOT" | "default";
  deprecated: boolean;
};

export function resolveConfiguredRuntimeRoot(): string {
  return process.env.OPENCLAW_RUNTIME_ROOT?.trim() || DEFAULT_RUNTIME_ROOT;
}

export function resolveConfiguredExternalMemoryRoot(): ExternalMemoryRootResolution {
  const configuredMemoryRoot = process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT?.trim();
  if (configuredMemoryRoot) {
    return {
      runtimeRoot: resolveConfiguredRuntimeRoot(),
      memoryRoot: configuredMemoryRoot,
      source: "env:OPENCLAW_EXTERNAL_MEMORY_ROOT",
      deprecated: DEPRECATED_MEMORY_ROOTS.has(configuredMemoryRoot),
    };
  }
  const runtimeRoot = resolveConfiguredRuntimeRoot();
  if (process.env.OPENCLAW_RUNTIME_ROOT?.trim()) {
    return {
      runtimeRoot,
      memoryRoot: `${runtimeRoot}/memory-sidecar`,
      source: "env:OPENCLAW_RUNTIME_ROOT",
      deprecated: false,
    };
  }
  return {
    runtimeRoot,
    memoryRoot: DEFAULT_MEMORY_ROOT,
    source: "default",
    deprecated: false,
  };
}

export function describeExternalMemoryRoot(): ExternalMemoryRootResolution {
  return resolveConfiguredExternalMemoryRoot();
}
