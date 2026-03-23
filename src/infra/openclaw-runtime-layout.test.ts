import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { describeOpenClawRuntimeLayout } from "./openclaw-runtime-layout.js";

describe("describeOpenClawRuntimeLayout", () => {
  const previousRuntimeRoot = process.env.OPENCLAW_RUNTIME_ROOT;
  const previousMemoryRoot = process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;

  afterEach(() => {
    if (previousRuntimeRoot === undefined) {
      delete process.env.OPENCLAW_RUNTIME_ROOT;
    } else {
      process.env.OPENCLAW_RUNTIME_ROOT = previousRuntimeRoot;
    }
    if (previousMemoryRoot === undefined) {
      delete process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;
    } else {
      process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT = previousMemoryRoot;
    }
  });

  it("describes canonical runtime and external memory roots", () => {
    delete process.env.OPENCLAW_RUNTIME_ROOT;
    delete process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT;
    const layout = describeOpenClawRuntimeLayout();
    expect(layout.runtimeRoot).toBe("/home/park/openclaw");
    expect(layout.externalMemoryRoot).toBe("/home/park/openclaw/memory-sidecar");
    expect(layout.externalMemorySource).toBe("default");
    expect(layout.stateDir).toMatch(/\.openclaw$/);
    expect(layout.gatewayLockDir).toBe(
      path.join(os.tmpdir(), `openclaw-${process.getuid?.() ?? ""}`.replace(/-$/, "")),
    );
  });

  it("prefers explicit external memory root", () => {
    process.env.OPENCLAW_RUNTIME_ROOT = "/runtime/root";
    process.env.OPENCLAW_EXTERNAL_MEMORY_ROOT = "/runtime/custom-memory";
    const layout = describeOpenClawRuntimeLayout();
    expect(layout.runtimeRoot).toBe("/runtime/root");
    expect(layout.externalMemoryRoot).toBe("/runtime/custom-memory");
    expect(layout.externalMemorySource).toBe("env:OPENCLAW_EXTERNAL_MEMORY_ROOT");
  });
});
